from fastapi import Request, HTTPException, status
from fraud_detection import fraud_engine

async def check_fraud(request: Request):
    """Check for fraud patterns in request"""
    client_ip = request.client.host
    
    # Check if IP is blocked
    if fraud_engine.is_ip_blocked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - IP blocked due to suspicious activity"
        )
    
    # For registration requests, check for multiple registrations
    if request.url.path == "/auth/register" and request.method == "POST":
        body = await request.json()
        email = body.get("email")
        
        if email and fraud_engine.is_email_blocked(email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email blocked - multiple registration attempts"
            )
        
        # Check for suspicious patterns
        if email:
            fraud_check = fraud_engine.check_multiple_registrations(email, client_ip)
            if fraud_check["is_suspicious"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many registration attempts. Please try again later."
                )
