"""
CoresAI Hardware Fingerprinting
Collects and validates hardware-specific identifiers
"""

import wmi
import hashlib
import subprocess
import uuid
import json
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class HardwareFingerprint:
    def __init__(self):
        self.wmi = wmi.WMI()
        
    def get_cpu_info(self) -> str:
        """Get CPU identifier."""
        try:
            cpu = self.wmi.Win32_Processor()[0]
            cpu_id = f"{cpu.ProcessorId.strip()}-{cpu.Name.strip()}"
            return hashlib.sha256(cpu_id.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error getting CPU info: {str(e)}")
            return ""

    def get_gpu_info(self) -> List[str]:
        """Get GPU identifiers."""
        try:
            gpus = self.wmi.Win32_VideoController()
            gpu_ids = []
            for gpu in gpus:
                gpu_id = f"{gpu.Name.strip()}-{gpu.DeviceID.strip()}"
                gpu_ids.append(hashlib.sha256(gpu_id.encode()).hexdigest())
            return gpu_ids
        except Exception as e:
            logger.error(f"Error getting GPU info: {str(e)}")
            return []

    def get_disk_info(self) -> List[str]:
        """Get storage device identifiers."""
        try:
            disks = self.wmi.Win32_DiskDrive()
            disk_ids = []
            for disk in disks:
                disk_id = f"{disk.Model.strip()}-{disk.SerialNumber.strip()}"
                disk_ids.append(hashlib.sha256(disk_id.encode()).hexdigest())
            return disk_ids
        except Exception as e:
            logger.error(f"Error getting disk info: {str(e)}")
            return []

    def get_motherboard_info(self) -> str:
        """Get motherboard identifier."""
        try:
            board = self.wmi.Win32_BaseBoard()[0]
            board_id = f"{board.Manufacturer.strip()}-{board.Product.strip()}-{board.SerialNumber.strip()}"
            return hashlib.sha256(board_id.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error getting motherboard info: {str(e)}")
            return ""

    def get_network_adapters(self) -> List[str]:
        """Get network adapter MAC addresses."""
        try:
            adapters = self.wmi.Win32_NetworkAdapter(PhysicalAdapter=True)
            mac_addresses = []
            for adapter in adapters:
                if adapter.MACAddress:
                    mac_addresses.append(hashlib.sha256(adapter.MACAddress.encode()).hexdigest())
            return mac_addresses
        except Exception as e:
            logger.error(f"Error getting network adapters: {str(e)}")
            return []

    def get_machine_guid(self) -> str:
        """Get Windows machine GUID."""
        try:
            machine_guid = str(uuid.getnode())
            return hashlib.sha256(machine_guid.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error getting machine GUID: {str(e)}")
            return ""

    def collect_all_hwids(self) -> Dict[str, any]:
        """Collect all hardware identifiers."""
        return {
            "cpu_id": self.get_cpu_info(),
            "gpu_ids": self.get_gpu_info(),
            "disk_ids": self.get_disk_info(),
            "motherboard_id": self.get_motherboard_info(),
            "network_ids": self.get_network_adapters(),
            "machine_guid": self.get_machine_guid()
        }

    def generate_system_fingerprint(self) -> str:
        """Generate a unique system fingerprint from all hardware IDs."""
        hwids = self.collect_all_hwids()
        fingerprint_str = (
            f"{hwids['cpu_id']}-"
            f"{'-'.join(hwids['gpu_ids'])}-"
            f"{'-'.join(hwids['disk_ids'])}-"
            f"{hwids['motherboard_id']}-"
            f"{'-'.join(hwids['network_ids'])}-"
            f"{hwids['machine_guid']}"
        )
        return hashlib.sha512(fingerprint_str.encode()).hexdigest()

    def verify_hardware_match(self, stored_fingerprint: str) -> bool:
        """Verify if current hardware matches stored fingerprint."""
        current_fingerprint = self.generate_system_fingerprint()
        return current_fingerprint == stored_fingerprint

def get_system_fingerprint() -> str:
    """Get the current system's hardware fingerprint."""
    fingerprinter = HardwareFingerprint()
    return fingerprinter.generate_system_fingerprint()

def verify_system_fingerprint(stored_fingerprint: str) -> bool:
    """Verify if the current system matches a stored fingerprint."""
    fingerprinter = HardwareFingerprint()
    return fingerprinter.verify_hardware_match(stored_fingerprint)

if __name__ == "__main__":
    # Example usage
    fingerprint = get_system_fingerprint()
    print(f"System Fingerprint: {fingerprint}") 