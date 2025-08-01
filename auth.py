from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import logging
import datetime
from models import db, User # Make sure User is imported here
from emails_utils import send_email 

# Create a Blueprint for authentication routes
# The url_prefix will make all routes in this blueprint start with /auth
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize URLSafeTimedSerializer
def get_serializer():
    # Use JWT_SECRET_KEY from app config for consistency and security
    # It must be the same key used in main.py for JWTManager
    return URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])

# --- User Registration ---
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email") # Ensure email is expected in the register request
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing username, email, or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = generate_password_hash(password)
    # Ensure User model supports 'email' and 'is_verified'
    new_user = User(username=username, email=email, password=hashed_password, is_verified=False)
    db.session.add(new_user)
    db.session.commit()

    # Send verification email
    s = get_serializer()
    # Using 'email-confirm' salt to prevent token misuse for other purposes
    token = s.dumps(email, salt='email-confirm')
    # Correctly generates external URL for email verification route
    verification_link = url_for('auth.verify_email', token=token, _external=True)
    send_email("Verify Your Email for OpenQQuantify", email, f"Click to verify your email: {verification_link}")

    return jsonify({"message": "User registered successfully. Check your email for verification."}), 201

# --- User Login ---
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        # Optional: Add check for email verification if desired
        # if not user.is_verified:
        #     return jsonify({"error": "Email not verified. Please check your inbox or register again."}), 403
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# --- Email Verification ---
# Route should match the url_prefix set on the blueprint
@auth_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    s = get_serializer()
    try:
        # Using 'email-confirm' salt to load the token
        email = s.loads(token, salt='email-confirm', max_age=3600) # Token valid for 1 hour
    except Exception:
        return jsonify({"error": "The verification link is invalid or has expired."}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        if not user.is_verified:
            user.is_verified = True
            db.session.commit()
            return jsonify({"message": "Email verified successfully!"}), 200
        else:
            return jsonify({"message": "Email already verified."}), 200
    return jsonify({"error": "User not found."}), 404

# --- Password Reset Request ---
@auth_bp.route("/request-reset", methods=["POST"])
def request_reset():
    data = request.json
    email = data.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404 # Do not disclose if user exists

    s = get_serializer()
    # Using 'password-reset' salt for password reset tokens
    token = s.dumps(email, salt='password-reset')
    reset_link = url_for('auth.reset_password', token=token, _external=True)
    send_email("Password Reset for OpenQQuantify", email, f"Click to reset your password: {reset_link}")

    # Optionally, record when the reset token was sent to invalidate old tokens
    user.reset_token_sent_at = datetime.datetime.now()
    db.session.commit()

    return jsonify({"message": "Password reset link sent! Check your email."}), 200

# --- Password Reset ---
@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    s = get_serializer()
    try:
        # Using 'password-reset' salt to load the token, enforce max_age
        email = s.loads(token, salt='password-reset', max_age=3600) # Token valid for 1 hour
    except Exception:
        return jsonify({"error": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Optional: Further checks for token validity (e.g., if it's too old based on reset_token_sent_at)
    # if user.reset_token_sent_at and (datetime.datetime.now() - user.reset_token_sent_at).total_seconds() > 3600:
    #     return jsonify({"error": "Password reset link has expired."}), 400 # Or redirect to request new one

    data = request.json
    new_password = data.get("password")
    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    user.password = generate_password_hash(new_password)
    user.reset_token_sent_at = None # Clear timestamp after successful reset
    db.session.commit()
    return jsonify({"message": "Password updated successfully."}), 200