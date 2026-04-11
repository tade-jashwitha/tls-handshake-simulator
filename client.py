import random
from encryption import encrypt_message, generate_session_key, get_cipher_suites


class Client:

    def __init__(self):
        self.client_random = format(random.randint(0, 2**32 - 1), "08x").upper()
        self.tls_version = "TLS 1.3"
        self.supported_ciphers = get_cipher_suites()
        self.session_id = None

    def client_hello(self):
        return {
            "random": self.client_random,
            "tls_version": self.tls_version,
            "cipher_suites": self.supported_ciphers,
            "extensions": ["server_name", "supported_groups", "signature_algorithms"],
        }

    def verify_certificate(self, certificate):
        trusted_issuers = ["DigiCert", "Let's Encrypt", "GlobalSign", "Comodo"]
        if certificate.issuer in trusted_issuers and certificate.is_valid():
            return True, f"Certificate verified — issued by {certificate.issuer}"
        elif certificate.issuer not in trusted_issuers:
            return False, f"Untrusted issuer: {certificate.issuer}"
        else:
            return False, "Certificate has expired"

    def generate_pre_master_secret(self):
        return format(random.randint(0, 2**32 - 1), "08x").upper() + \
               format(random.randint(0, 2**32 - 1), "08x").upper()

    def encrypt_pre_master(self, public_key, pre_master):
        return encrypt_message(public_key, pre_master)

    def generate_session_key(self, server_random, pre_master):
        return generate_session_key(
            self.client_random,
            server_random,
            pre_master
        )