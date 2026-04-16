# main.py - Sovereign Heritage Core Standalone Service
# Primary handler for the Secure Personal Database API.
import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from sovereign_heritage_core import SovereignHeritageCore

app = Flask(__name__)
CORS(app)

# --- SECURITY INITIALIZATION ---
# In a commercial production environment, the Master Key is provided
# via a secure login handshake and is never persisted in plain text.
MASTER_KEY = os.environ.get("SOVEREIGN_MASTER_PASSWORD", "SovereignAdmin2024")
vault_engine = SovereignHeritageCore(MASTER_KEY)

@app.route('/status', methods=['GET'])
def get_status():
    """Service Health & Branding Check."""
    return jsonify({
        "status": "online",
        "branding": "Sovereign Heritage Core",
        "descriptor": "Your Secure Personal Database",
        "version": "1.0.0",
        "encryption_standard": "AES-256-GCM",
        "heritage_protocol": "ENABLED"
    })

@app.route('/seal', methods=['POST'])
def seal_data():
    """
    Seals (Encrypts) sensitive text data.
    Expected Payload: {"payload": "your sensitive string"}
    """
    data = request.json
    if not data or 'payload' not in data:
        return jsonify({"error": "No payload provided"}), 400

    sealed_blob = vault_engine.seal_text(data['payload'])
    return jsonify({
        "status": "sealed",
        "blob": sealed_blob
    })

@app.route('/open', methods=['POST'])
def open_data():
    """
    Opens (Decrypts) a sealed blob.
    Expected Payload: {"blob": "encrypted_base64_string"}
    """
    data = request.json
    if not data or 'blob' not in data:
        return jsonify({"error": "No blob provided"}), 400

    plain_text = vault_engine.open_text(data['blob'])

    if "[DECRYPTION_ERROR]" in plain_text:
        return jsonify({"status": "failed", "error": "Decryption failed or data corrupt"}), 401

    return jsonify({
        "status": "opened",
        "payload": plain_text
    })

if __name__ == '__main__':
    # Running on Port 5002 to coexist with the Trading Engine on Port 5001.
    print("--- Sovereign Heritage Core Service Starting ---")
    print("Gateway: http://localhost:5002")
    app.run(host='0.0.0.0', port=5003, debug=False)