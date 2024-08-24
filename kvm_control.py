# kvm_control.py
from pynput import mouse, keyboard
import threading
import logging

class KVMControl:
    def __init__(self):
        self.shortcut = None
        self.active = False
        self.listener_thread = None
        self.stop_event = threading.Event()

    def set_shortcut(self, shortcut):
        self.shortcut = shortcut

    def toggle_control(self):
        self.active = not self.active
        logging.info(f"KVM Control {'enabled' if self.active else 'disabled'}")

    def start_listening(self):
        def listen():
            with keyboard.Listener(on_press=self.process_event) as k_listener, \
                    mouse.Listener(on_click=self.process_event) as m_listener:
                k_listener.join()
                m_listener.join()

        self.listener_thread = threading.Thread(target=listen, daemon=True)
        self.listener_thread.start()
        logging.info("Started listening for keyboard and mouse events.")

    def send_event(self, event):
        # Serialize and send the event over the network
        logging.debug(f"Sending event: {event}")

    def process_event(self, event):
        # Process received event or local event
        logging.debug(f"Processing event: {event}")
        if self.active:
            self.send_event(event)

    def stop_listening(self):
        self.stop_event.set()
        logging.info("Stopped listening for events.")
