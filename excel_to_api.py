from flask import Flask, jsonify
import pandas as pd
import os
import uuid

app = Flask(__name__)

# Define allowed Excel file extensions
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}

def read_excel_sheet(file_path, sheet_name):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except Exception as e:
        return str(e)

# Normalize company data
def normalize_company_data(row):
    return {
        "Applicant ID": row['Applicant id'],
        "Company Name": row['Company Name'],
        "CIN": row['CIN'],
        "GSTIN": row['GSTIN'],
        "Company PAN": row['Company PAN'],
        "Company Phone": int(row['Company Phone']),
        "Company Email": row['Company Email'],
        "Company Address": row['Company Address'],
        "Company MSME": row['Company MSME']
    }

# Normalize bank data
def normalize_bank_data(row):
    return {
        "Applicant id": row['Applicant id'],
        "Name": row['Name'],
        "Account No.": row['Account No.'],
        "Bank Name": row['Bank Name'],
        "IFSC Code": row['IFSC Code'],
        "Branch Name": row['Branch Name']
    }
    
# Normalize applicant data
def normalize_applicant_data(row):
    return {
        "Applicant id": row['Applicant id'],
        "First Name": row['First Name'],
        "Last Name": row['Last Name'],
        "Email": row['Email'],
        "Phone": row['Phone'],
        "Designation": row['Designation'],
        "Aadhar": row['Aadhar']
    }

# Normalize directors data
def normalize_directors_data(row):
    return {
        "Applicant ID": row['Applicant id'],
        "Director First Name": row['Director First Name'],
        "Director Last Name": row['Director Last Name'],
        "Director Email": row['Director Email'],
        "Director Phone": row['Director Phone'],
        "Director Designation": row['Director Designation'],
        "Director PAN": row['Director PAN'],
        "Director Aadhaar": row['Director Aadhaar'],
        "Total Current No. of Loans": int(row['Total Current No. of Loans']),
        "Total Current No. of ODs": int(row['Total Current No. of ODs']),
        "Total Current Loan Outstanding": int(row['Total Current Loan Outstanding']),
        "Current Total EMI": int(row['Current Total EMI']),
        "Any Dues Missed in Last 6 Months": row['Any Dues Missed in Last 6 Months'] == 'Yes',
        "Any Dues Missed in Last 12 Months": row['Any Dues Missed in Last 12 Months'] == 'Yes',
        "Any Dues Missed in Last 18 Months": row['Any Dues Missed in Last 18 Months'] == 'Yes'
    }

# API endpoint for company data
@app.route('/company-data', methods=['GET'])
def get_company_data():
    file_path = 'sample_excel_api.xlsx'
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    try:
        df = read_excel_sheet(file_path, 'Company_Data')
        data = [normalize_company_data(row) for index, row in df.iterrows()]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint to retrieve all data by applicant ID
@app.route('/onboard-Applicant/<string:applicant_id>', methods=['GET'])
def get_all_data_by_id(applicant_id):
    file_path = 'sample_excel_api.xlsx'
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read company data
    company_response = read_excel_sheet(file_path, 'Company_Data')
    if "error" in company_response:
        return jsonify(company_response), 500
    company_df = company_response[company_response['Applicant id'] == applicant_id]
    if company_df.empty:
        return jsonify({'error': 'Company data not found'}), 404
    company_data = company_df.iloc[0]

    # Read applicant data
    applicant_response = read_excel_sheet(file_path, 'Applicant_Data')
    if "error" in applicant_response:
        return jsonify(applicant_response), 500
    applicant_df = applicant_response[applicant_response['Applicant id'] == applicant_id]
    if applicant_df.empty:
        return jsonify({'error': 'Applicant data not found'}), 404
    applicant_data = applicant_df.iloc[0]

    # Read directors data
    directors_response = read_excel_sheet(file_path, 'Directors_Data')
    if "error" in directors_response:
        return jsonify(directors_response), 500
    directors_df = directors_response[directors_response['Applicant id'] == applicant_id]
    if directors_df.empty:
        return jsonify({'error': 'Directors data not found'}), 404
    directors_data = directors_df.iloc[0]

    # Combine data with explicit type conversion
    all_data = {
        "ApplicantId": applicant_id,
        "companyName": str(company_data['Company Name']),
        "companyCIN": str(company_data['CIN']),
        "companyGSTIN": str(company_data['GSTIN']),
        "companyPAN": str(company_data['Company PAN']),
        "companyPhone": str(company_data['Company Phone']),
        "companyEmail": str(company_data['Company Email']),
        "companyAddress": str(company_data['Company Address']),
        "companyMSME": str(company_data['Company MSME']),
        "applicantFirstName": str(applicant_data['First Name']),
        "applicantLastName": str(applicant_data['Last Name']),
        "applicantEmail": str(applicant_data['Email']),
        "applicantPhone": str(applicant_data['Phone']),
        "applicantDesignation": str(applicant_data['Designation']),
        "applicantAadhaar": str(applicant_data['Aadhar']),
        "directorFirstName": str(directors_data['Director First Name']),
        "directorLastName": str(directors_data['Director Last Name']),
        "directorEmail": str(directors_data['Director Email']),
        "directorPhone": str(directors_data['Director Phone']),
        "directorDesignation": str(directors_data['Director Designation']),
        "directorAadhaar": str(directors_data['Director Aadhaar']),
        "directorPAN": str(directors_data['Director PAN']),
        "directorTotalLoanCount": int(directors_data['Total Current No. of Loans']),
        "directorTotalODCount": int(directors_data['Total Current No. of ODs']),
        "directorCurrentLoanOutstanding": int(directors_data['Total Current Loan Outstanding']),
        "directorCurrentLoanEMI": int(directors_data['Current Total EMI']),
        "isDirectorDueMissedLast6Months": directors_data['Any Dues Missed in Last 6 Months'] == 'Yes',
        "isDirectorDueMissedLast12Months": directors_data['Any Dues Missed in Last 12 Months'] == 'Yes',
        "isDirectorDueMissedLast18Months": directors_data['Any Dues Missed in Last 18 Months'] == 'Yes'
    }
    return jsonify(all_data), 200

# API endpoint for applicant data
@app.route('/applicant-data', methods=['GET'])
def get_applicant_data():
    file_path = 'sample_excel_api.xlsx'
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    response = read_excel_sheet(file_path, 'Applicant_Data')
    if "error" in response:  # Handle read_excel_sheet errors
        return jsonify(response), 500
    data = [normalize_applicant_data(row) for index, row in response.iterrows()]
    return jsonify(data), 200

# API endpoint for directors data
@app.route('/directors-data>', methods=['GET'])
def get_directors_data():
    file_path = 'sample_excel_api.xlsx'
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    try:
        df = read_excel_sheet(file_path, 'Directors_Data')
        print(df.columns)  # Print column names to verify
        data = [normalize_directors_data(row) for index, row in df.iterrows()]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# API endpoint for bank data
@app.route('/bank-data/<string:applicant_id>', methods=['GET'])
def get_bank_data_by_id(applicant_id):
    file_path = 'sample_excel_api.xlsx'
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    try:
        df = read_excel_sheet(file_path, 'Bank_Data')
        applicant_df = df[df['Applicant id'] == applicant_id]
        if applicant_df.empty:
            return jsonify({'error': 'Applicant bank data not found'}), 404
        data = [normalize_bank_data(row) for index, row in applicant_df.iterrows()]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001,debug=True)
    
