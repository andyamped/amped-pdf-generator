#!/usr/bin/env python3
"""
AMPED PDF Generator v3.2 - Production Ready (Pure Python)
Builds professional PDFs from structured data (NO HTML conversion needed)
100% Python - NO system dependencies required
Supports white-labeling for all trades (electrical, HVAC, flooring, plumbing)
"""

from flask import Flask, request, jsonify, send_file
import logging
from datetime import datetime
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# ============================================================================
# TRADE WHITE-LABEL CONFIGURATION
# ============================================================================

TRADE_CONFIGS = {
    "electrical": {
        "name": "Electrical",
        "primary_color": colors.HexColor("#0066CC"),
        "secondary_color": colors.HexColor("#003366"),
        "accent_color": colors.HexColor("#FF9800")
    },
    "hvac": {
        "name": "HVAC",
        "primary_color": colors.HexColor("#FF6B00"),
        "secondary_color": colors.HexColor("#CC5500"),
        "accent_color": colors.HexColor("#FFB84D")
    },
    "plumbing": {
        "name": "Plumbing",
        "primary_color": colors.HexColor("#2196F3"),
        "secondary_color": colors.HexColor("#1565C0"),
        "accent_color": colors.HexColor("#64B5F6")
    },
    "flooring": {
        "name": "Flooring",
        "primary_color": colors.HexColor("#8B4513"),
        "secondary_color": colors.HexColor("#654321"),
        "accent_color": colors.HexColor("#CD853F")
    }
}

def get_trade_config(trade_type):
    """Get trade configuration, default to electrical"""
    trade = trade_type.lower() if trade_type else "electrical"
    return TRADE_CONFIGS.get(trade, TRADE_CONFIGS["electrical"])

# ============================================================================
# PDF GENERATION (Pure Python - ReportLab)
# ============================================================================

def build_pdf_from_data(data, trade_config):
    """Build PDF directly from structured data using ReportLab"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=trade_config['primary_color'],
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=trade_config['primary_color'],
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Build document content
    story = []
    
    # Title
    story.append(Paragraph(f"⚡ AMPED {trade_config['name']} Analysis", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Company & Project Info
    company = data.get('companyName', 'Company')
    project = data.get('projectName', 'Project')
    
    info_data = [
        ['Company:', company],
        ['Project:', project],
        ['Date:', datetime.now().strftime('%Y-%m-%d')],
        ['Trade Type:', trade_config['name']]
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 5*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (0, -1), trade_config['primary_color']),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # CONDUIT ROUTING SECTION
    conduit_routes = data.get('conduitRoutes', [])
    if conduit_routes:
        story.append(Paragraph("🔧 Conduit Routing Analysis", heading_style))
        
        route_headers = ['Route ID', 'From', 'To', 'Size', 'Distance (ft)', 'NEC Compliant']
        route_data = [route_headers]
        
        for route in conduit_routes:
            route_data.append([
                route.get('routeId', ''),
                route.get('from', '')[:25],  # Truncate long text
                route.get('to', '')[:25],
                route.get('size_required', ''),
                str(route.get('total_distance', '')),
                'Yes ✓' if route.get('necCompliant', True) else 'NO ⚠️'
            ])
        
        route_table = Table(route_data, colWidths=[0.8*inch, 1.8*inch, 1.8*inch, 0.8*inch, 1*inch, 1.2*inch])
        route_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), trade_config['primary_color']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(route_table)
        story.append(Spacer(1, 0.2*inch))
    
    # DEVICES SECTION
    devices = data.get('deviceCounts', data.get('devices', []))
    if devices:
        story.append(Paragraph("🔌 Devices & Fixtures", heading_style))
        
        device_headers = ['Device Type', 'Quantity', 'Unit', 'Labor Hours']
        device_data = [device_headers]
        
        total_labor = 0
        for device in devices:
            qty = device.get('quantity', device.get('qty', 0))
            labor = device.get('total_labor_hours', device.get('labor_hours', 0))
            total_labor += labor
            
            device_data.append([
                device.get('type', device.get('item', 'Unknown')),
                str(qty),
                device.get('unit', 'EA'),
                f"{labor:.1f}"
            ])
        
        # Add total row
        device_data.append(['TOTAL', '', '', f"{total_labor:.1f} hrs"])
        
        device_table = Table(device_data, colWidths=[3*inch, 1*inch, 0.8*inch, 1.5*inch])
        device_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), trade_config['secondary_color']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(device_table)
        story.append(Spacer(1, 0.2*inch))
    
    # CONDUIT SUMMARY (if different from routes)
    conduit = data.get('conduit', [])
    if conduit:
        story.append(Paragraph("📦 Conduit Summary", heading_style))
        
        conduit_headers = ['Type', 'Size', 'Length (ft)', 'NEC Compliant']
        conduit_data = [conduit_headers]
        
        total_conduit = 0
        for item in conduit:
            length = item.get('length_ft', 0)
            total_conduit += length
            
            conduit_data.append([
                item.get('type', 'EMT'),
                item.get('size', ''),
                str(length),
                item.get('nec_compliant', 'Yes')
            ])
        
        # Add total
        conduit_data.append(['TOTAL', '', f"{total_conduit} ft", ''])
        
        conduit_table = Table(conduit_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        conduit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), trade_config['accent_color']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(conduit_table)
        story.append(Spacer(1, 0.2*inch))
    
    # SUMMARY
    summary = data.get('summary', {})
    if summary:
        story.append(Paragraph("📊 Project Summary", heading_style))
        
        summary_data = [
            ['Total Devices:', str(summary.get('total_devices', 0))],
            ['Total Conduit:', f"{summary.get('total_conduit_ft', 0)} ft"],
            ['Total Routes:', str(summary.get('total_routes', 0))],
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (0, -1), trade_config['primary_color']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(summary_table)
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"Generated by AMPED AI Estimating Assistant v3.2", footer_style))
    story.append(Paragraph(f"© 2025 Amped Integrations, LLC", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "service": "AMPED PDF Generator",
        "version": "3.2.0",
        "method": "Pure Python (ReportLab)",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from structured data (NOT HTML)
    
    Expected JSON structure (from "Prepare for Spreadsheet" node):
    {
        "companyName": "string",
        "projectName": "string",
        "tradeType": "electrical|hvac|plumbing|flooring" (optional),
        "deviceCounts": [...],
        "conduitRoutes": [...],
        "conduit": [...],
        "summary": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        project_name = data.get('projectName', 'Project')
        company_name = data.get('companyName', 'AMPED')
        trade_type = data.get('tradeType', 'electrical')
        
        # Get trade configuration
        trade_config = get_trade_config(trade_type)
        
        logger.info(f"Generating PDF for {company_name} - {project_name} ({trade_config['name']})")
        
        # Build PDF from structured data
        pdf_buffer = build_pdf_from_data(data, trade_config)
        
        # Generate filename
        filename = f"{project_name.replace(' ', '_')}_{trade_config['name']}_Annotated.pdf"
        
        # Return PDF
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        return jsonify({
            "error": "PDF generation failed",
            "details": str(e)
        }), 500

@app.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "service": "AMPED PDF Generator",
        "version": "3.2.0",
        "method": "Pure Python (ReportLab - NO system dependencies)",
        "endpoints": {
            "health": "/health",
            "generate_pdf": "/generate-pdf",
            "info": "/api/info"
        },
        "supported_trades": list(TRADE_CONFIGS.keys()),
        "expected_format": {
            "companyName": "string",
            "projectName": "string",
            "tradeType": "string (optional)",
            "deviceCounts": "array",
            "conduitRoutes": "array",
            "conduit": "array",
            "summary": "object"
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/health", "/generate-pdf", "/api/info"]
    }), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
