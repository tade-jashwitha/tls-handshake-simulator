class Certificate:

    def __init__(self, domain, issuer, public_key):
        self.domain = domain
        self.issuer = issuer
        self.public_key = public_key

    def display(self):

        print("Certificate Information")
        print("Domain:", self.domain)
        print("Issuer:", self.issuer)