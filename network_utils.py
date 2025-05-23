import socket
import psutil
import subprocess
import sys
import time
from typing import List, Tuple, Optional

def get_available_port(start_port: int, end_port: int = None) -> int:
    """Find first available port in range."""
    if end_port is None:
        end_port = start_port + 1000
        
    for port in range(start_port, end_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports in range {start_port}-{end_port}")

def get_local_ip() -> str:
    """Get the local IP address."""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to Google DNS
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return False
    except OSError:
        return True

def configure_windows_firewall(ports: List[int], protocol: str = "TCP") -> bool:
    """Configure Windows Firewall for the given ports."""
    if sys.platform != "win32":
        return True
        
    try:
        # Remove existing rules first
        for port in ports:
            rule_name = f"CoresAI_{protocol}_{port}"
            subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                 'name=all', 'protocol=TCP', f'localport={port}'],
                capture_output=True
            )
            
            # Add new inbound rule
            subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                 f'name={rule_name}',
                 'dir=in',
                 'action=allow',
                 f'protocol={protocol}',
                 f'localport={port}'],
                check=True,
                capture_output=True
            )
            
            # Add new outbound rule
            subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                 f'name={rule_name}',
                 'dir=out',
                 'action=allow',
                 f'protocol={protocol}',
                 f'localport={port}'],
                check=True,
                capture_output=True
            )
        return True
    except subprocess.CalledProcessError:
        return False

def kill_process_on_port(port: int) -> bool:
    """Kill any process using the specified port."""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        proc.kill()
                        time.sleep(0.5)  # Wait for process to terminate
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except Exception:
        return False

def setup_network(backend_port: int = 8082, frontend_port: int = 3000) -> Tuple[str, int, int]:
    """
    Set up network configuration including ports and firewall.
    Returns (local_ip, backend_port, frontend_port)
    """
    local_ip = get_local_ip()
    
    # Try to use preferred ports first, otherwise find available ones
    if is_port_in_use(backend_port):
        kill_process_on_port(backend_port)
        if is_port_in_use(backend_port):
            backend_port = get_available_port(8000, 9000)
            
    if is_port_in_use(frontend_port):
        kill_process_on_port(frontend_port)
        if is_port_in_use(frontend_port):
            frontend_port = get_available_port(3000, 4000)
    
    # Configure firewall
    configure_windows_firewall([backend_port, frontend_port])
    
    return local_ip, backend_port, frontend_port 