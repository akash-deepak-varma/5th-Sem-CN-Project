import socket
import ssl
import os

PORT = 12345
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"
DATA_DIR = "Data"  # Directory to store files

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

def handle_client(conn):
    print("Client connected")
    conn.send(b"Welcome to the SSL FTP Server!\n")
    
    while True:
        data = conn.recv(1024).decode()
        if not data:
            print("Client disconnected")
            break

        command = data.strip()
        print("Command received:", command)

        # Handle file upload
        if command.startswith("UPLOAD"):
            _, filename = command.split()
            filepath = os.path.join(DATA_DIR, filename)
            conn.send(b"READY")
            with open(filepath, "wb") as f:
                while True:
                    chunk = conn.recv(1024)
                    if chunk == b"EOF":
                        break
                    f.write(chunk)
            print(f"File {filename} uploaded successfully.")
            conn.send(b"UPLOAD SUCCESS\n")

        # Handle file download
        elif command.startswith("DOWNLOAD"):
            _, filename = command.split()
            filepath = os.path.join(DATA_DIR, filename)
            if os.path.exists(filepath):
                conn.send(b"READY")
                with open(filepath, "rb") as f:
                    while chunk := f.read(1024):
                        conn.send(chunk)
                conn.send(b"EOF")
                print(f"File {filename} sent to client.")
            else:
                conn.send(b"ERROR: File not found\n")

        # Handle file deletion
        elif command.startswith("DELETE"):
            _, filename = command.split()
            filepath = os.path.join(DATA_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                conn.send(b"DELETE SUCCESS\n")
                print(f"File {filename} deleted.")
            else:
                conn.send(b"ERROR: File not found\n")

        # Handle file renaming
        elif command.startswith("RENAME"):
            _, old_filename, new_filename = command.split()
            old_filepath = os.path.join(DATA_DIR, old_filename)
            new_filepath = os.path.join(DATA_DIR, new_filename)
            if os.path.exists(old_filepath):
                os.rename(old_filepath, new_filepath)
                conn.send(b"RENAME SUCCESS\n")
                print(f"File {old_filename} renamed to {new_filename}.")
            else:
                conn.send(b"ERROR: File not found\n")

        # Handle file moving
        elif command.startswith("MOVE"):
            _, filename, new_directory = command.split()
            filepath = os.path.join(DATA_DIR, filename)
            new_path = os.path.join(DATA_DIR, new_directory, filename)
            if os.path.exists(filepath):
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                os.rename(filepath, new_path)
                conn.send(b"MOVE SUCCESS\n")
                print(f"File {filename} moved to {new_directory}.")
            else:
                conn.send(b"ERROR: File not found\n")

        # Handle quit command
        elif command == "QUIT":
            print("Client requested to quit.")
            break
        
        else:
            conn.send(b"ERROR: Invalid command\n")
    
    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind(('', PORT))
        sock.listen(5)
        print(f"Server listening on port {PORT}...")
        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                conn, addr = ssock.accept()
                print(f"Connection established with {addr}")
                handle_client(conn)

if __name__ == "__main__":
    start_server()
