# AMPED PDF Generator

A production-grade Flask microservice for generating annotated electrical estimating PDFs. Part of the AMPED AI Estimating Assistant workflow.

## Overview

This service generates professional PDF estimates with electrical routing, device, and conduit markup annotations. It's designed to integrate seamlessly with n8n workflows and maintain the full complexity and power of the AMPED estimating software.

## Features

- **Comprehensive PDF Generation**: Creates detailed electrical estimation PDFs with proper formatting
- - **Multi-Section Annotations**: Supports routes, devices, and conduit data with dedicated sections
  - - **Form-URL-Encoded Input**: Compatible with n8n workflow HTTP nodes using standard form parameters
    - - **JSON Parsing**: Automatically parses JSON arrays from form data
      - - **Responsive Design**: Landscape orientation for better annotation space
        - - **Production Ready**: Built with gunicorn for Railway deployment
          - - **Health Monitoring**: Includes `/health` endpoint for deployment monitoring
            - - **API Documentation**: Built-in `/api/pdf-info` endpoint describing service capabilities
             
              - ## Requirements
             
              - - Python 3.8+
                - - Flask 3.0.0
                  - - reportlab 4.0.9 (for PDF generation)
                    - - Pillow 10.1.0 (for image processing)
                      - - gunicorn 21.2.0 (for production deployment)
                       
                        - ## Installation
                       
                        - ### Local Development
                       
                        - ```bash
                          # Clone the repository
                          git clone https://github.com/andyamped/amped-pdf-generator.git
                          cd amped-pdf-generator

                          # Create virtual environment
                          python -m venv venv
                          source venv/bin/activate  # On Windows: venv\Scripts\activate

                          # Install dependencies
                          pip install -r requirements.txt

                          # Run the application
                          python app.py
                          ```

                          The application will start on `http://localhost:5000`.

                          ## API Endpoints

                          ### GET `/health`

                          Health check endpoint for monitoring service availability.

                          **Response:**
                          ```json
                          {
                            "status": "healthy",
                            "service": "amped-pdf-generator"
                          }
                          ```

                          ### POST `/generate-pdf`

                          Generate an annotated PDF from electrical estimating data.

                          **Content-Type:** `application/x-www-form-urlencoded`

                          **Parameters:**
                          - `routes` (JSON array): Array of route objects with properties like type, length, conduit
                          - - `devices` (JSON array): Array of device objects with properties like type, quantity, voltage
                            - - `conduit` (JSON array): Array of conduit objects with properties like size, type, length
                             
                              - **Example Request:**
                              - ```bash
                                curl -X POST http://localhost:5000/generate-pdf \
                                  -d "routes=[{\"type\":\"EMT\",\"length\":\"100\",\"conduit\":\"3/4\"}]" \
                                  -d "devices=[{\"type\":\"Breaker\",\"quantity\":\"1\",\"voltage\":\"120\"}]" \
                                  -d "conduit=[{\"size\":\"3/4\",\"type\":\"EMT\",\"length\":\"100\"}]"
                                ```

                                **Response:**
                                - Returns a PDF file attachment named `estimate_YYYYMMDD_HHMMSS.pdf`
                               
                                - **Error Responses:**
                                - - 400: Invalid form data (malformed JSON arrays)
                                  - - 500: Internal server error during PDF generation
                                   
                                    - ### GET `/api/pdf-info`
                                   
                                    - API information endpoint describing the service, endpoints, and expected fields.
                                   
                                    - **Response:**
                                    - ```json
                                      {
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
                                      }
                                      ```

                                      ## n8n Workflow Integration

                                      In your n8n workflow HTTP node:

                                      1. **Method:** POST
                                      2. 2. **URL:** `https://your-railway-domain.app/generate-pdf`
                                         3. 3. **Authentication:** None (unless you add authentication)
                                            4. 4. **Body Content Type:** Form Urlencoded
                                               5. 5. **Form Parameters:**
                                                  6.    - `routes`: JSON string of routes array
                                                        -    - `devices`: JSON string of devices array
                                                             -    - `conduit`: JSON string of conduit array
                                                              
                                                                  - ## Deployment on Railway
                                                              
                                                                  - ### Prerequisites
                                                                  - - Railway account at https://railway.app
                                                                    - - GitHub repository connected to Railway
                                                                     
                                                                      - ### Deployment Steps
                                                                     
                                                                      - 1. Create a new Railway project
                                                                        2. 2. Connect your GitHub repository
                                                                           3. 3. Railway will automatically detect the `Procfile` and `requirements.txt`
                                                                              4. 4. Set environment variables if needed (PORT defaults to 5000)
                                                                                 5. 5. Deploy
                                                                                   
                                                                                    6. The service will be available at: `https://<your-service-name>.up.railway.app`
                                                                                   
                                                                                    7. ### Environment Variables
                                                                                   
                                                                                    8. - `PORT` (optional): Server port (default: 5000)
                                                                                      
                                                                                       - ## PDF Output Format
                                                                                      
                                                                                       - The generated PDF includes:
                                                                                      
                                                                                       - 1. **Header Section**
                                                                                         2.    - Title: "AMPED Electrical Estimating Report"
                                                                                               -    - Generation timestamp
                                                                                                
                                                                                                    - 2. **Electrical Routes**
                                                                                                      3.    - Type, length, and conduit information
                                                                                                            -    - Color-coded section (blue)
                                                                                                             
                                                                                                                 - 3. **Electrical Devices**
                                                                                                                   4.    - Device type, quantity, and voltage
                                                                                                                         -    - Color-coded section (green)
                                                                                                                          
                                                                                                                              - 4. **Conduit Schedule**
                                                                                                                                5.    - Size, type, and length specifications
                                                                                                                                      -    - Color-coded section (brown)
                                                                                                                                       
                                                                                                                                           - 5. **Summary**
                                                                                                                                             6.    - Totals for routes, devices, and conduit items
                                                                                                                                               
                                                                                                                                                   - ## Architecture
                                                                                                                                               
                                                                                                                                                   - ### Core Components
                                                                                                                                               
                                                                                                                                                   - - **parse_form_data()**: Extracts and validates form parameters, handling both string and list JSON formats
                                                                                                                                                     - - **generate_pdf_with_annotations()**: Generates the PDF document with proper formatting and annotations
                                                                                                                                                       - - **Flask Routes**: RESTful API endpoints for health checks, PDF generation, and service info
                                                                                                                                                        
                                                                                                                                                         - ### Dependencies
                                                                                                                                                         - 
                                                                                                                                                         - **Flask**: Web framework for HTTP API
                                                                                                                                                         - - **reportlab**: Professional PDF generation
                                                                                                                                                           - - **Werkzeug**: WSGI application library (Flask dependency)
                                                                                                                                                             - - **Pillow**: Image processing (for potential future image embedding)
                                                                                                                                                               - - **gunicorn**: Production WSGI HTTP server
                                                                                                                                                                
                                                                                                                                                                 - ## Logging and Monitoring
                                                                                                                                                                
                                                                                                                                                                 - The application includes comprehensive logging for:
                                                                                                                                                                 - - PDF generation operations
                                                                                                                                                                   - - Form data parsing errors
                                                                                                                                                                     - - Validation errors
                                                                                                                                                                       - - Unexpected exceptions
                                                                                                                                                                        
                                                                                                                                                                         - Logs are written to stdout for Railway console monitoring.
                                                                                                                                                                        
                                                                                                                                                                         - ## Troubleshooting
                                                                                                                                                                         
                                                                                                                                                                         ### "Invalid form data" Error
                                                                                                                                                                         - Ensure routes, devices, and conduit parameters are valid JSON strings
                                                                                                                                                                         - - Check that JSON arrays are properly formatted with no extra characters
                                                                                                                                                                          
                                                                                                                                                                           - ### PDF generation fails
                                                                                                                                                                           - - Verify adequate server memory (reportlab can be memory-intensive)
                                                                                                                                                                             - - Check server logs for specific error messages
                                                                                                                                                                               - - Ensure dataset isn't excessively large
                                                                                                                                                                                
                                                                                                                                                                                 - ### n8n connection issues
                                                                                                                                                                                 - - Verify the Railway endpoint URL is correct
                                                                                                                                                                                   - - Confirm Form Urlencoded content type is set in n8n HTTP node
                                                                                                                                                                                     - - Check that n8n can reach the Railway service (no firewall blocks)
                                                                                                                                                                                      
                                                                                                                                                                                       - ## Excel Generator Integration
                                                                                                                                                                                      
                                                                                                                                                                                       - This PDF generator complements the existing amped-excel-generator service. Both can be used in the same n8n workflow:
                                                                                                                                                                                       - - Excel generator: Creates detailed Excel workbooks
                                                                                                                                                                                         - - PDF generator: Creates annotated PDF estimates
                                                                                                                                                                                           - 
                                                                                                                                                                                           Both services maintain full data integrity and complexity.

## License

Proprietary - AMPED Solutions

## Support

For issues or questions, contact the AMPED development team.

## Version History

### v1.0.0 (2026-01-11)
- Initial release
- - Support for routes, devices, and conduit annotations
  - - Railway deployment ready
    - - n8n workflow integration
