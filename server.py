import random
from encryption import generate_keys, decrypt_message, generate_session_key, get_cipher_suites
from certificate import Certificate


class Server:

    def __init__(self, domain="example.com", issuer="DigiCert"):
        self.private_key, self.public_key = generate_keys()
        self.server_random = format(random.randint(0, 2**32 - 1), "08x").upper()
        self.tls_version = "TLS 1.3"
        self.supported_ciphers = get_cipher_suites()
        self.certificate = Certificate(domain, issuer, self.public_key)

    def server_hello(self, client_hello):
        # Negotiate cipher suite — pick first client suite we support
        negotiated = None
        for suite in client_hello.get("cipher_suites", []):
            if suite in self.supported_ciphers:
                negotiated = suite
                break
        self.negotiated_cipher = negotiated or self.supported_ciphers[0]
        return {
            "random": self.server_random,
            "tls_version": self.tls_version,
            "selected_cipher": self.negotiated_cipher,
            "session_id": format(random.randint(0, 2**32 - 1), "08x").upper(),
        }

    def send_certificate(self):
        return self.certificate

    def decrypt_pre_master(self, encrypted_secret):
        return decrypt_message(self.private_key, encrypted_secret)

    def generate_session_key(self, client_random, pre_master):
        return generate_session_key(
            client_random,
            self.server_random,
            pre_master
        )