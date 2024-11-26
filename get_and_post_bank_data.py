from flask import Flask, jsonify, request
import pandas as pd
import os
import requests

app = Flask(__name__)

# Backend server for posting data
Onboarded_URL_Server = 'https://f93d-2401-4900-9018-253c-4dc5-1ae6-b7c4-7e16.ngrok-free.app/onboard-Applicant/{}'

# Function to read Excel file and handle errors
def read_excel_sheet(file_path, sheet_name):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except Exception as e:
        return str(e)

# Normalize bank data
def normalize_bank_data(row):
    return {
        "ApplicantId": row['Applicant id'],
        "applicantFullName": row['Name'],
        "applicantBankAccountNumber": int(row['Account No.']),
        "applicantBankName": row['Bank Name'],
        "applicantBankIFSCCode": row['IFSC Code'],
        "applicantBankBranchName": row['Branch Name']
    }

# API endpoint for retrieving bank data by Applicant ID
@app.route('/bank-data/<string:applicant_id>', methods=['GET'])
def get_bank_data_by_id(applicant_id):
    file_path = 'sample_excel_api.xlsx'
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        # Read the "Bank_Data" sheet
        df = read_excel_sheet(file_path, 'Bank_Data')
        if isinstance(df, str):  # Check if an error occurred
            return jsonify({'error': df}), 500

        # Filter rows by Applicant ID
        applicant_df = df[df['Applicant id'] == applicant_id]
        if applicant_df.empty:
            return jsonify({'error': 'Applicant bank data not found'}), 404

        # Extract and normalize data
        bank_data = [normalize_bank_data(row) for index, row in applicant_df.iterrows()][0]  # Expecting one result

        # Post the normalized data to the target server
        try:
            target_url = Onboarded_URL_Server.format(applicant_id)
            response = requests.post(
                target_url,
                json=bank_data,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code != 200:
                return jsonify({
                    'data': bank_data,
                    'warning': f'Failed to send data to target server. Status code: {response.status_code}'
                }), 206  # Partial Content

        except requests.exceptions.RequestException as e:
            return jsonify({
                'data': bank_data,
                'error': f'Network error when sending data: {e}'
            }), 206  # Partial Content

        return jsonify(bank_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True)
