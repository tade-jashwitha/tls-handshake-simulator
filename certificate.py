import hashlib
import datetime


class Certificate:

    def __init__(self, domain, issuer, public_key, validity_days=365):
        self.domain = domain
        self.issuer = issuer
        self.public_key = public_key
        self.issued_at = datetime.datetime.utcnow()
        self.expires_at = self.issued_at + datetime.timedelta(days=validity_days)
        self.serial_number = hashlib.sha1(
            (domain + issuer + str(self.issued_at)).encode()
        ).hexdigest()[:16].upper()
        self.signature_algorithm = "SHA256WithRSAEncryption"
        self.key_size = 2048

    def get_fingerprint(self):
        data = f"{self.domain}{self.issuer}{self.serial_number}"
        return ":".join(
            hashlib.sha256(data.encode()).hexdigest()[i:i+2].upper()
            for i in range(0, 20, 2)
        )

    def is_valid(self):
        now = datetime.datetime.utcnow()
        return self.issued_at <= now <= self.expires_at

    def to_dict(self):
        return {
            "domain": self.domain,
            "issuer": self.issuer,
            "serial_number": self.serial_number,
            "issued_at": self.issued_at.strftime("%Y-%m-%d %H:%M UTC"),
            "expires_at": self.expires_at.strftime("%Y-%m-%d %H:%M UTC"),
            "signature_algorithm": self.signature_algorithm,
            "key_size": self.key_size,
            "fingerprint": self.get_fingerprint(),
            "valid": self.is_valid(),
        }

    def display(self):
        print("Certificate Information")
        print(f"  Domain : {self.domain}")
        print(f"  Issuer : {self.issuer}")
        print(f"  Serial : {self.serial_number}")
        print(f"  Expires: {self.expires_at}")