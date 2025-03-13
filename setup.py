#!/usr/bin/env python
import os
import shutil
from pathlib import Path

def setup_project():
    """
    Sets up the project directories and files for the budget tracker application.
    """
    print("Setting up Personal Budget Tracker project...")
    
    # Create required directories
    directories = [
        "creds",
        "static",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Copy example files to their proper locations
    example_files = [
        ("categories.json.example", "categories.json"),
        ("transaction_mappings.json.example", "transaction_mappings.json"),
        (".env.example", ".env")
    ]
    
    for src, dest in example_files:
        src_path = Path(src)
        dest_path = Path(dest)
        
        if src_path.exists() and not dest_path.exists():
            shutil.copy2(src_path, dest_path)
            print(f"✓ Copied {src} to {dest}")
        elif not src_path.exists():
            print(f"✗ Warning: Example file {src} not found")
        else:
            print(f"- Skipped: {dest} already exists")
    
    print("\nSetup complete! Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run the application with: uvicorn app:app --reload")
    print("3. Visit http://localhost:8000 in your browser")

if __name__ == "__main__":
    setup_project()