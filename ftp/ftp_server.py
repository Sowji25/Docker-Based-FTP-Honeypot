from sqlalchemy import insert
from database.db import engine
from database.models import credentials

import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"
PORT = 2121


def handle_client(conn, addr):
    print(f"[+] FTP Connection from {addr}")

    conn.send(b"220 Fake FTP Server Ready\r\n")

    username = ""

    while True:
        try:
            data = conn.recv(1024).decode(errors="ignore").replace("\r", "").replace("\n", "")

            if not data:
                break

            print("Received:", repr(data))

            log = f"{datetime.now()} | {addr[0]} | {data}"

            print(log)

            with open("/app/ftp_logs.txt", "a") as f:
                f.write(log + "\n")

            if data.upper().startswith("USER"):
                parts = data.split(" ", 1)
                if len(parts) > 1:
                    username = parts[1]

                conn.send(b"331 Username OK, need password\r\n")

            elif data.upper().startswith("PASS"):
                parts = data.split(" ", 1)
                password = ""

                if len(parts) > 1:
                    password = parts[1]

                print(f"[+] Username : {username}")
                print(f"[+] Password : {password}")

                try:
                    with engine.begin() as connection:
                        connection.execute(
                            insert(credentials).values(
                                username=username,
                                password=password,
                                ip_address=addr[0],
                                login_time=str(datetime.now())
                            )
                        )

                    print("[+] Credentials saved to PostgreSQL")

                except Exception as db_error:
                    print("[!] Database Error:", db_error)

                conn.send(b"530 Login incorrect\r\n")

            elif data.upper() == "QUIT":
                conn.send(b"221 Goodbye\r\n")
                break

            else:
                conn.send(b"500 Unknown command\r\n")

        except Exception as e:
            print("[!] Error:", e)
            break

    print(f"[-] Connection Closed: {addr}")
    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen(5)

    print("=" * 40)
    print(" Fake FTP Honeypot Running on Port 2121")
    print("=" * 40)

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        )
        thread.start()


if __name__ == "__main__":
    start_server()