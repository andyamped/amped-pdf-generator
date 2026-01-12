import os
import json
import logging
from io import BytesIO
from flask import Flask, request, send_file, jsonify
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

def parse_form_data(request_data):
      """Parse form-urlencoded data from n8n workflow."""
      try:
                routes = request_data.get('routes', '[]')
                devices = request_data.get('devices', '[]')
                conduit = request_data.get('conduit', '[]')

        # Handle both string and list formats
                if isinstance(routes, str):
                              routes = json.loads(routes) if routes else []
                          if isinstance(devices, str):
                                        devices = json.loads(devices) if devices else []
                                    if isinstance(conduit, str):
                                                  conduit = json.loads(conduit) if conduit else []

        return routes, devices, conduit
except Exception as e:
        logger.error(f"Error parsing form data: {str(e)}")
        raise ValueError(f"Invalid form data: {str(e)}")

def generate_pdf_with_annotations(routes, devices, conduit):
      """Generate PDF with electrical routing, device, and conduit annotations."""
    try:
              # Create PDF in landscape orientation for better annotation space
              buffer = BytesIO()
              c = canvas.Canvas(buffer, pagesize=landscape(letter))
              width, height = landscape(letter)

        # Add header
              c.setFont("Helvetica-Bold", 24)
              c.drawString(0.5*inch, height - 0.5*inch, "AMPED Electrical Estimating Report")

        # Add timestamp
              c.setFont("Helvetica", 10)
              timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              c.drawString(0.5*inch, height - 0.75*inch, f"Generated: {timestamp}")

        # Draw section divider
              c.setLineWidth(1)
              c.line(0.5*inch, height - 0.9*inch, width - 0.5*inch, height - 0.9*inch)

        # Current vertical position for content
              y_position = height - 1.2*inch
              line_height = 0.2*inch
              section_spacing = 0.3*inch

        # ROUTES SECTION
              if routes:
                            c.setFont("Helvetica-Bold", 14)
                            c.setFillColor(colors.HexColor("#1f4788"))
                            c.drawString(0.5*inch, y_position, "ELECTRICAL ROUTES")
                            y_position -= line_height

            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)

            for idx, route in enumerate(routes, 1):
                              route_text = f"Route {idx}: "
                              if isinstance(route, dict):
                                                    route_text += f"Type={route.get('type', 'Unknown')}, "
                                                    route_text += f"Length={route.get('length', 'N/A')}ft, "
                                                    route_text += f"Conduit={route.get('conduit', 'N/A')}"
else:
                    route_text += str(route)

                c.drawString(0.75*inch, y_position, route_text)
                y_position -= line_height

            y_position -= section_spacing

        # DEVICES SECTION
        if devices:
                      c.setFont("Helvetica-Bold", 14)
                      c.setFillColor(colors.HexColor("#2d5016"))
                      c.drawString(0.5*inch, y_position, "ELECTRICAL DEVICES")
                      y_position -= line_height

            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)

            for idx, device in enumerate(devices, 1):
                              device_text = f"Device {idx}: "
                              if isinstance(device, dict):
                                                    device_text += f"Type={device.get('type', 'Unknown')}, "
                                                    device_text += f"Qty={device.get('quantity', 'N/A')}, "
                                                    device_text += f"Voltage={device.get('voltage', 'N/A')}V"
else:
                    device_text += str(device)

                c.drawString(0.75*inch, y_position, device_text)
                y_position -= line_height

            y_position -= section_spacing

        # CONDUIT SECTION
        if conduit:
                      c.setFont("Helvetica-Bold", 14)
                      c.setFillColor(colors.HexColor("#8b4513"))
                      c.drawString(0.5*inch, y_position, "CONDUIT SCHEDULE")
                      y_position -= line_height

            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)

            for idx, conduit_item in enumerate(conduit, 1):
                              conduit_text = f"Conduit {idx}: "
                              if isinstance(conduit_item, dict):
                                                    conduit_text += f"Size={conduit_item.get('size', 'Unknown')}, "
                                                    conduit_text += f"Type={conduit_item.get('type', 'N/A')}, "
                                                    conduit_text += f"Length={conduit_item.get('length', 'N/A')}ft"
else:
                    conduit_text += str(conduit_item)

                c.drawString(0.75*inch, y_position, conduit_text)
                y_position -= line_height

            y_position -= section_spacing

        # Add summary section
        c.setLineWidth(1)
        c.line(0.5*inch, y_position, width - 0.5*inch, y_position)
        y_position -= section_spacing

        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#1f4788"))
        c.drawString(0.5*inch, y_position, "SUMMARY")
        y_position -= line_height

        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(0.75*inch, y_position, f"Total Routes: {len(routes)}")
        y_position -= line_height
        c.drawString(0.75*inch, y_position, f"Total Devices: {len(devices)}")
        y_position -= line_height
        c.drawString(0.75*inch, y_position, f"Total Conduit Items: {len(conduit)}")

        # Save and return PDF
        c.save()
        buffer.seek(0)
        return buffer

except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
      """Health check endpoint for Railway monitoring."""
    return jsonify({"status": "healthy", "service": "amped-pdf-generator"}), 200

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
      """Generate annotated PDF from electrical estimating data.

              Expected form-urlencoded data:
                  - routes: JSON array of route objects
                      - devices: JSON array of device objects
                          - conduit: JSON array of conduit objects
                              """
    try:
              # Parse input data
              routes, devices, conduit = parse_form_data(request.form)

        logger.info(f"Generating PDF with {len(routes)} routes, {len(devices)} devices, {len(conduit)} conduit items")

        # Generate PDF
        pdf_buffer = generate_pdf_with_annotations(routes, devices, conduit)

        # Return PDF file
        return send_file(
                      pdf_buffer,
                      mimetype='application/pdf',
                      as_attachment=True,
                      download_name=f'estimate_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )

except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/pdf-info', methods=['GET'])
def pdf_info():
      """API endpoint providing information about the PDF generator service."""
    return jsonify({
              "service": "AMPED PDF Generator",
              "version": "1.0.0",
              "endpoints": {
                            "health": "/health",
                            "generate_pdf": "/generate-pdf",
                            "info": "/api/pdf-info"
              },
              "expected_fields": {
                            "routes": "JSON array of electrical routes",
                            "devices": "JSON array of electrical devices",
                            "conduit": "JSON array of conduit specifications"
              },
              "content_type": "application/x-www-form-urlencoded"
    }), 200

if __name__ == '__main__':
      port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
