import json
import logging
from datetime import datetime
import requests
from flask import Flask, request, jsonify

application_ids = {}
kyc_transactions = {}
# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global dictionary to store partial payloads
payload_store = {}

def convert_yes_no_to_boolean(payload):
    """
    Convert 'Yes'/'No' strings to boolean True/False for specific fields
    """
    boolean_fields = [
        'isDirectorDueMissedLast12Months',
        'isDirectorDueMissedLast18Months',
        'isDirectorDueMissedLast6Months'
    ]
    
    processed_payload = payload.copy()
    
    for field in boolean_fields:
        if field in processed_payload:
            if processed_payload[field] == "Yes":
                processed_payload[field] = True
            elif processed_payload[field] == "No":
                processed_payload[field] = False
    
    return processed_payload

def merge_payloads(payload_store):
    """
    Merge multiple partial payloads into a single comprehensive payload
    """
    merged_payload = {}
    
    for partial_payload in payload_store.values():
        merged_payload.update(partial_payload)
    
    return merged_payload

@app.route('/receive-partial-application', methods=['POST'])
def receive_partial_application():
    """
    Endpoint to receive partial POST requests
    """
    try:
        # Get JSON payload
        payload = request.get_json()
        
        # Generate a unique session ID (you might want to pass this from the client)
        session_id = request.args.get('session_id', 'default_session')
        
        # Ensure the session exists in the payload store
        if session_id not in payload_store:
            payload_store[session_id] = {}
        
        # Determine which type of payload this is and store accordingly
        if 'applicantAadhaar' in payload:
            payload_store[session_id]['applicant'] = payload
        elif 'companyCIN' in payload:
            payload_store[session_id]['company'] = payload
        elif 'directorAadhaar' in payload:
            payload_store[session_id]['director'] = payload
        
        # Log the received payload
        logger.info(f"Received partial payload for session {session_id}:")
        logger.info(json.dumps(payload, indent=2))
        
        # Check if all parts are received
        if len(payload_store[session_id]) == 3:
            # Merge payloads
            final_payload = merge_payloads(payload_store[session_id])
            
            # Process the payload
            processed_payload = convert_yes_no_to_boolean(final_payload)
            
            # Forward to target server
            target_response = forward_to_target_server(processed_payload)
            
            # Store the application ID
            application_ids[session_id] = target_response.get('applicationId')
            
            # Clear the payload store for this session
            del payload_store[session_id]
            
            # Prepare response
            return jsonify({
                "status": "success",
                "message": "Complete application received and forwarded",
                "processedPayload": processed_payload,
                "targetResponse": target_response
            }), 200
        else:
            # Not all parts received yet
            return jsonify({
                "status": "partial",
                "message": "Partial application received",
                "partsReceived": list(payload_store[session_id].keys())
            }), 202
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

def forward_to_target_server(payload):
    """
    Forward the processed payload to the target server
    """
    try:
        # Replace with your actual target server URL
        target_url = 'https://5d49-14-99-167-142.ngrok-free.app/receive-partial-application'  # Use httpbin for testing
        
        # Set up headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        
        # Send POST request
        response = requests.post(
            target_url, 
            data=payload_json,
            headers=headers
        )
        
        # Check response
        response.raise_for_status()
        
        logger.info(f"Successfully forwarded request to {target_url}")
        logger.info(f"Response Status: {response.status_code}")
        
        return response.json()
    
    except requests.RequestException as e:
        logger.error(f"Error forwarding request: {e}")
        raise
@app.route('/receive-kyc-details', methods=['POST'])
def receive_kyc_details():
    """
    Endpoint to receive KYC details and forward to target server
    """
    try:
        # Get JSON payload
        payload = request.get_json()
        
        # Validate required fields
        required_fields = [
            'applicantBankBranchName', 
            'applicantFullName', 
            'applicantBankAccountNumber', 
            'applicantBankName', 
            'applicantBankIFSCCode', 
            'ApplicantId'
        ]
        for field in required_fields:
            if field not in payload:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Forward to target server with application ID in URL
        target_url = 'https://mock-51e439ddcad24fc78831c096a2513df0.mock.insomnia.rest/onboard-kyc'

        
        headers = {'Content-Type': 'application/json'}
        payload_json = json.dumps(payload)
        
        try:
            response = requests.post(target_url, data=payload_json, headers=headers)
            response.raise_for_status()
            
            # Extract the response from the target server
            response_data = response.json()
            transaction_id = response_data.get("TransactionId")
            applicant_id = response_data.get("ApplicantId")
            
            # Store in the temporary dictionary
            if transaction_id and applicant_id:
                kyc_transactions[applicant_id] = transaction_id
            
            return jsonify({
                "status": "success",
                "message": "KYC details forwarded successfully",
                "targetResponse": response_data
            }), 200
        
        except requests.RequestException as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to forward KYC request: {str(e)}"
            }), 500
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
        
if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5003, debug=True)