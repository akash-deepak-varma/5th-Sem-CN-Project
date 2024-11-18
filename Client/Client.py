import socket
import ssl
import os

SERVER_IP = "127.0.0.1"
PORT = 12345
CERT_FILE = "cert.pem"

context = ssl.create_default_context()
context.load_verify_locations(CERT_FILE)

# For testing purposes only:
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

def start_client():
    with socket.create_connection((SERVER_IP, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=SERVER_IP) as ssock:
            print(ssock.recv(1024).decode())  # Welcome message from server

            while True:
                print("\nOptions:")
                print("1. Upload a file")
                print("2. Download a file")
                print("3. Delete a file")
                print("4. Rename a file")
                print("5. Move a file")
                print("6. Quit")
                choice = input("Enter your choice: ").strip()

                if choice == "1":  # Upload a file
                    filepath = input("Enter the file path to upload: ").strip()
                    if not os.path.exists(filepath):
                        print("File does not exist!")
                        continue
                    filename = os.path.basename(filepath)
                    ssock.send(f"UPLOAD {filename}".encode())
                    response = ssock.recv(1024).decode()
                    if response == "READY":
                        with open(filepath, "rb") as f:
                            while chunk := f.read(1024):
                                ssock.send(chunk)
                        ssock.send(b"EOF")
                        print(ssock.recv(1024).decode())
                    else:
                        print(response)

                elif choice == "2":  # Download a file
                    filename = input("Enter the filename to download: ").strip()
                    ssock.send(f"DOWNLOAD {filename}".encode())
                    response = ssock.recv(1024).decode()
                    if response == "READY":
                        with open(filename, "wb") as f:
                            while True:
                                chunk = ssock.recv(1024)
                                if chunk == b"EOF":
                                    break
                                f.write(chunk)
                        print(f"File {filename} downloaded successfully.")
                    else:
                        print(response)

                elif choice == "3":  # Delete a file
                    filename = input("Enter the filename to delete: ").strip()
                    ssock.send(f"DELETE {filename}".encode())
                    print(ssock.recv(1024).decode())

                elif choice == "4":  # Rename a file
                    old_filename = input("Enter the current filename: ").strip()
                    new_filename = input("Enter the new filename: ").strip()
                    ssock.send(f"RENAME {old_filename} {new_filename}".encode())
                    print(ssock.recv(1024).decode())

                elif choice == "5":  # Move a file
                    filename = input("Enter the filename to move: ").strip()
                    new_directory = input("Enter the destination directory: ").strip()
                    ssock.send(f"MOVE {filename} {new_directory}".encode())
                    print(ssock.recv(1024).decode())

                elif choice == "6":  # Quit
                    ssock.send(b"QUIT")
                    print("Disconnected from server.")
                    break
                else:
                    print("Invalid choice. Try again.")

if __name__ == "__main__":
    start_client()
