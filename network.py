import socket
import netifaces
import logging
import platform

if platform.system() == "Windows":
    import winreg

class NetworkManager:
    def __init__(self):
        self.port = 5000  # Default port
        self.broadcast_name = "default kvm"
        self.interface = None
        self.buffer_size = 1024

    def get_interfaces(self):
        interfaces = netifaces.interfaces()
        if platform.system() == "Windows":
            return [self._get_windows_friendly_name(iface) for iface in interfaces]
        return interfaces

    def _get_windows_friendly_name(self, iface):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"SYSTEM\\CurrentControlSet\\Control\\Network\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{iface}\\Connection")
            name, _ = winreg.QueryValueEx(key, "Name")
            return name
        except:
            return iface

    def set_interface(self, interface):
        self.interface = interface

    def set_port(self, port):
        self.port = int(port) if port else 5000

    def set_broadcast_name(self, name):
        self.broadcast_name = name

    def discover_hosts(self):
        broadcast_message = f"DISCOVER_KVM:{self.broadcast_name}"
        hosts = []

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(2)
            sock.sendto(broadcast_message.encode(), ('<broadcast>', self.port))

            try:
                while True:
                    data, addr = sock.recvfrom(self.buffer_size)
                    if data:
                        host_info = data.decode()
                        logging.info(f"Discovered host: {host_info} at {addr[0]}")
                        hosts.append(f"{host_info} ({addr[0]})")
            except socket.timeout:
                logging.info("Host discovery completed.")

        return hosts

    def start_host(self):
        host_ip = self._get_host_ip()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host_ip, self.port))
        self.server_socket.listen(1)
        logging.info(f"Host server started on {host_ip}:{self.port}")

    def connect_to_host(self, host):
        host_ip = host.split('(')[-1][:-1]
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host_ip, self.port))
        logging.info(f"Connected to host {host_ip}:{self.port}")

    def _get_host_ip(self):
        if self.interface:
            return netifaces.ifaddresses(self.interface)[netifaces.AF_INET][0]['addr']
        return socket.gethostbyname(socket.gethostname())

    def p2p_connect(self):
        # Implement P2P connection logic here
        pass