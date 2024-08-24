from ui import KVMUI
from network import NetworkManager
from kvm_control import KVMControl
import tkinter as tk
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    network_manager = NetworkManager()
    kvm_control = KVMControl()
    ui = KVMUI(root, network_manager, kvm_control)
    ui.run()

if __name__ == "__main__":
    main()