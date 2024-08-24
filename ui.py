import tkinter as tk
from tkinter import ttk
import threading

class KVMUI:
    def __init__(self, root, network_manager, kvm_control):
        self.root = root
        self.network_manager = network_manager
        self.kvm_control = kvm_control
        self.setup_ui()

    def setup_ui(self):
        self.root.title("KVM Control")
        self.root.geometry("400x300")

        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text=f"IP: {self.network_manager.ip}").grid(column=0, row=0, sticky=tk.W)

        self.mode_var = tk.StringVar(value="client")
        ttk.Radiobutton(frame, text="Host", variable=self.mode_var, value="host").grid(column=0, row=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="Client", variable=self.mode_var, value="client").grid(column=1, row=1, sticky=tk.W)

        self.start_button = ttk.Button(frame, text="Start", command=self.start)
        self.start_button.grid(column=0, row=2, columnspan=2, sticky=tk.EW)

        self.host_listbox = tk.Listbox(frame, height=5)
        self.host_listbox.grid(column=0, row=3, columnspan=2, sticky=(tk.W, tk.E))

        self.connect_button = ttk.Button(frame, text="Connect", command=self.connect, state=tk.DISABLED)
        self.connect_button.grid(column=0, row=4, columnspan=2, sticky=tk.EW)

        self.status_label = ttk.Label(frame, text="Not connected")
        self.status_label.grid(column=0, row=5, columnspan=2, sticky=tk.W)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(column=0, row=6, columnspan=2, sticky=(tk.W, tk.E))

        self.discover_hosts()

    def start(self):
        if self.mode_var.get() == "host":
            self.network_manager.start_host()
            self.start_button.config(text="Stop", command=self.stop)
            self.status_label.config(text="Waiting for connection...")
        self.kvm_control.start_listening()

    def stop(self):
        self.network_manager.disconnect()
        self.kvm_control.stop_listening()
        self.start_button.config(text="Start", command=self.start)
        self.status_label.config(text="Disconnected")

    def connect(self):
        selected = self.host_listbox.curselection()
        if selected:
            host_ip = self.host_listbox.get(selected[0])
            self.network_manager.connect_to_host(host_ip)
            self.connect_button.config(text="Disconnect", command=self.disconnect)
            self.status_label.config(text=f"Connected to {host_ip}")
            self.kvm_control.start_listening()

    def disconnect(self):
        self.network_manager.disconnect()
        self.kvm_control.stop_listening()
        self.connect_button.config(text="Connect", command=self.connect)
        self.status_label.config(text="Disconnected")

    def discover_hosts(self):
        def task():
            hosts = self.network_manager.discover_hosts()
            self.host_listbox.delete(0, tk.END)
            for host in hosts:
                self.host_listbox.insert(tk.END, host)
            self.connect_button.config(state=tk.NORMAL)
            self.progress_var.set(0)

        self.progress_var.set(50)
        threading.Thread(target=task, daemon=True).start()

    def run(self):
        self.root.mainloop()