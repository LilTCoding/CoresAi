"""
CoresAI License Key Validator
Handles validation and management of license keys
"""

import json
import os
import datetime
from typing import Dict, Optional, Tuple
import hashlib
import logging
from .hardware_fingerprint import get_system_fingerprint, verify_system_fingerprint

logger = logging.getLogger(__name__)

class LicenseValidator:
    def __init__(self, license_file: str = "private_license_keys.json"):
        self.license_file = license_file
        self.keys_data = self._load_license_data()
        
    def _load_license_data(self) -> Dict:
        """Load the license key data from the JSON file."""
        try:
            if not os.path.exists(self.license_file):
                logger.error(f"License file not found: {self.license_file}")
                return {}
                
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading license data: {str(e)}")
            return {}

    def validate_key(self, key: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate a license key.
        
        Args:
            key: The license key to validate
            
        Returns:
            Tuple containing:
            - bool: Whether the key is valid
            - str: Duration code if valid, empty string if not
            - str: Error message if invalid, None if valid
        """
        try:
            # Check basic format
            if not key or not isinstance(key, str):
                return False, "", "Invalid key format"

            # Check prefix
            if not key.startswith("CoresAi-"):
                return False, "", "Invalid key prefix"

            # Split the key into segments
            segments = key.split("-")
            if len(segments) != 6:
                return False, "", "Invalid key structure"

            # Get duration code
            duration_code = segments[1]
            if duration_code not in self.keys_data["validation_rules"]["allowed_durations"]:
                return False, "", "Invalid duration code"

            # Check if key exists in the database
            duration_map = {
                "1M": "1_month",
                "3M": "3_months",
                "6M": "6_months",
                "12M": "12_months",
                "LT": "lifetime"
            }
            
            duration = duration_map.get(duration_code)
            if not duration:
                return False, "", "Invalid duration"

            # Search for the key in the appropriate duration section
            key_list = self.keys_data["license_keys"][duration]["keys"]
            key_entry = next((k for k in key_list if k["key"] == key), None)
            
            if not key_entry:
                return False, "", "Key not found in database"
                
            if key_entry["status"] != "unused":
                # If key is used, check hardware fingerprint
                if "hardware_fingerprint" in key_entry:
                    if not verify_system_fingerprint(key_entry["hardware_fingerprint"]):
                        return False, "", "Key is locked to a different system"
                return False, "", "Key has already been used"

            return True, duration_code, None

        except Exception as e:
            logger.error(f"Error validating key: {str(e)}")
            return False, "", f"Validation error: {str(e)}"

    def mark_key_as_used(self, key: str) -> bool:
        """Mark a key as used in the database and lock it to the current hardware."""
        try:
            # Get hardware fingerprint
            hardware_fingerprint = get_system_fingerprint()
            
            # Find and update the key
            for duration in self.keys_data["license_keys"]:
                key_list = self.keys_data["license_keys"][duration]["keys"]
                for k in key_list:
                    if k["key"] == key and k["status"] == "unused":
                        k.update({
                            "status": "used",
                            "activation_date": datetime.datetime.now().isoformat(),
                            "hardware_fingerprint": hardware_fingerprint,
                            "activation_hwids": {
                                "timestamp": datetime.datetime.now().isoformat(),
                                "fingerprint": hardware_fingerprint
                            }
                        })
                        
                        # Save the updated data
                        with open(self.license_file, 'w') as f:
                            json.dump(self.keys_data, f, indent=2)
                        return True
            return False
            
        except Exception as e:
            logger.error(f"Error marking key as used: {str(e)}")
            return False

    def get_key_duration(self, duration_code: str) -> Optional[int]:
        """Get the duration in days for a given duration code."""
        duration_days = {
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "12M": 365,
            "LT": 36500  # 100 years for lifetime
        }
        return duration_days.get(duration_code)

    def get_key_price(self, duration_code: str) -> Optional[float]:
        """Get the price for a given duration code."""
        duration_map = {
            "1M": "1_month",
            "3M": "3_months",
            "6M": "6_months",
            "12M": "12_months",
            "LT": "lifetime"
        }
        duration = duration_map.get(duration_code)
        return self.keys_data["pricing"].get(duration) if duration else None

    def verify_hardware_lock(self, key: str) -> Tuple[bool, str]:
        """Verify if the current hardware matches the locked hardware for a key."""
        try:
            # Find the key in the database
            for duration in self.keys_data["license_keys"]:
                key_list = self.keys_data["license_keys"][duration]["keys"]
                key_entry = next((k for k in key_list if k["key"] == key), None)
                
                if key_entry and "hardware_fingerprint" in key_entry:
                    if verify_system_fingerprint(key_entry["hardware_fingerprint"]):
                        return True, "Hardware verification successful"
                    return False, "Key is locked to a different system"
                    
            return False, "Key not found or not activated"
            
        except Exception as e:
            logger.error(f"Error verifying hardware lock: {str(e)}")
            return False, f"Hardware verification error: {str(e)}"

def validate_and_activate_key(key: str) -> Tuple[bool, str]:
    """
    Validate and activate a license key.
    
    Args:
        key: The license key to validate and activate
        
    Returns:
        Tuple containing:
        - bool: Whether the operation was successful
        - str: Success/error message
    """
    validator = LicenseValidator()
    
    # Validate the key
    is_valid, duration_code, error = validator.validate_key(key)
    
    if not is_valid:
        return False, f"Invalid license key: {error}"
    
    # Mark the key as used and lock to hardware
    if not validator.mark_key_as_used(key):
        return False, "Failed to activate key"
    
    # Get duration and price info
    duration_days = validator.get_key_duration(duration_code)
    price = validator.get_key_price(duration_code)
    
    return True, f"License key activated successfully! Duration: {duration_days} days, Price: ${price}"

if __name__ == "__main__":
    # Example usage
    test_key = "CoresAi-1M-X7K9-NQWP-VJHT-L4MD"
    success, message = validate_and_activate_key(test_key)
    print(message) 