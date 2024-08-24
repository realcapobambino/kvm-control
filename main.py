import tkinter as tk
from tkinter import ttk
import socket
import threading
import random
import time
import struct
import hashlib
from pynput import mouse, keyboard

# Configuration
PORT_RANGE = (49152, 65535)  # Dynamic/private port range
MULTICAST_GROUP = '224.0.0.251'
MULTICAST_PORT = 5353
BUFFER_SIZE = 1024
DISCOVERY_TIMEOUT = 10
KEY_LENGTH = 32  # 256-bit key

class KVMControl:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cross-platform KVM Control")
        self.setup_ui()

        self.is_host = False
        self.active = False
        self.hosts = []
        self.selected_host = None
        self.port = random.randint(*PORT_RANGE)
        self.key = self.generate_key()

        self.mouse_listener = None
        self.keyboard_listener = None
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.sock = None

    def setup_ui(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.mode_var = tk.StringVar(value="client")
        ttk.Radiobutton(self.frame, text="Host", variable=self.mode_var, value="host", command=self.toggle_mode).grid(column=0, row=0, sticky=tk.W)
        ttk.Radiobutton(self.frame, text="Client", variable=self.mode_var, value="client", command=self.toggle_mode).grid(column=1, row=0, sticky=tk.W)

        self.host_frame = ttk.Frame(self.frame)
        self.host_frame.grid(column=0, row=1, columnspan=2, sticky=(tk.W, tk.E))

        self.host_listbox = tk.Listbox(self.host_frame, height=5)
        self.host_listbox.grid(column=0, row=0, sticky=(tk.W, tk.E))
        self.host_listbox.bind('<<ListboxSelect>>', self.on_host_select)

        self.refresh_button = ttk.Button(self.host_frame, text="Refresh", command=self.discover_hosts)
        self.refresh_button.grid(column=1, row=0, sticky=tk.W)

        self.status_label = ttk.Label(self.frame, text="Status: Not connected")
        self.status_label.grid(column=0, row=2, columnspan=2, sticky=(tk.W, tk.E))

        self.start_button = ttk.Button(self.frame, text="Start", command=self.start)
        self.start_button.grid(column=0, row=3, columnspan=2, sticky=(tk.W, tk.E))

    def toggle_mode(self):
        self.is_host = self.mode_var.get() == "host"
        self.host_frame.grid_remove() if self.is_host else self.host_frame.grid()

    def on_host_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.selected_host = self.hosts[selection[0]]

    def discover_hosts(self):
        self.hosts = []
        self.host_listbox.delete(0, tk.END)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(DISCOVERY_TIMEOUT)

        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', MULTICAST_PORT))
            mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            start_time = time.time()
            while time.time() - start_time < DISCOVERY_TIMEOUT:
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    if data.startswith(b'KVM_HOST'):
                        host_port = int(data.split(b':')[1])
                        self.hosts.append((addr[0], host_port))
                        self.host_listbox.insert(tk.END, f"{addr[0]}:{host_port}")
                except socket.timeout:
                    pass
        finally:
            sock.close()

    def broadcast_presence(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        message = f'KVM_HOST:{self.port}'.encode()
        while self.active:
            sock.sendto(message, (MULTICAST_GROUP, MULTICAST_PORT))
            time.sleep(1)

        sock.close()

    def generate_key(self):
        return hashlib.sha256(str(random.getrandbits(256)).encode()).digest()

    def encrypt(self, message):
        return bytes([message[i] ^ self.key[i % KEY_LENGTH] for i in range(len(message))])

    def decrypt(self, ciphertext):
        return bytes([ciphertext[i] ^ self.key[i % KEY_LENGTH] for i in range(len(ciphertext))])

    def start(self):
        if self.active:
            self.stop()
            return

        self.active = True
        self.start_button.config(text="Stop")

        if self.is_host:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(('0.0.0.0', self.port))
            self.sock.listen(1)
            self.status_label.config(text=f"Listening on port {self.port}")
            threading.Thread(target=self.broadcast_presence, daemon=True).start()
            threading.Thread(target=self.accept_connection, daemon=True).start()
        else:
            if not self.selected_host:
                self.status_label.config(text="Please select a host")
                return
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.selected_host)
            self.status_label.config(text=f"Connected to {self.selected_host[0]}:{self.selected_host[1]}")
            self.setup_listeners()

    def stop(self):
        self.active = False
        self.start_button.config(text="Start")
        self.status_label.config(text="Disconnected")
        if self.sock:
            self.sock.close()
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def accept_connection(self):
        conn, addr = self.sock.accept()
        self.status_label.config(text=f"Connected to {addr[0]}:{addr[1]}")
        self.setup_listeners()
        self.receive_events(conn)

    def setup_listeners(self):
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def on_move(self, x, y):
        if self.active and self.is_host:
            self.send_event(f"MOVE {x} {y}")

    def on_click(self, x, y, button, pressed):
        if self.active and self.is_host:
            self.send_event(f"CLICK {x} {y} {button} {pressed}")

    def on_scroll(self, x, y, dx, dy):
        if self.active and self.is_host:
            self.send_event(f"SCROLL {x} {y} {dx} {dy}")

    def on_press(self, key):
        if self.active and self.is_host:
            self.send_event(f"PRESS {key}")

    def on_release(self, key):
        if self.active and self.is_host:
            self.send_event(f"RELEASE {key}")

    def send_event(self, event):
        if self.sock:
            encrypted_event = self.encrypt(event.encode())
            self.sock.sendall(encrypted_event)

    def receive_events(self, conn):
        while self.active:
            try:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                decrypted_data = self.decrypt(data)
                self.process_event(decrypted_data.decode())
            except Exception as e:
                print(f"Error receiving event: {e}")
                break
        self.stop()

    def process_event(self, event):
        parts = event.split()
        if parts[0] == "MOVE":
            self.mouse_controller.position = (int(parts[1]), int(parts[2]))
        elif parts[0] == "CLICK":
            button = getattr(mouse.Button, parts[3])
            if parts[4] == "True":
                self.mouse_controller.press(button)
            else:
                self.mouse_controller.release(button)
        elif parts[0] == "SCROLL":
            self.mouse_controller.scroll(int(parts[3]), int(parts[4]))
        elif parts[0] == "PRESS":
            key = keyboard.KeyCode.from_char(parts[1]) if len(parts[1]) == 1 else getattr(keyboard.Key, parts[1])
            self.keyboard_controller.press(key)
        elif parts[0] == "RELEASE":
            key = keyboard.KeyCode.from_char(parts[1]) if len(parts[1]) == 1 else getattr(keyboard.Key, parts[1])
            self.keyboard_controller.release(key)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    kvm = KVMControl()
    kvm.run()