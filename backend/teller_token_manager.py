import os
import json
import base64
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


class TellerTokenManager:
    """
    Manages Teller API access tokens, including storage and retrieval.
    Tokens are stored in the creds directory and are associated with institutions.
    """
    
    def __init__(self, creds_dir: str = "creds"):
        self.creds_dir = creds_dir
        self.tokens_file = os.path.join(creds_dir, "teller_tokens.json")
        
        # Ensure the creds directory exists
        os.makedirs(creds_dir, exist_ok=True)
        
        # Load existing tokens or create empty structure
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict:
        """Load tokens from the tokens file or return empty dict if file doesn't exist"""
        if os.path.exists(self.tokens_file):
            try:
                with open(self.tokens_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading tokens: {e}")
                return {"tokens": []}
        else:
            return {"tokens": []}
    
    def _save_tokens(self) -> None:
        """Save tokens to the tokens file"""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            print(f"Error saving tokens: {e}")
    
    def store_token(self, 
                   access_token: str, 
                   institution_name: str,
                   institution_id: Optional[str] = None,
                   user_id: Optional[str] = None,
                   enrollment_id: Optional[str] = None,
                   signature: Optional[str] = None) -> bool:
        """
        Store a new Teller access token
        
        Args:
            access_token: The access token from Teller
            institution_name: Name of the financial institution
            institution_id: ID of the financial institution (optional)
            user_id: Teller user ID (optional)
            enrollment_id: Teller enrollment ID (optional)
            signature: Token signature (optional)
            
        Returns:
            bool: True if token was stored successfully, False otherwise
        """
        # Check if token already exists
        for token in self.tokens["tokens"]:
            if token.get("access_token") == access_token:
                # Update existing token
                token.update({
                    "institution_name": institution_name,
                    "institution_id": institution_id,
                    "user_id": user_id,
                    "enrollment_id": enrollment_id,
                    "signature": signature,
                    "last_updated": datetime.now().isoformat()
                })
                self._save_tokens()
                return True
        
        # Add new token
        self.tokens["tokens"].append({
            "access_token": access_token,
            "institution_name": institution_name,
            "institution_id": institution_id,
            "user_id": user_id,
            "enrollment_id": enrollment_id,
            "signature": signature,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        })
        
        self._save_tokens()
        return True
    
    def store_teller_enrollment(self, enrollment_data: Dict) -> bool:
        """
        Store token information from a Teller enrollment response
        
        Args:
            enrollment_data: The enrollment object from Teller Connect onSuccess callback
            
        Returns:
            bool: True if token was stored successfully, False otherwise
        """
        try:
            access_token = enrollment_data.get("accessToken")
            if not access_token:
                print("Error: No access token in enrollment data")
                return False
            
            # Extract user and enrollment info
            user_info = enrollment_data.get("user", {})
            enrollment_info = enrollment_data.get("enrollment", {})
            institution_info = enrollment_info.get("institution", {})
            
            return self.store_token(
                access_token=access_token,
                institution_name=institution_info.get("name", "Unknown Institution"),
                institution_id=institution_info.get("id"),
                user_id=user_info.get("id"),
                enrollment_id=enrollment_info.get("id"),
                signature=enrollment_data.get("signatures", [None])
            )
        except Exception as e:
            print(f"Error storing enrollment: {e}")
            return False
    
    def get_all_tokens(self) -> List[Dict]:
        """Get all stored tokens"""
        return self.tokens["tokens"]
    
    def get_token_by_institution(self, institution_name: str) -> Optional[str]:
        """Get a token for a specific institution"""
        for token in self.tokens["tokens"]:
            if token.get("institution_name", "").lower() == institution_name.lower():
                return token.get("access_token")
        return None
    
    def get_token_info(self, access_token: str) -> Optional[Dict]:
        """Get information about a specific token"""
        for token in self.tokens["tokens"]:
            if token.get("access_token") == access_token:
                return token
        return None
    
    def delete_token(self, access_token: str) -> bool:
        """Delete a token"""
        for i, token in enumerate(self.tokens["tokens"]):
            if token.get("access_token") == access_token:
                del self.tokens["tokens"][i]
                self._save_tokens()
                return True
        return False
    
    def delete_all_tokens(self) -> bool:
        """Delete all tokens"""
        self.tokens = {"tokens": []}
        self._save_tokens()
        return True