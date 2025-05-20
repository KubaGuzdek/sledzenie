#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Direct deployment to Render.com without Git
This script helps upload files directly to Render.com using their API
"""

import os
import sys
import requests
import json
import getpass
import zipfile
import tempfile
import time
from pathlib import Path

def create_zip_archive(directory='.', exclude_dirs=None, exclude_files=None):
    """Create a ZIP archive of the current directory"""
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', 'venv', 'env', 'node_modules']
    
    if exclude_files is None:
        exclude_files = ['.DS_Store', '.gitignore', '.env']
    
    print("Tworzenie archiwum ZIP...")
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_file.close()
    
    # Create a ZIP archive
    with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # Skip excluded files
                if file in exclude_files:
                    continue
                
                file_path = os.path.join(root, file)
                
                # Skip the ZIP file itself
                if os.path.abspath(file_path) == os.path.abspath(temp_file.name):
                    continue
                
                # Add file to ZIP
                zipf.write(file_path, os.path.relpath(file_path, directory))
    
    print(f"Archiwum ZIP zostało utworzone: {temp_file.name}")
    return temp_file.name

def upload_to_render(api_key, zip_file):
    """Upload a ZIP archive to Render.com"""
    print("Przygotowanie do wgrania na Render.com...")
    
    # Get service name
    service_name = input("Podaj nazwę usługi na Render.com (np. king-of-the-bay): ")
    
    # Create headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/zip"
    }
    
    # Upload ZIP file
    print(f"Wgrywanie plików do usługi {service_name}...")
    
    with open(zip_file, 'rb') as f:
        response = requests.post(
            f"https://api.render.com/v1/services/{service_name}/deploys",
            headers=headers,
            data=f
        )
    
    # Check response
    if response.status_code == 201:
        print("Pliki zostały pomyślnie wgrane na Render.com.")
        deploy_id = response.json().get("id")
        print(f"ID wdrożenia: {deploy_id}")
        return deploy_id
    else:
        print(f"Błąd podczas wgrywania plików: {response.status_code}")
        print(response.text)
        return None

def check_deploy_status(api_key, service_name, deploy_id):
    """Check the status of a deployment"""
    print("Sprawdzanie statusu wdrożenia...")
    
    # Create headers
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Check status
    response = requests.get(
        f"https://api.render.com/v1/services/{service_name}/deploys/{deploy_id}",
        headers=headers
    )
    
    # Check response
    if response.status_code == 200:
        status = response.json().get("status")
        print(f"Status wdrożenia: {status}")
        return status
    else:
        print(f"Błąd podczas sprawdzania statusu: {response.status_code}")
        print(response.text)
        return None

def create_render_service(api_key):
    """Create a new service on Render.com"""
    print("Tworzenie nowej usługi na Render.com...")
    
    # Get service details
    service_name = input("Podaj nazwę usługi (np. king-of-the-bay): ")
    service_type = "web_service"
    
    # Create headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Create service data
    data = {
        "name": service_name,
        "type": service_type,
        "env": "python",
        "region": "frankfurt",  # or another region
        "plan": "free",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "python wsgi_render.py",
        "envVars": [
            {
                "key": "PYTHON_VERSION",
                "value": "3.9.0"
            }
        ]
    }
    
    # Create service
    response = requests.post(
        "https://api.render.com/v1/services",
        headers=headers,
        json=data
    )
    
    # Check response
    if response.status_code == 201:
        print(f"Usługa {service_name} została utworzona na Render.com.")
        service_id = response.json().get("id")
        print(f"ID usługi: {service_id}")
        return service_id, service_name
    else:
        print(f"Błąd podczas tworzenia usługi: {response.status_code}")
        print(response.text)
        return None, None

def main():
    """Main function"""
    print("=== Bezpośrednie wdrożenie na Render.com bez użycia Git ===")
    
    # Get Render.com API key
    print("\nAby wdrożyć aplikację na Render.com, potrzebujesz klucza API.")
    print("Klucz API możesz wygenerować na stronie: https://render.com/docs/api")
    
    api_key = getpass.getpass("Podaj klucz API Render.com: ")
    
    # Check if service exists
    service_exists = input("Czy usługa już istnieje na Render.com? (t/n): ").lower() == "t"
    
    if service_exists:
        service_name = input("Podaj nazwę istniejącej usługi: ")
        service_id = None
    else:
        # Create a new service
        service_id, service_name = create_render_service(api_key)
        
        if not service_id:
            print("Nie udało się utworzyć usługi. Spróbuj ponownie później.")
            return
    
    # Create ZIP archive
    zip_file = create_zip_archive()
    
    # Upload to Render.com
    deploy_id = upload_to_render(api_key, zip_file)
    
    if deploy_id:
        print("\nPliki zostały wgrane na Render.com.")
        print("Wdrożenie jest w trakcie. Może to potrwać kilka minut.")
        
        # Check status periodically
        for _ in range(10):
            status = check_deploy_status(api_key, service_name, deploy_id)
            
            if status == "live":
                print("\nWdrożenie zakończone sukcesem!")
                print(f"Aplikacja jest dostępna pod adresem: https://{service_name}.onrender.com")
                break
            elif status == "failed":
                print("\nWdrożenie nie powiodło się.")
                print("Sprawdź logi w panelu Render.com, aby dowiedzieć się więcej.")
                break
            
            print("Oczekiwanie na zakończenie wdrożenia...")
            time.sleep(30)
    
    # Clean up
    try:
        os.unlink(zip_file)
        print(f"Usunięto tymczasowy plik ZIP: {zip_file}")
    except:
        pass
    
    print("\nProces wdrożenia zakończony.")
    print("Możesz sprawdzić status wdrożenia w panelu Render.com.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika.")
    except Exception as e:
        print(f"\nWystąpił błąd: {e}")
