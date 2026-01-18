
import sys
import os
import json
import base64
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.database import SessionLocal
from app.models.user import User

def decode_base64_json(s):
    # Add padding if needed
    s += '=' * (-len(s) % 4)
    return json.loads(base64.b64decode(s).decode('utf-8'))

def check_token(token):
    print(f"Checking token: {token[:20]}...")
    try:
        parts = token.split('.')
        if len(parts) != 3:
            print("Invalid token format (not 3 parts)")
            return
        
        header = decode_base64_json(parts[0])
        payload = decode_base64_json(parts[1])
        
        print("Header:", header)
        print("Payload:", payload)
        
        exp = payload.get('exp')
        if exp:
            exp_date = datetime.utcfromtimestamp(exp)
            now = datetime.utcnow()
            print(f"Expiration: {exp} ({exp_date})")
            print(f"Current UTC: {now.timestamp()} ({now})")
            
            if now > exp_date:
                print("STATUS: EXPIRED")
            else:
                remaining = exp_date - now
                print(f"STATUS: VALID (Time-wise). Remaining: {remaining}")
        else:
            print("No exp claim")
            
        sub = payload.get('sub')
        print(f"Subject (username): {sub}")
        
        return sub
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def check_user(username):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"User found: ID={user.id}, Username={user.username}, Role={user.role}, Active={user.is_active}")
        else:
            print("User NOT found in database")
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2NzAwMjcyNn0._njnrrd94wUKddgvWwP_CSj7842klGJftMdccp4v8RY"
    print("--- 1. Token Analysis ---")
    username = check_token(token)
    
    if username:
        print("\n--- 2. Database User Check ---")
        check_user(username)
