import os
# Enhanced error handling for system operations
import sys
import platform
import psutil
import wmi
import winreg
import subprocess
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

class SystemAwareness:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.wmi_client = wmi.WMI()
        self.system_info = {}
        self.update_system_info()

    def update_system_info(self) -> None:
        """Update all system information."""
        try:
            self.system_info = {
                'os': self._get_os_info(),
                'hardware': self._get_hardware_info(),
                'software': self._get_installed_software(),
                'performance': self._get_performance_metrics(),
                'network': self._get_network_info(),
                'security': self._get_security_info(),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error updating system info: {str(e)}")

    def _get_os_info(self) -> Dict[str, Any]:
        """Get detailed Windows OS information."""
        try:
            os_info = {
                'name': platform.system(),
                'version': platform.version(),
                'release': platform.release(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'windows_edition': self._get_windows_edition(),
                'last_update': self._get_last_windows_update(),
                'system_type': self._get_system_type(),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
            return os_info
        except Exception as e:
            self.logger.error(f"Error getting OS info: {str(e)}")
            return {}

    def _get_hardware_info(self) -> Dict[str, Any]:
        """Get detailed hardware information."""
        try:
            hardware_info = {
                'cpu': self._get_cpu_info(),
                'memory': self._get_memory_info(),
                'disks': self._get_disk_info(),
                'gpu': self._get_gpu_info(),
                'motherboard': self._get_motherboard_info()
            }
            return hardware_info
        except Exception as e:
            self.logger.error(f"Error getting hardware info: {str(e)}")
            return {}

    def _get_installed_software(self) -> List[Dict[str, str]]:
        """Get list of installed software."""
        try:
            software_list = []
            for software in self.wmi_client.Win32_Product():
                software_list.append({
                    'name': software.Name,
                    'version': software.Version,
                    'vendor': software.Vendor,
                    'install_date': software.InstallDate
                })
            return software_list
        except Exception as e:
            self.logger.error(f"Error getting installed software: {str(e)}")
            return []

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        try:
            return {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': dict(psutil.virtual_memory()._asdict()),
                'disk_usage': {disk.mountpoint: dict(psutil.disk_usage(disk.mountpoint)._asdict())
                             for disk in psutil.disk_partitions()},
                'network_io': dict(psutil.net_io_counters()._asdict()),
                'process_count': len(psutil.pids())
            }
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {str(e)}")
            return {}

    def _get_network_info(self) -> Dict[str, Any]:
        """Get network configuration and status."""
        try:
            network_info = {
                'interfaces': [],
                'connections': [],
                'dns_servers': []
            }
            
            # Get network interfaces
            for interface in psutil.net_if_addrs():
                network_info['interfaces'].append({
                    'name': interface,
                    'addresses': psutil.net_if_addrs()[interface]
                })
            
            # Get active connections
            for conn in psutil.net_connections():
                network_info['connections'].append({
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid
                })
            
            return network_info
        except Exception as e:
            self.logger.error(f"Error getting network info: {str(e)}")
            return {}

    def _get_security_info(self) -> Dict[str, Any]:
        """Get security-related information."""
        try:
            security_info = {
                'antivirus': self._get_antivirus_info(),
                'firewall': self._get_firewall_status(),
                'updates': self._get_security_updates(),
                'user_accounts': self._get_user_accounts()
            }
            return security_info
        except Exception as e:
            self.logger.error(f"Error getting security info: {str(e)}")
            return {}

    def _get_windows_edition(self) -> str:
        """Get Windows edition information."""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            edition = winreg.QueryValueEx(key, "ProductName")[0]
            winreg.CloseKey(key)
            return edition
        except Exception as e:
            self.logger.error(f"Error getting Windows edition: {str(e)}")
            return "Unknown"

    def _get_last_windows_update(self) -> str:
        """Get the last Windows update information."""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\UpdateHistory")
            last_update = winreg.QueryValueEx(key, "LastSuccessTime")[0]
            winreg.CloseKey(key)
            return last_update
        except Exception as e:
            logging.info(f"Could not get last Windows update: {e}")
            return "Unknown"

    def _get_system_type(self) -> str:
        """Get system type (32-bit or 64-bit)."""
        return platform.architecture()[0]

    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information."""
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                'cpu_usage_per_core': [f"{x}%" for x in psutil.cpu_percent(percpu=True)],
                'total_cpu_usage': f"{psutil.cpu_percent()}%"
            }
            return cpu_info
        except Exception as e:
            self.logger.error(f"Error getting CPU info: {str(e)}")
            return {}

    def _get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                'total': f"{memory.total / (1024**3):.2f} GB",
                'available': f"{memory.available / (1024**3):.2f} GB",
                'used': f"{memory.used / (1024**3):.2f} GB",
                'percentage': f"{memory.percent}%",
                'swap_total': f"{swap.total / (1024**3):.2f} GB",
                'swap_used': f"{swap.used / (1024**3):.2f} GB",
                'swap_free': f"{swap.free / (1024**3):.2f} GB"
            }
        except Exception as e:
            self.logger.error(f"Error getting memory info: {str(e)}")
            return {}

    def _get_disk_info(self) -> List[Dict[str, Any]]:
        """Get detailed disk information."""
        try:
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': f"{usage.total / (1024**3):.2f} GB",
                        'used': f"{usage.used / (1024**3):.2f} GB",
                        'free': f"{usage.free / (1024**3):.2f} GB",
                        'percentage': f"{usage.percent}%"
                    }
                    disks.append(disk_info)
                except Exception:
                    continue
            return disks
        except Exception as e:
            self.logger.error(f"Error getting disk info: {str(e)}")
            return []

    def _get_gpu_info(self) -> List[Dict[str, Any]]:
        """Get GPU information."""
        try:
            gpus = []
            for gpu in self.wmi_client.Win32_VideoController():
                gpu_info = {
                    'name': gpu.Name,
                    'adapter_ram': f"{int(gpu.AdapterRAM) / (1024**3):.2f} GB" if gpu.AdapterRAM else "Unknown",
                    'driver_version': gpu.DriverVersion,
                    'video_processor': gpu.VideoProcessor,
                    'video_memory_type': gpu.VideoMemoryType
                }
                gpus.append(gpu_info)
            return gpus
        except Exception as e:
            self.logger.error(f"Error getting GPU info: {str(e)}")
            return []

    def _get_motherboard_info(self) -> Dict[str, str]:
        """Get motherboard information."""
        try:
            board = self.wmi_client.Win32_BaseBoard()[0]
            return {
                'manufacturer': board.Manufacturer,
                'product': board.Product,
                'serial': board.Serial,
                'version': board.Version
            }
        except Exception as e:
            logging.info(f"Could not get motherboard info: {e}")
            return {}

    def _get_antivirus_info(self) -> List[Dict[str, str]]:
        """Get installed antivirus information."""
        try:
            antivirus_list = []
            for av in self.wmi_client.Win32_Product():
                if any(keyword in av.Name.lower() for keyword in ['antivirus', 'security', 'defender']):
                    antivirus_list.append({
                        'name': av.Name,
                        'version': av.Version,
                        'vendor': av.Vendor
                    })
            return antivirus_list
        except Exception as e:
            self.logger.error(f"Error getting antivirus info: {str(e)}")
            return []

    def _get_firewall_status(self) -> Dict[str, Any]:
        """Get Windows Firewall status."""
        try:
            firewall = self.wmi_client.Win32_FirewallSettings()[0]
            return {
                'enabled': firewall.Enabled,
                'default_inbound_action': firewall.DefaultInboundAction,
                'default_outbound_action': firewall.DefaultOutboundAction
            }
        except Exception as e:
            self.logger.error(f"Error getting firewall status: {str(e)}")
            return {}

    def _get_security_updates(self) -> List[Dict[str, str]]:
        """Get recent security updates."""
        try:
            updates = []
            for update in self.wmi_client.Win32_QuickFixEngineering():
                if 'security' in update.Description.lower():
                    updates.append({
                        'hotfix_id': update.HotFixID,
                        'description': update.Description,
                        'installed_on': update.InstalledOn
                    })
            return updates
        except Exception as e:
            self.logger.error(f"Error getting security updates: {str(e)}")
            return []

    def _get_user_accounts(self) -> List[Dict[str, str]]:
        """Get user account information."""
        try:
            users = []
            for user in self.wmi_client.Win32_UserAccount():
                users.append({
                    'name': user.Name,
                    'full_name': user.FullName,
                    'disabled': user.Disabled,
                    'account_type': user.AccountType,
                    'sid': user.SID
                })
            return users
        except Exception as e:
            self.logger.error(f"Error getting user accounts: {str(e)}")
            return []

    def get_system_summary(self) -> Dict[str, Any]:
        """Get a summary of the system state."""
        self.update_system_info()
        return {
            'system_info': self.system_info,
            'timestamp': datetime.now().isoformat()
        }

    def get_specific_info(self, category: str) -> Dict[str, Any]:
        """Get specific system information by category."""
        if category in self.system_info:
            return self.system_info[category]
        return {} 