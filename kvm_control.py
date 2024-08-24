# kvm_control.py
import threading
import logging
from pynput import mouse, keyboard

class KVMControl:
    def __init__(self):
        self.shortcut = None
        self.active = False
        self.stop_event = threading.Event()

    def set_shortcut(self, shortcut):
        self.shortcut = shortcut

    def toggle_control(self):
        self.active = not self.active
        logging.info(f"KVM Control {'enabled' if self.active else 'disabled'}")

    def start_listening(self):
        def on_press(key):
            self.process_event(('key_press', key))

        def on_release(key):
            self.process_event(('key_release', key))

        def on_move(x, y):
            self.process_event(('mouse_move', x, y))

        def on_click(x, y, button, pressed):
            self.process_event(('mouse_click', x, y, button, pressed))

        def on_scroll(x, y, dx, dy):
            self.process_event(('mouse_scroll', x, y, dx, dy))

        self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop_listening(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

    def process_event(self, event):
        # Process received event or local event
        # logging.debug(f"Processing event: {event}")
        if self.active:
            self.send_event(event)
            logging.debug(f"Processing event: {event}")

    def send_event(self, event):
        # Serialize and send the event over the network
        logging.debug(f"Sending event: {event}")
