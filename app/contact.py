from flask import Blueprint, request, jsonify
from email.message import EmailMessage
import smtplib
import requests
import os
import re
import requests


contact_bp = Blueprint("contact_bp", __name__)

RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
RECAPTCHA_THRESHOLD = float(os.getenv('RECAPTCHA_THRESHOLD', '0.5'))
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))

def verify_recaptcha(token: str, expected_action: str) -> dict:
    try:
        resp = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={'secret': RECAPTCHA_SECRET_KEY, 'response': token},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
    except:
        return {'success': False, 'error': 'recaptcha-request-failed'}

    if not data.get('success'):
        return {'success': False, 'error': 'recaptcha-invalid', 'raw': data}

    if data.get('action') != expected_action:
        return {'success': False, 'error': 'recaptcha-action-mismatch', 'raw': data}

    if float(data.get('score', 0)) < RECAPTCHA_THRESHOLD:
        return {'success': False, 'error': 'recaptcha-score-too-low', 'score': data.get('score')}

    return {'success': True, 'score': data.get('score')}

def send_contact_email(payload: dict):
    msg = EmailMessage()
    body = (
        f"New Contact Form Submission:\n\n"
        f"Name: {payload['name']}\n"
        f"Email: {payload['email']}\n"
        f"Phone: {payload.get('phone', 'N/A')}\n"
        f"Subject: {payload['subject']}\n\n"
        f"Message:\n{payload['message']}\n"
    )
    msg.set_content(body)
    msg['Subject'] = f"Contact: {payload['subject']}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Reply-To'] = payload['email']

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as smtp:
        smtp.ehlo()
        if SMTP_PORT == 587:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)

    return True, 'sent'


@contact_bp.route('/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({'error': 'invalid-json'}), 400

    required = ['name', 'email', 'subject', 'message', 'recaptchaToken']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing-fields'}), 400

    if not is_valid_email(data['email']):
        return jsonify({'error': 'invalid-email'}), 400

    verify = verify_recaptcha(data['recaptchaToken'], expected_action='contact_submit')
    if not verify.get('success'):
        return jsonify({'error': 'recaptcha-failed', 'detail': verify.get('error')}), 401

    sent, info = send_contact_email(data)
    if not sent:
        return jsonify({'error': 'email-failed', 'detail': info}), 502

    return jsonify({'message': 'Message sent successfully.'}), 200
