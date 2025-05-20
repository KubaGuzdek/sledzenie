#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Skrypt do tworzenia archiwum ZIP dla wdrożenia na Render.com
Ten skrypt tworzy archiwum ZIP zawierające wszystkie niezbędne pliki do wdrożenia na Render.com
"""

import os
import sys
import zipfile
import datetime
import shutil
from pathlib import Path

def create_zip_archive(output_path=None):
    """Tworzy archiwum ZIP z plikami do wdrożenia na Render.com"""
    
    # Lista plików i katalogów do uwzględnienia
    include_files = [
        # Pliki konfiguracyjne
        "render.yaml",
        "wsgi_render.py",
        "requirements.txt",
        
        # Pliki backendu
        "websocket_server.py",
        
        # Pliki HTML
        "index.html",
        "login.html",
        "organizer-view.html",
        "404.html",
        "map-placeholder.html",
        
        # Pliki README
        "README.md"
    ]
    
    # Lista katalogów do uwzględnienia
    include_dirs = [
        "css",
        "js",
        "img",
        "data"
    ]
    
    # Lista plików i katalogów do wykluczenia
    exclude_files = [
        ".DS_Store",
        ".gitignore",
        "setup_git_for_render.py",
        "render_direct_deploy.py",
        "verify_render_files.py",
        "create_render_zip.py",
        "test_websocket_client.py",
        "test_websocket_server.py",
        "upload_to_pythonanywhere.py"
    ]
    
    exclude_dirs = [
        ".git",
        "__pycache__",
        "venv",
        "env",
        "node_modules"
    ]
    
    # Jeśli nie podano ścieżki wyjściowej, użyj domyślnej
    if output_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"king-of-the-bay_render_{timestamp}.zip"
    
    print(f"Tworzenie archiwum ZIP: {output_path}")
    
    # Utwórz archiwum ZIP
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Dodaj pliki
        for file_path in include_files:
            if os.path.isfile(file_path):
                print(f"Dodawanie pliku: {file_path}")
                zipf.write(file_path)
            else:
                print(f"Plik nie istnieje, pomijanie: {file_path}")
        
        # Dodaj katalogi
        for dir_path in include_dirs:
            if os.path.isdir(dir_path):
                print(f"Dodawanie katalogu: {dir_path}")
                
                for root, dirs, files in os.walk(dir_path):
                    # Usuń wykluczane katalogi
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    
                    for file in files:
                        # Pomiń wykluczane pliki
                        if file in exclude_files:
                            continue
                        
                        file_path = os.path.join(root, file)
                        print(f"  Dodawanie: {file_path}")
                        zipf.write(file_path)
            else:
                print(f"Katalog nie istnieje, pomijanie: {dir_path}")
    
    # Sprawdź, czy archiwum zostało utworzone
    if os.path.isfile(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\nArchiwum ZIP zostało utworzone: {output_path}")
        print(f"Rozmiar: {size_mb:.2f} MB")
        print("\nMożesz teraz wgrać to archiwum na Render.com przez panel administracyjny.")
        return output_path
    else:
        print("\nBłąd: Nie udało się utworzyć archiwum ZIP.")
        return None

def main():
    """Główna funkcja"""
    print("=== Tworzenie archiwum ZIP dla wdrożenia na Render.com ===\n")
    
    # Sprawdź, czy podano ścieżkę wyjściową
    output_path = None
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    
    # Utwórz archiwum ZIP
    zip_path = create_zip_archive(output_path)
    
    if zip_path:
        print("\nInstrukcja wgrania archiwum na Render.com:")
        print("1. Zaloguj się do panelu Render.com: https://dashboard.render.com/")
        print("2. Utwórz nową usługę typu 'Web Service'")
        print("3. Wybierz opcję 'Upload Files'")
        print("4. Prześlij utworzone archiwum ZIP")
        print("5. Skonfiguruj usługę zgodnie z instrukcją w pliku RENDER_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika")
    except Exception as e:
        print(f"\nWystąpił nieoczekiwany błąd: {e}")
