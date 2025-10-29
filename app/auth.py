# backend/app/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_cors import cross_origin
from app.models import Admin
from app import db
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def login():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Missing username or password"}), 400

    admin = Admin.query.filter_by(username=data["username"]).first()

    # 👇 Plain text check
    if not admin or admin.password != data["password"]:
        return jsonify({"msg": "Invalid credentials"}), 401

    expires = datetime.timedelta(days=1)
    access_token = create_access_token(identity=admin.username, expires_delta=expires)

    return jsonify({"msg": "Login successful", "access_token": access_token, "admin": admin.username}), 200
   