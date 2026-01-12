#!/usr/bin/env python3
"""
AMPED PDF Generator v3.0 - Production Ready
Converts HTML electrical drawings to professional PDFs
Supports white-labeling for all trades (electrical, HVAC, flooring, plumbing)
"""

from flask import Flask, request, jsonify, send_file
import logging
from datetime import datetime
import os
import io
from xhtml2pdf import pisa

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
        "primary_color": "#0066CC",
        "secondary_color": "#003366",
        "accent_color": "#FF9800"
    },
    "hvac": {
        "name": "HVAC",
        "primary_color": "#FF6B00",
        "secondary_color": "#CC5500",
        "accent_color": "#FFB84D"
    },
    "plumbing": {
        "name": "Plumbing",
        "primary_color": "#2196F3",
        "secondary_color": "#1565C0",
        "accent_color": "#64B5F6"
    },
    "flooring": {
        "name": "Flooring",
        "primary_color": "#8B4513",
        "secondary_color": "#654321",
        "accent_color": "#CD853F"
    }
}

def get_trade_config(trade_type):
    """Get trade configuration, default to electrical"""
    trade = trade_type.lower() if trade_type else "electrical"
    return TRADE_CONFIGS.get(trade, TRADE_CONFIGS["electrical"])

# ============================================================================
# PDF GENERATION
# ============================================================================

def inject_trade_branding(html_content, trade_config):
    """Inject trade-specific colors into HTML"""
    # Replace color placeholders with trade-specific colors
    html_content = html_content.replace("#0066CC", trade_config["primary_color"])
    html_content = html_content.replace("#003366", trade_config["secondary_color"])
    html_content = html_content.replace("#ff9800", trade_config["accent_color"])
    return html_content

def convert_html_to_pdf(html_content):
    """Convert HTML to PDF using xhtml2pdf"""
    try:
        # Create PDF buffer
        pdf_buffer = io.BytesIO()
        
        # Convert HTML to PDF
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=pdf_buffer,
            encoding='utf-8'
        )
        
        if pisa_status.err:
            raise Exception(f"PDF conversion error: {pisa_status.err}")
        
        pdf_buffer.seek(0)
        return pdf_buffer
        
    except Exception as e:
        logger.error(f"HTML to PDF conversion failed: {str(e)}")
        raise

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "service": "AMPED PDF Generator",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from HTML content
    
    Expected JSON:
    {
        "htmlContent": "<html>...</html>",
        "projectName": "Project Name",
        "companyName": "Company Name",
        "tradeType": "electrical|hvac|plumbing|flooring" (optional, defaults to electrical)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract data
        html_content = data.get('htmlContent')
        if not html_content:
            return jsonify({"error": "Missing required field: htmlContent"}), 400
        
        project_name = data.get('projectName', 'Project')
        company_name = data.get('companyName', 'AMPED')
        trade_type = data.get('tradeType', 'electrical')
        
        # Get trade configuration
        trade_config = get_trade_config(trade_type)
        
        # Inject trade-specific branding
        branded_html = inject_trade_branding(html_content, trade_config)
        
        logger.info(f"Generating PDF for {company_name} - {project_name} ({trade_config['name']})")
        
        # Convert to PDF
        pdf_buffer = convert_html_to_pdf(branded_html)
        
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
        "version": "3.0.0",
        "endpoints": {
            "health": "/health",
            "generate_pdf": "/generate-pdf",
            "info": "/api/info"
        },
        "supported_trades": list(TRADE_CONFIGS.keys()),
        "expected_format": {
            "htmlContent": "HTML string (required)",
            "projectName": "string (optional)",
            "companyName": "string (optional)",
            "tradeType": "string (optional, defaults to 'electrical')"
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
