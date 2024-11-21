from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional


app = FastAPI(title="KYC Test API")


class KYCRequest(BaseModel):
    customer_id: str
    name: str
    Aadhar_Number: Optional[str] = None
    document_type: Optional[str] = None


sample_data = {
    'ABC123': {
        'name': 'John Doe',
        'Aadhar_Number': '123456789012',
        'document_type': 'Aadhar'
    },
    'XYZ789': {
        'name': 'Jane Smith',
        'Aadhar_Number': '123456789012',
        'document_type': 'Aadhar'
    }
}


@app.post("/verify-kyc", status_code=status.HTTP_200_OK)
async def verify_kyc(request: KYCRequest):
    try:
        # Check if all required fields are present
        if not all([request.customer_id, request.name, request.Aadhar_Number, request.document_type]):
            return {
                "is_verified": False,
                "message": "KYC Verification failed: Incomplete details"
            }

        # Check Aadhar number validity
        if len(request.Aadhar_Number) != 12:
            return {
                "is_verified": False,
                "message": "KYC Verification failed: Invalid Aadhar Number"
            }

        # Check if customer exists in sample data
        customer_data = sample_data.get(request.customer_id)
        
        if not customer_data:
            return {
                "is_verified": False,
                "message": "KYC Verification failed: Customer not found"
            }

        # Verify the data
        is_verified = (
            request.name == customer_data['name'] and
            request.Aadhar_Number == customer_data['Aadhar_Number'] and
            request.document_type == customer_data['document_type']
        )

        return {
            "is_verified": is_verified,
            "message": "KYC Verification successful" if is_verified else "KYC Verification failed"
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)