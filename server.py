import random
from encryption import generate_keys, decrypt_message, generate_session_key
from certificate import Certificate


class Server:

    def __init__(self):

        self.private_key, self.public_key = generate_keys()

        self.server_random = str(random.randint(100000,999999))

        self.certificate = Certificate(
            "example.com",
            "DigiCert",
            self.public_key
        )


    def server_hello(self):

        print("Server: Sending Server Hello")

        return self.server_random


    def send_certificate(self):

        print("Server: Sending Certificate")

        self.certificate.display()

        return self.certificate


    def decrypt_pre_master(self, encrypted_secret):

        print("Server: Decrypting Pre-Master Secret")

        pre_master = decrypt_message(self.private_key, encrypted_secret)

        return pre_master


    def generate_session_key(self, client_random, pre_master):

        print("Server: Generating Session Key")

        session_key = generate_session_key(
            client_random,
            self.server_random,
            pre_master
        )

        return session_key