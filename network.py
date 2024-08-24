import socket
import threading
import logging
import platform

class NetworkManager:
    def __init__(self):
        self.port = 5000
        self.ip = self.get_local_ip()
        self.connected = False
        self.server_socket = None
        self.client_socket = None

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def start_host(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(1)
        logging.info(f"Host started on {self.ip}:{self.port}")
        threading.Thread(target=self._accept_connection, daemon=True).start()

    def _accept_connection(self):
        while not self.connected:
            try:
                self.client_socket, addr = self.server_socket.accept()
                self.connected = True
                logging.info(f"Connected to client {addr}")
            except:
                pass

    def connect_to_host(self, host_ip):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((host_ip, self.port))
            self.connected = True
            logging.info(f"Connected to host {host_ip}:{self.port}")
        except:
            logging.error(f"Failed to connect to {host_ip}:{self.port}")

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        self.connected = False
        logging.info("Disconnected")

    def discover_hosts(self):
        hosts = []
        for i in range(1, 255):
            ip = f"{self.ip.rsplit('.', 1)[0]}.{i}"
            if ip != self.ip:
                try:
                    with socket.create_connection((ip, self.port), timeout=0.1):
                        hosts.append(ip)
                except:
                    pass
        return hosts