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

        # Set a grid layout with padding
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        padding = {'padx': 10, 'pady': 5}

        # Interface selection
        ttk.Label(self.root, text="Network Interface:").grid(column=0, row=0, sticky=tk.W, **padding)
        self.interface_var = tk.StringVar()
        self.interface_dropdown = ttk.Combobox(self.root, textvariable=self.interface_var, state="readonly")
        self.interface_dropdown['values'] = self.network_manager.get_interfaces()
        self.interface_dropdown.grid(column=1, row=0, sticky=tk.EW, **padding)

        # Port entry
        ttk.Label(self.root, text="Port (0 for random):").grid(column=0, row=1, sticky=tk.W, **padding)
        self.port_entry = ttk.Entry(self.root)
        self.port_entry.grid(column=1, row=1, sticky=tk.EW, **padding)

        # Broadcast name entry
        ttk.Label(self.root, text="Broadcast Name:").grid(column=0, row=2, sticky=tk.W, **padding)
        self.broadcast_entry = ttk.Entry(self.root)
        self.broadcast_entry.insert(0, self.network_manager.broadcast_name)
        self.broadcast_entry.grid(column=1, row=2, sticky=tk.EW, **padding)

        # KVM switch shortcut
        ttk.Label(self.root, text="KVM Switch Shortcut:").grid(column=0, row=3, sticky=tk.W, **padding)
        self.shortcut_entry = ttk.Entry(self.root)
        self.shortcut_entry.grid(column=1, row=3, sticky=tk.EW, **padding)

        # Host/Client mode selection
        self.mode_var = tk.StringVar(value="client")
        ttk.Label(self.root, text="Mode:").grid(column=0, row=4, sticky=tk.W, **padding)
        mode_frame = ttk.Frame(self.root)
        ttk.Radiobutton(mode_frame, text="Host", variable=self.mode_var, value="host").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Client", variable=self.mode_var, value="client").pack(side=tk.LEFT)
        mode_frame.grid(column=1, row=4, sticky=tk.W, **padding)

        # Action buttons
        button_frame = ttk.Frame(self.root)
        ttk.Button(button_frame, text="Start", command=self.start).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Discover Hosts", command=self.discover_hosts).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="P2P Connect", command=self.p2p_connect).pack(side=tk.LEFT, padx=5)
        button_frame.grid(column=0, row=5, columnspan=2, pady=10)

        # Host list
        ttk.Label(self.root, text="Available Hosts:").grid(column=0, row=6, sticky=tk.W, **padding)
        self.host_listbox = tk.Listbox(self.root, height=6)
        self.host_listbox.grid(column=0, row=7, columnspan=2, sticky=tk.EW, **padding)

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

        self.kvm_control.start_listening()

    def discover_hosts(self):
        hosts = self.network_manager.discover_hosts()
        self.host_listbox.delete(0, tk.END)
        for host in hosts:
            self.host_listbox.insert(tk.END, host)

    def p2p_connect(self):
        self.network_manager.p2p_connect()
