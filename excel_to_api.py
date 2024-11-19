from flask import Flask, jsonify
import pandas as pd
import os
from collections import OrderedDict

app = Flask(__name__)

# Define allowed Excel file extensions
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}

def excel_to_json(file_path):
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        # Normalize data
        normalized_data = []
        for index, row in df.iterrows():
            company_data = {
                "Company Name": row['Company Name'],
                "CIN": row['CIN'],
                "GSTIN": row['GSTIN'],
                "Company PAN": row['Company PAN'],
                "Company Phone": int(row['Company Phone']),
                "Company Email": row['Company Email'],
                "Company Adderess": row['Company Adderess'],
                "Company MSME": row['Company MSME']
            }
            
            directors = [OrderedDict([
                ("No. of directors", int(row['No. of Directors'])),
                ("First Name", row['Director First Name']),
                ("Last Name", row['Director Last Name']),
                ("Email", row['Director Email']),
                ("Phone", row['Director Phone']),
                ("Designation", row['Director Designation']),
                ("PAN", row['Director PAN']),
                ("Aadhaar", row['Director Aadhaar']),
                ("Total Current No. of Loans", int(row['Total Current No. of Loans'])),
                ("Total Current No. of ODs", int(row['Total Current No. of ODs'])),
                ("Total Current Loan Outstanding", int(row['Total Current Loan outstanding'])),
                ("Current Total EMI", int(row['Current total EMI'])),
                ("Any dues missed in last 6 months", row['Any dues missed in last 6 months'] == 'Yes'),
                ("Any dues missed in last 12 months", row['Any dues missed in last 12 months'] == 'Yes'),
                ("Any dues missed in last 18 months", row['Any dues missed in last 18 months'] == 'Yes')
            ])]
            
            Applicant = {
                "First Name": row['First Name'],
                "Last Name": row['Last Name'],
                "Email": row['Email'],
                "Phone": row['Phone'],
                "Designation": row['Designation'],
                "Aadhar": row['Aadhar']
            }
            
            normalized_data.append({
                "Company Details": company_data,
                "Applicant": Applicant,
                "Directors": directors
            })
        return normalized_data
    except Exception as e:
        return str(e)

# Convert Excel to JSON API endpoint
@app.route('/convert/<filename>', methods=['GET'])
def convert_excel(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': f'File {filename} not found'}), 404
    
    if os.path.splitext(filename)[1].lower() not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        data = excel_to_json(file_path)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# List available Excel files API endpoint
@app.route('/list-files', methods=['GET'])
def list_excel_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_files = [f for f in os.listdir(current_dir) if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]
    return jsonify({'excel_files': excel_files})

if __name__ == '__main__':
    app.run(debug=True)