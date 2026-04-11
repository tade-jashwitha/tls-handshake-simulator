from flask import Flask, render_template, jsonify, request
from client import Client
from server import Server
from certificate import Certificate
from encryption import generate_keys
import hashlib
import datetime

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/simulate")
def simulate():
    issuer = request.args.get("issuer", "DigiCert")
    steps = []

    client = Client()
    server = Server(domain="example.com", issuer=issuer)

    # ── Step 1: Client Hello ──────────────────────────────────────────────────
    client_hello = client.client_hello()
    steps.append({
        "id": 1,
        "title": "Client Hello",
        "direction": "client_to_server",
        "status": "success",
        "description": "Client initiates handshake, advertising capabilities.",
        "packet": {
            "TLS Version": client_hello["tls_version"],
            "Client Random": client_hello["random"],
            "Cipher Suites": ", ".join(client_hello["cipher_suites"]),
            "Extensions": ", ".join(client_hello["extensions"]),
        }
    })

    # ── Step 2: Server Hello ──────────────────────────────────────────────────
    server_hello = server.server_hello(client_hello)
    steps.append({
        "id": 2,
        "title": "Server Hello",
        "direction": "server_to_client",
        "status": "success",
        "description": "Server confirms TLS version and selects cipher suite.",
        "packet": {
            "TLS Version": server_hello["tls_version"],
            "Server Random": server_hello["random"],
            "Selected Cipher": server_hello["selected_cipher"],
            "Session ID": server_hello["session_id"],
        }
    })

    # ── Step 3: Certificate ───────────────────────────────────────────────────
    certificate = server.send_certificate()
    cert_dict = certificate.to_dict()
    steps.append({
        "id": 3,
        "title": "Certificate",
        "direction": "server_to_client",
        "status": "success",
        "description": "Server presents its X.509 digital certificate.",
        "packet": {
            "Subject": cert_dict["domain"],
            "Issuer": cert_dict["issuer"],
            "Serial": cert_dict["serial_number"],
            "Valid Until": cert_dict["expires_at"],
            "Algorithm": cert_dict["signature_algorithm"],
            "Key Size": f"{cert_dict['key_size']} bits",
            "Fingerprint": cert_dict["fingerprint"],
        }
    })

    # ── Step 4: Certificate Verification ─────────────────────────────────────
    verified, verify_msg = client.verify_certificate(certificate)
    steps.append({
        "id": 4,
        "title": "Certificate Verification",
        "direction": "client_internal",
        "status": "success" if verified else "error",
        "description": verify_msg,
        "packet": {
            "Issuer Trust": "✓ Trusted CA" if verified else "✗ Untrusted CA",
            "Validity Period": "✓ Valid" if certificate.is_valid() else "✗ Expired",
            "Domain Match": "✓ example.com",
            "Signature": "✓ RSA-SHA256 verified" if verified else "✗ Failed",
        }
    })

    if not verified:
        steps.append({
            "id": 5,
            "title": "Handshake Failed",
            "direction": "client_internal",
            "status": "error",
            "description": "TLS Alert: Certificate Unknown (42). Connection terminated.",
            "packet": {"Alert Level": "Fatal", "Alert Code": "42", "Reason": verify_msg}
        })
        return jsonify({"steps": steps, "success": False})

    # ── Step 5: Pre-Master Secret ─────────────────────────────────────────────
    pre_master = client.generate_pre_master_secret()
    encrypted_secret = client.encrypt_pre_master(certificate.public_key, pre_master)
    encrypted_hex = encrypted_secret.hex()[:32] + "..."
    steps.append({
        "id": 5,
        "title": "Pre-Master Secret",
        "direction": "client_to_server",
        "status": "success",
        "description": "Client generates a random pre-master secret and encrypts it with the server's public key (RSA-OAEP).",
        "packet": {
            "Pre-Master Secret": pre_master[:8] + "..." + pre_master[-4:],
            "Encrypted (hex)": encrypted_hex,
            "Encryption": "RSA-OAEP / SHA-256",
            "Key Used": "Server Public Key",
        }
    })

    # ── Step 6: Server Decrypts ───────────────────────────────────────────────
    server_pre_master = server.decrypt_pre_master(encrypted_secret)
    steps.append({
        "id": 6,
        "title": "Decrypt Pre-Master Secret",
        "direction": "server_internal",
        "status": "success",
        "description": "Server uses its private key to decrypt the pre-master secret.",
        "packet": {
            "Decryption Key": "Server Private Key",
            "Algorithm": "RSA-OAEP / SHA-256",
            "Result": "✓ Decryption successful",
            "Pre-Master (first 8)": server_pre_master[:8] + "...",
        }
    })

    # ── Step 7: Session Keys ──────────────────────────────────────────────────
    client_session = client.generate_session_key(server_hello["random"], pre_master)
    server_session = server.generate_session_key(client_hello["random"], server_pre_master)

    keys_match = client_session == server_session
    steps.append({
        "id": 7,
        "title": "Session Key Derivation",
        "direction": "both_internal",
        "status": "success" if keys_match else "error",
        "description": "Both sides independently derive the same session key using the pre-master secret and random values.",
        "packet": {
            "Client Random": client_hello["random"],
            "Server Random": server_hello["random"],
            "Pre-Master": pre_master[:8] + "...",
            "Algorithm": "HMAC-SHA256 PRF",
            "Session Key (preview)": client_session[:16] + "...",
            "Keys Match": "✓ Yes — secure channel ready" if keys_match else "✗ Mismatch — handshake failed",
        }
    })

    if not keys_match:
        return jsonify({"steps": steps, "success": False})

    # ── Step 8: Finished ──────────────────────────────────────────────────────
    steps.append({
        "id": 8,
        "title": "Handshake Complete",
        "direction": "both",
        "status": "success",
        "description": "TLS handshake successful. Encrypted application data can now be exchanged.",
        "packet": {
            "Cipher": server_hello["selected_cipher"],
            "Session Key": client_session[:16] + "...",
            "Status": "✓ Secure channel established",
            "Protection": "Confidentiality + Integrity + Authentication",
        }
    })

    return jsonify({"steps": steps, "success": True})


@app.route("/certificate")
def certificate_page():
    return render_template("certificate.html")


@app.route("/api/certificate")
def api_certificate():
    domain   = request.args.get("domain", "example.com")
    issuer   = request.args.get("issuer", "DigiCert")
    org      = request.args.get("org", "Example Corp Ltd.")
    validity = int(request.args.get("validity", 365))

    _, public_key = generate_keys()
    cert = Certificate(domain, issuer, public_key, validity_days=validity)
    data = cert.to_dict()

    data["org"] = org
    data["country"] = "US"
    data["san"] = [domain, f"www.{domain}"]
    data["key_usage"] = ["Digital Signature", "Key Encipherment", "Certificate Sign"]
    data["ext_key_usage"] = ["TLS Web Server Authentication", "TLS Web Client Authentication"]
    data["ocsp_url"] = f"http://ocsp.{issuer.lower().replace(' ', '')}.com"
    data["ca_issuers"] = f"http://cacerts.{issuer.lower().replace(' ', '')}.com/root.crt"
    data["crl_url"] = f"http://crl.{issuer.lower().replace(' ', '')}.com/latest.crl"
    data["public_key_hex"] = "30:82:01:0a:02:82:01:01:00:d1:4e:2f:9a:c3:7a:91:b2:4f:88:02:03:01:00:01"

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)