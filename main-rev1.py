import socket
import threading
from pynput import mouse, keyboard

# Configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 5273  # Choose an available port
SWITCH_KEY = keyboard.Key.f12  # Key to switch between systems

class KVMControl:
    def __init__(self, is_host):
        self.is_host = is_host
        self.active = True
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        if self.is_host:
            self.sock.bind((HOST, PORT))
            self.sock.listen(1)
            print(f"Listening on {HOST}:{PORT}")
            self.conn, addr = self.sock.accept()
            print(f"Connected by {addr}")
        else:
            self.sock.connect((HOST, PORT))
            print(f"Connected to {HOST}:{PORT}")

        self.mouse_listener.start()
        self.keyboard_listener.start()
        threading.Thread(target=self.receive_events, daemon=True).start()

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
        if key == SWITCH_KEY:
            self.active = not self.active
            print(f"{'Activated' if self.active else 'Deactivated'} KVM control")
        elif self.active and self.is_host:
            self.send_event(f"PRESS {key}")

    def on_release(self, key):
        if self.active and self.is_host:
            self.send_event(f"RELEASE {key}")

    def send_event(self, event):
        if self.is_host:
            self.conn.sendall(event.encode())
        else:
            self.sock.sendall(event.encode())

    def receive_events(self):
        while True:
            data = self.conn.recv(1024) if self.is_host else self.sock.recv(1024)
            if not data:
                break
            self.process_event(data.decode())

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

if __name__ == "__main__":
    is_host = input("Is this the host system? (y/n): ").lower() == 'y'
    kvm = KVMControl(is_host)
    kvm.start()

    print("KVM control active. Press F12 to toggle control.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting...")