#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Upload script for PythonAnywhere
This script helps upload the application files to PythonAnywhere
"""

import os
import sys
import requests
import getpass
import json
from pathlib import Path

# Configuration
API_BASE_URL = "https://www.pythonanywhere.com/api/v0/user/{username}"
DEFAULT_PATH = "/home/{username}/mysite"

def get_api_token():
    """Get the API token from the user"""
    print("Aby przesłać pliki do PythonAnywhere, potrzebujesz tokenu API.")
    print("Możesz go wygenerować na stronie: https://www.pythonanywhere.com/account/#api_token")
    return getpass.getpass("Wprowadź token API: ")

def get_username():
    """Get the PythonAnywhere username from the user"""
    return input("Wprowadź nazwę użytkownika PythonAnywhere: ")

def get_remote_path(username):
    """Get the remote path from the user"""
    default = DEFAULT_PATH.format(username=username)
    path = input(f"Wprowadź ścieżkę docelową na PythonAnywhere (domyślnie: {default}): ")
    return path if path else default

def create_remote_directory(username, token, path):
    """Create a remote directory if it doesn't exist"""
    url = API_BASE_URL.format(username=username) + "/files/path" + path
    headers = {"Authorization": f"Token {token}"}
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 201:
        print(f"Utworzono katalog: {path}")
        return True
    elif response.status_code == 200:
        print(f"Katalog już istnieje: {path}")
        return True
    else:
        print(f"Błąd podczas tworzenia katalogu: {response.status_code} - {response.text}")
        return False

def upload_file(username, token, local_path, remote_path):
    """Upload a file to PythonAnywhere"""
    url = API_BASE_URL.format(username=username) + "/files/path" + remote_path
    headers = {"Authorization": f"Token {token}"}
    
    with open(local_path, "rb") as f:
        content = f.read()
    
    response = requests.post(url, headers=headers, files={"content": content})
    
    if response.status_code == 201 or response.status_code == 200:
        print(f"Przesłano plik: {remote_path}")
        return True
    else:
        print(f"Błąd podczas przesyłania pliku: {response.status_code} - {response.text}")
        return False

# Files and directories to exclude from upload
EXCLUDE_LIST = [
    '.git',
    '.gitignore',
    'node_modules',
    '.vercel',
    'vercel.json',
    '__pycache__',
    '.vscode',
    '.idea',
    '.DS_Store',
    'venv',
    'env',
    '.env'
]

def should_exclude(path):
    """Check if a path should be excluded from upload"""
    basename = os.path.basename(path)
    
    # Check if the basename is in the exclude list
    if basename in EXCLUDE_LIST:
        return True
    
    # Check if the path contains any of the excluded directories
    for item in EXCLUDE_LIST:
        if f"/{item}/" in path or path.endswith(f"/{item}"):
            return True
    
    return False

def upload_directory(username, token, local_dir, remote_dir):
    """Upload a directory to PythonAnywhere"""
    # Check if directory should be excluded
    if should_exclude(local_dir):
        print(f"Pomijanie wykluczonego katalogu: {local_dir}")
        return True
    
    # Create the remote directory
    if not create_remote_directory(username, token, remote_dir):
        return False
    
    # Upload all files in the directory
    success = True
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir + "/" + item
        
        # Skip excluded files and directories
        if should_exclude(local_path):
            print(f"Pomijanie wykluczonego pliku/katalogu: {local_path}")
            continue
        
        if os.path.isdir(local_path):
            # Create subdirectory
            if not upload_directory(username, token, local_path, remote_path):
                success = False
        else:
            # Upload file
            if not upload_file(username, token, local_path, remote_path):
                success = False
    
    return success

def main():
    """Main function"""
    print("=== Narzędzie do przesyłania plików do PythonAnywhere ===")
    
    # Get user credentials
    username = get_username()
    token = get_api_token()
    remote_path = get_remote_path(username)
    
    # Get the local directory
    local_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Confirm upload
    print(f"\nPrzesyłanie plików z: {local_dir}")
    print(f"Do: {remote_path}")
    confirm = input("Czy chcesz kontynuować? (t/n): ")
    
    if confirm.lower() != "t":
        print("Anulowano przesyłanie.")
        return
    
    # Upload files
    print("\nRozpoczęto przesyłanie plików...")
    
    # Create main directories
    for directory in ["css", "js", "data", "img"]:
        create_remote_directory(username, token, remote_path + "/" + directory)
    
    # Upload all files
    if upload_directory(username, token, local_dir, remote_path):
        print("\nPrzesyłanie zakończone sukcesem!")
        print(f"Twoja aplikacja jest dostępna pod adresem: https://{username}.pythonanywhere.com")
    else:
        print("\nPrzesyłanie zakończone z błędami.")
        print("Sprawdź komunikaty błędów powyżej i spróbuj ponownie.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika.")
    except Exception as e:
        print(f"\nWystąpił błąd: {e}")
