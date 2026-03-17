import random
from encryption import encrypt_message, generate_session_key


class Client:

    def __init__(self):
        self.client_random = str(random.randint(100000, 999999))


    def client_hello(self):
        print("Client: Sending Client Hello")
        return self.client_random


    def verify_certificate(self, certificate):
        print("Client: Verifying Certificate")

        if certificate.issuer == "DigiCert":
            print("Client: Certificate Verified")
            return True
        else:
            print("Client: Certificate Invalid")
            return False


    def generate_pre_master_secret(self):
        print("Client: Generating Pre-Master Secret")
        return str(random.randint(1000000, 9999999))


    def encrypt_pre_master(self, public_key, pre_master):
        print("Client: Encrypting Pre-Master Secret")
        return encrypt_message(public_key, pre_master)


    def generate_session_key(self, server_random, pre_master):
        print("Client: Generating Session Key")

        return generate_session_key(
            self.client_random,
            server_random,
            pre_master
        )