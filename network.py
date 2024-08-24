import socket
import netifaces
import threading
import logging

import platform

if platform.system() == "Windows":
    import winreg


class NetworkManager:
    def __init__(self):
        self.port = 0
        self.broadcast_name = "default kvm"
        self.interface = None

    def get_interfaces(self):
        interfaces = netifaces.interfaces()
        if platform.system() == "Windows":
            interfaces = [self._get_windows_friendly_name(iface) for iface in interfaces]
        return interfaces

    def _get_windows_friendly_name(self, iface):
        # Convert GUID to a user-friendly interface name in Windows
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"SYSTEM\\CurrentControlSet\\Control\\Network\\{iface}\\Connection")
            name, _ = winreg.QueryValueEx(key, "Name")
            return name
        except Exception as e:
            return iface  # Fallback to the original name if something fails

    def set_interface(self, interface):
        self.interface = interface

    def set_port(self, port):
        self.port = int(port) if port else 0

    def set_broadcast_name(self, name):
        self.broadcast_name = name

    def discover_hosts(self):
        # Send a UDP broadcast to discover hosts
        broadcast_message = f"DISCOVER_KVM:{self.broadcast_name}"
        self.hosts = []

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(2)  # Timeout for receiving responses
            sock.sendto(broadcast_message.encode(), ('<broadcast>', self.broadcast_port))

            try:
                while True:
                    data, addr = sock.recvfrom(self.buffer_size)
                    if data:
                        host_info = data.decode()
                        logging.info(f"Discovered host: {host_info} at {addr[0]}")
                        self.hosts.append((host_info, addr[0]))
            except socket.timeout:
                logging.info("Host discovery completed.")

        return [f"{name} ({ip})" for name, ip in self.hosts]

    def start_host(self):
        # Start the host server to listen for incoming connections
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host_ip, self.port))
        self.server_socket.listen(1)
        logging.info(f"Host server started on {self.host_ip}:{self.port}")

        def handle_client_connection(client_socket):
            try:
                while True:
                    data = client_socket.recv(self.buffer_size)
                    if not data:
                        break
                    # Process incoming data
                    logging.debug(f"Received data: {data.decode()}")
            finally:
                client_socket.close()

        def accept_connections():
            while True:
                client_socket, addr = self.server_socket.accept()
                logging.info(f"Connection accepted from {addr}")
                threading.Thread(target=handle_client_connection, args=(client_socket,), daemon=True).start()

        threading.Thread(target=accept_connections, daemon=True).start()

    def connect_to_host(self, host):
        # Connect to the selected host
        host_ip = host.split('(')[-1][:-1]
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host_ip, self.port))
        logging.info(f"Connected to host {host_ip}:{self.port}")

    def p2p_connect(self):
        # Implement P2P connection logic here
        pass
