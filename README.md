#  TLS Handshake Simulation

##  Project Overview

This project is a **simulation of the SSL/TLS Handshake Protocol**, demonstrating how a secure connection is established between a client (browser) and a server.

The simulation visually represents the **step-by-step TLS handshake process**, including message exchange, certificate verification, and session key generation.



##  Objectives

* Understand how secure communication works over the internet
* Learn the TLS handshake process
* Simulate client-server authentication
* Demonstrate secure key exchange
* Visualize session key generation



## Key Concepts Covered

* SSL vs TLS
* Client-Server Architecture
* Public Key Cryptography (RSA)
* Symmetric Encryption
* Digital Certificates
* Hash Functions (SHA-256)
* Session Key Generation



## TLS Handshake Process (Simulated)

1. **Client Hello**
   Client sends supported cipher suites and a random number

2. **Server Hello**
   Server responds with selected cipher suite and its random number

3. **Certificate Exchange**
   Server sends its digital certificate

4. **Certificate Verification**
   Client verifies the authenticity of the certificate

5. **Pre-Master Secret Exchange**
   Client generates a secret and encrypts it using server’s public key

6. **Session Key Generation**
   Both client and server compute the same session key

7. **Secure Communication**
   Encrypted communication begins



## Project Structure

```
tls_handshake_simulation
│
├── app.py                  # Flask backend
├── client.py               # Client simulation
├── server.py               # Server simulation
├── encryption.py           # Cryptographic functions
├── certificate.py          # Certificate handling
│
├── templates/
│   └── index.html          # Frontend UI
│
└── static/
    ├── style.css           # Styling
    └── script.js           # Frontend logic
```



## Technologies Used

* **Python** (Flask)
* **HTML, CSS, JavaScript**
* **Cryptography Library**
* **Hashlib (SHA-256)**



## How to Run the Project

### Clone the Repository

```
git clone https://github.com/your-username/tls-handshake-simulation.git
cd tls-handshake-simulation
```

### Create Virtual Environment (optional but recommended)

```
python -m venv .venv
.venv\Scripts\activate
```

### Install Dependencies

```
pip install flask cryptography
```

### Run the Application

```
python app.py
```

### Open in Browser

```
http://127.0.0.1:5000
```



## How It Works

1. Click **Start Handshake**
2. Frontend sends request to Flask backend (`/simulate`)
3. Backend simulates TLS handshake
4. Steps are returned as JSON
5. Frontend displays:

   * Packet movement between client & server
   * Step-by-step handshake progress



## Features

* Client-Server Communication Simulation
* Step-by-step TLS Handshake Visualization
* Packet Movement Animation
* Handshake Timeline Display
* Secure Session Indication



## Output

The simulation shows:

* Client → Server communication
* Certificate verification
* Secure key exchange
* Session key generation
* Secure TLS session establishment



## Applications

* Secure Web Browsing (HTTPS)
* Online Banking
* Secure Email Communication
* VPN Connections
* Cloud Security



## Future Enhancements

* Add real-time encryption/decryption visualization
* Support multiple cipher suites
* Add graphical animations (arrows, locks)
* Implement real socket-based communication
* Add user interaction controls



## 📄 License

This project is for educational purposes only.
