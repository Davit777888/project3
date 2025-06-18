#!/usr/bin/env python3
import socket
import ipaddress
import concurrent.futures
import subprocess
import platform
from datetime import datetime

def scan_port(ip, port, timeout=1.0):
    try:
        sock = socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((str(ip), port))
        if result == 0:
            print(f"port {port} open {ip}")
            try:
                service = socket.getservbyport(port)
                print(f" Service: {service}")
            except:
                pass
            sock.close()
    except Exception as e:
        print(f"Error while scanning port {port}: {e}")
def ping_host(ip):
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', '-w', '1', str(ip)]
        with open('/dev/null', 'w') as devnull:
            return subprocess.call(command, stdout=devnull, stderr=devnull) == 0
    except:
        return False
def scan_network(network, ports, max_threads=100):
    print(f"\nNetwork scanning started {network} in {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        net = ipaddress.ip_network(network, strict=False)
    except ValueError as e:
        print(f"Error: {e}")
        return
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        for ip in net.hosts():
            ip = str(ip)
            if ping_host(ip):
                print(f"\nHost {ip} available")
                for port in ports:
                    executor.submit(scan_port, ip, port)
            else:
                print(f".", end="", flush=True)
        if     __name__ == "__main__":
            NETWORK = "192.168.1.0/24"
            PORTS_TO_SCAN = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3389]
            scan_network(NETWORK, PORTS_TO_SCAN)
            print("\nScanning complete!")
