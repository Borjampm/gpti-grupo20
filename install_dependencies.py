#!/usr/bin/env python3
"""
Installation script for the Telegram Bot dependencies
This script helps install all required packages including Spire.Office.Free for enhanced Word to PDF conversion
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🤖 Installing Telegram Bot Dependencies...")
    print("=" * 50)

    # Read requirements from file
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ Error: {requirements_file} not found!")
        return

    with open(requirements_file, 'r') as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    failed_packages = []

    for package in packages:
        print(f"📦 Installing {package}...")
        if install_package(package):
            print(f"✅ Successfully installed {package}")
        else:
            print(f"❌ Failed to install {package}")
            failed_packages.append(package)

    print("\n" + "=" * 50)

    if failed_packages:
        print(f"❌ Installation completed with {len(failed_packages)} failed packages:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\nYou may need to install these manually or check for compatibility issues.")
    else:
        print("✅ All packages installed successfully!")

    print("\n📋 Special Notes:")
    print("• docx2pdf provides enhanced Word to PDF conversion with formatting preservation")
    print("• pdf2docx provides enhanced PDF to Word conversion with layout, tables, and images")
    print("• LibreOffice CLI provides enhanced PowerPoint to PDF conversion")
    print("• Cross-platform compatibility (Windows, macOS, Linux)")
    print("• Automatic fallback methods for maximum compatibility")
    print("• For PDF to image conversion, install 'poppler-utils' system package separately")
    print("• For PowerPoint conversion, install LibreOffice separately")
    print("\n🚀 You can now run the bot with: python main.py")

if __name__ == "__main__":
    main()
