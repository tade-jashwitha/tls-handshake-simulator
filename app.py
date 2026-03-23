from flask import Flask, render_template, jsonify
from client import Client
from server import Server
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/simulate")
def simulate():
    steps = []

    client = Client()
    server = Server()

    # Client Hello
    client_random = client.client_hello()
    steps.append({
        "text": "Client → Client Hello",
        "info": "Client sends supported encryption methods and its random number.",
        "rsa_details": {
            "Client Random": client_random
        }
    })

    # Server Hello
    server_random = server.server_hello()
    steps.append({
        "text": "Server → Server Hello",
        "info": "Server selects encryption method and sends its random number.",
        "rsa_details": {
            "Server Random": server_random
        }
    })

    # Certificate
    certificate = server.send_certificate()
    pub_key_pem = certificate.public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    steps.append({
        "text": "Server → Sending Certificate",
        "info": "Server sends SSL certificate containing its 2048-bit RSA Public Key.",
        "rsa_details": {
            "RSA Public Key": pub_key_pem
        }
    })

    # Verification
    verified = client.verify_certificate(certificate)
    steps.append({
        "text": "Client → Verifying Certificate",
        "info": "Client verifies the certificate's authenticity.",
        "rsa_details": None
    })

    if not verified:
        steps.append({"text": "Handshake Failed", "info": "Certificate invalid.", "rsa_details": None})
        return jsonify(steps)

    # Pre master secret
    pre_master = client.generate_pre_master_secret()
    encrypted_secret = client.encrypt_pre_master(
        certificate.public_key, pre_master
    )
    steps.append({
        "text": "Client → Sending Pre-Master Secret",
        "info": "Client generates a secret key and encrypts it using the Server's RSA Public Key.",
        "rsa_details": {
            "Original Pre-Master Secret": pre_master,
            "Encrypted Pre-Master (Hex)": encrypted_secret.hex()
        }
    })

    # Server decrypt
    server_pre_master = server.decrypt_pre_master(encrypted_secret)

    # Session key
    client_session = client.generate_session_key(server_random, pre_master)
    server_session = server.generate_session_key(client_random, server_pre_master)

    # Check if session keys match
    if client_session != server_session:
        steps.append({"text": "Handshake Failed: Session keys do not match", "info": "Decryption failed.", "rsa_details": None})
        return jsonify(steps)

    steps.append({
        "text": "Client → Session Key Generated",
        "info": "Client derives the shared session key.",
        "rsa_details": {
            "Client Session Key": client_session
        }
    })
    
    steps.append({
        "text": "Server → Session Key Generated",
        "info": "Server derives the identically shared session key.",
        "rsa_details": {
            "Server Session Key": server_session
        }
    })

    steps.append({
        "text": "Secure TLS Session Established",
        "info": "Secure encrypted communication can now begin.",
        "rsa_details": None
    })

    return jsonify(steps)

if __name__ == "__main__":
    app.run(debug=True)