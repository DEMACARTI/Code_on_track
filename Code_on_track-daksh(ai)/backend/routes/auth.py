from flask import Blueprint, request, jsonify
import jwt
import datetime
from config import SECRET_KEY

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    print(f"DEBUG: Login attempt. Data: {data}")
    username = data.get('username')
    password = data.get('password')
    print(f"DEBUG: User: {username}, Pass: {password}")

    if username == "admin" and password == "admin":
        # Create token
        token_payload = {
            "sub": username,
            "role": "admin",
            "email": "admin@example.com",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
        return jsonify({
            "access_token": token,
            "user": {
                "sub": username,
                "role": "admin",
                "email": "admin@example.com"
            }
        })
    
    return jsonify({"error": "Invalid credentials"}), 401
