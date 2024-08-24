import tkinter as tk
from ui import KVMUI
from network import NetworkManager
from kvm_control import KVMControl

def main():
    root = tk.Tk()
    network_manager = NetworkManager()
    kvm_control = KVMControl()
    ui = KVMUI(root, network_manager, kvm_control)
    root.mainloop()

if __name__ == "__main__":
    main()
