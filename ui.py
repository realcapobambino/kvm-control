# ui.py
import tkinter as tk
from tkinter import ttk

class KVMUI:
    def __init__(self, root, network_manager, kvm_control):
        self.root = root
        self.network_manager = network_manager
        self.kvm_control = kvm_control
        self.setup_ui()

    def setup_ui(self):
        self.root.title("KVM Control")

        # Interface selection
        ttk.Label(self.root, text="Network Interface:").pack()
        self.interface_var = tk.StringVar()
        self.interface_dropdown = ttk.Combobox(self.root, textvariable=self.interface_var)
        self.interface_dropdown['values'] = self.network_manager.get_interfaces()
        self.interface_dropdown.pack()

        # Port entry
        ttk.Label(self.root, text="Port (0 for random):").pack()
        self.port_entry = ttk.Entry(self.root)
        self.port_entry.pack()

        # Broadcast name entry
        ttk.Label(self.root, text="Broadcast Name:").pack()
        self.broadcast_entry = ttk.Entry(self.root)
        self.broadcast_entry.insert(0, self.network_manager.broadcast_name)
        self.broadcast_entry.pack()

        # KVM switch shortcut
        ttk.Label(self.root, text="KVM Switch Shortcut:").pack()
        self.shortcut_entry = ttk.Entry(self.root)
        self.shortcut_entry.pack()

        # Host/Client mode selection
        self.mode_var = tk.StringVar(value="client")
        ttk.Radiobutton(self.root, text="Host", variable=self.mode_var, value="host").pack()
        ttk.Radiobutton(self.root, text="Client", variable=self.mode_var, value="client").pack()

        # Action buttons
        ttk.Button(self.root, text="Start", command=self.start).pack()
        ttk.Button(self.root, text="Discover Hosts", command=self.discover_hosts).pack()
        ttk.Button(self.root, text="P2P Connect", command=self.p2p_connect).pack()

        # Host list
        self.host_listbox = tk.Listbox(self.root)
        self.host_listbox.pack()

    def start(self):
        self.network_manager.set_interface(self.interface_var.get())
        self.network_manager.set_port(self.port_entry.get())
        self.network_manager.set_broadcast_name(self.broadcast_entry.get())
        self.kvm_control.set_shortcut(self.shortcut_entry.get())

        if self.mode_var.get() == "host":
            self.network_manager.start_host()
        else:
            selected_host = self.host_listbox.get(tk.ACTIVE)
            if selected_host:
                self.network_manager.connect_to_host(selected_host)

    def discover_hosts(self):
        hosts = self.network_manager.discover_hosts()
        self.host_listbox.delete(0, tk.END)
        for host in hosts:
            self.host_listbox.insert(tk.END, host)

    def p2p_connect(self):
        self.network_manager.p2p_connect()