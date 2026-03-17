from flask import Flask, render_template, jsonify
from client import Client
from server import Server

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
    steps.append("Client → Client Hello")

    # Server Hello
    server_random = server.server_hello()
    steps.append("Server → Server Hello")

    # Certificate
    certificate = server.send_certificate()
    steps.append("Server → Sending Certificate")

    # Verification
    verified = client.verify_certificate(certificate)
    steps.append("Client → Verifying Certificate")

    if not verified:
        steps.append("Handshake Failed")
        return jsonify(steps)

    # Pre master secret
    pre_master = client.generate_pre_master_secret()
    encrypted_secret = client.encrypt_pre_master(
        certificate.public_key, pre_master
    )
    steps.append("Client → Sending Pre-Master Secret")

    # Server decrypt
    server_pre_master = server.decrypt_pre_master(encrypted_secret)

    # Session key
    client_session = client.generate_session_key(server_random, pre_master)
    server_session = server.generate_session_key(client_random, server_pre_master)

    # Check if session keys match
    if client_session != server_session:
        steps.append("Handshake Failed: Session keys do not match")
        return jsonify(steps)

    steps.append("Client → Session Key Generated")
    steps.append("Server → Session Key Generated")

    steps.append("Secure TLS Session Established")

    return jsonify(steps)

if __name__ == "__main__":
    app.run(debug=True)