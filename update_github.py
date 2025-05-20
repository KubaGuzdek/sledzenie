#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Skrypt do aktualizacji plików na GitHub
Ten skrypt pomaga zaktualizować pliki na GitHub poprzez automatyzację procesu commit i push
"""

import os
import sys
import subprocess
import getpass
from datetime import datetime

def run_command(command, show_output=True):
    """Uruchom polecenie powłoki i zwróć wynik"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, 
                               capture_output=True)
        if show_output and result.stdout:
            print(result.stdout)
        return result.stdout, True
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas wykonywania komendy: {command}")
        print(f"Kod błędu: {e.returncode}")
        if e.stdout:
            print(f"Standardowe wyjście: {e.stdout}")
        if e.stderr:
            print(f"Błąd: {e.stderr}")
        return e.stderr, False

def is_git_installed():
    """Sprawdź, czy Git jest zainstalowany"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_git_repository():
    """Sprawdź, czy bieżący katalog jest repozytorium Git"""
    return os.path.isdir(".git")

def get_remote_url():
    """Pobierz URL zdalnego repozytorium"""
    try:
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                               check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_current_branch():
    """Pobierz nazwę bieżącej gałęzi"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"], 
                               check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "main"  # Domyślna gałąź

def initialize_git_repository():
    """Inicjalizuj nowe repozytorium Git"""
    print("Inicjalizacja repozytorium Git...")
    run_command("git init")

def create_gitignore():
    """Utwórz plik .gitignore, jeśli nie istnieje"""
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""
    
    if not os.path.exists(".gitignore"):
        print("Tworzenie pliku .gitignore...")
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        print("Plik .gitignore został utworzony.")
    else:
        print("Plik .gitignore już istnieje.")

def configure_git_user():
    """Skonfiguruj użytkownika Git, jeśli nie jest już skonfigurowany"""
    try:
        user_name = subprocess.check_output(["git", "config", "user.name"], text=True).strip()
        user_email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
        print(f"Użytkownik Git już skonfigurowany: {user_name} <{user_email}>")
        return True
    except subprocess.CalledProcessError:
        print("Konfiguracja użytkownika Git...")
        name = input("Podaj swoje imię i nazwisko dla Git: ")
        email = input("Podaj swój adres email dla Git: ")
        
        run_command(f'git config user.name "{name}"')
        run_command(f'git config user.email "{email}"')
        print("Użytkownik Git został skonfigurowany.")
        return True

def add_files_to_git(files=None):
    """Dodaj pliki do Git"""
    if files:
        for file in files:
            print(f"Dodawanie pliku {file} do repozytorium...")
            run_command(f'git add "{file}"')
    else:
        print("Dodawanie wszystkich plików do repozytorium...")
        run_command("git add .")

def commit_files(message=None):
    """Zatwierdź pliki w Git"""
    if not message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Aktualizacja plików dla Render.com ({timestamp})"
    
    print(f"Zatwierdzanie plików z komunikatem: {message}")
    run_command(f'git commit -m "{message}"')

def push_to_remote(branch=None, force=False):
    """Wypchnij zmiany do zdalnego repozytorium"""
    if not branch:
        branch = get_current_branch()
    
    force_flag = "--force" if force else ""
    
    print(f"Wypychanie zmian do zdalnego repozytorium (gałąź: {branch})...")
    output, success = run_command(f"git push {force_flag} origin {branch}")
    
    if not success:
        print("\nWystąpił błąd podczas wypychania zmian.")
        print("Możliwe przyczyny:")
        print("1. Zdalne repozytorium wymaga uwierzytelnienia")
        print("2. Lokalne zmiany kolidują ze zdalnymi zmianami")
        print("3. Brak uprawnień do wypychania zmian do zdalnego repozytorium")
        
        retry = input("\nCzy chcesz spróbować ponownie z opcją --force? (t/n): ")
        if retry.lower() == "t":
            print("Wypychanie zmian z opcją --force...")
            run_command(f"git push --force origin {branch}")

def setup_remote(url=None):
    """Skonfiguruj zdalne repozytorium"""
    if not url:
        print("\nAby zaktualizować pliki na GitHub, potrzebujesz URL repozytorium.")
        print("Format URL: https://github.com/username/repository.git")
        url = input("Podaj URL repozytorium GitHub: ")
    
    # Sprawdź, czy zdalne repozytorium już istnieje
    remote_url = get_remote_url()
    if remote_url:
        print(f"Zdalne repozytorium już skonfigurowane: {remote_url}")
        if remote_url != url:
            change = input("URL zdalnego repozytorium różni się od podanego. Czy chcesz go zmienić? (t/n): ")
            if change.lower() == "t":
                run_command(f'git remote set-url origin "{url}"')
                print(f"URL zdalnego repozytorium został zmieniony na: {url}")
    else:
        print(f"Konfiguracja zdalnego repozytorium: {url}")
        run_command(f'git remote add origin "{url}"')

def list_render_files():
    """Wyświetl listę plików związanych z Render.com"""
    render_files = [
        "render.yaml",
        "wsgi_render.py",
        "RENDER_DEPLOYMENT_GUIDE.md",
        "RENDER_CHECKLIST.md",
        "RENDER_README.md",
        "verify_render_files.py",
        "create_render_zip.py",
        "test_render_websocket.py",
        "render_direct_deploy.py",
        "setup_git_for_render.py",
        "update_github.py"
    ]
    
    existing_files = []
    for file in render_files:
        if os.path.isfile(file):
            existing_files.append(file)
    
    return existing_files

def main():
    """Funkcja główna"""
    print("=== Aktualizacja plików na GitHub ===\n")
    
    # Sprawdź, czy Git jest zainstalowany
    if not is_git_installed():
        print("Git nie jest zainstalowany. Zainstaluj Git i spróbuj ponownie.")
        return
    
    # Sprawdź, czy bieżący katalog jest repozytorium Git
    if not is_git_repository():
        print("Bieżący katalog nie jest repozytorium Git.")
        init = input("Czy chcesz zainicjalizować nowe repozytorium Git? (t/n): ")
        if init.lower() == "t":
            initialize_git_repository()
        else:
            print("Anulowano aktualizację plików na GitHub.")
            return
    
    # Utwórz plik .gitignore
    create_gitignore()
    
    # Skonfiguruj użytkownika Git
    if not configure_git_user():
        print("Nie udało się skonfigurować użytkownika Git.")
        return
    
    # Skonfiguruj zdalne repozytorium
    remote_url = get_remote_url()
    if not remote_url:
        setup_remote()
    
    # Wyświetl listę plików związanych z Render.com
    render_files = list_render_files()
    print("\nZnaleziono następujące pliki związane z Render.com:")
    for i, file in enumerate(render_files, 1):
        print(f"{i}. {file}")
    
    # Zapytaj, które pliki zaktualizować
    update_all = input("\nCzy chcesz zaktualizować wszystkie powyższe pliki? (t/n): ")
    if update_all.lower() == "t":
        files_to_update = render_files
    else:
        print("\nWybierz pliki do aktualizacji (podaj numery oddzielone przecinkami, np. 1,3,5):")
        selection = input("> ")
        try:
            indices = [int(idx.strip()) - 1 for idx in selection.split(",")]
            files_to_update = [render_files[idx] for idx in indices if 0 <= idx < len(render_files)]
        except (ValueError, IndexError):
            print("Nieprawidłowy wybór. Aktualizacja wszystkich plików.")
            files_to_update = render_files
    
    # Dodaj pliki do Git
    add_files_to_git(files_to_update)
    
    # Zatwierdź pliki
    commit_message = input("\nPodaj komunikat commita (lub naciśnij Enter, aby użyć domyślnego): ")
    commit_files(commit_message if commit_message else None)
    
    # Wypchnij zmiany do zdalnego repozytorium
    push = input("\nCzy chcesz wypchnąć zmiany do zdalnego repozytorium? (t/n): ")
    if push.lower() == "t":
        branch = input("Podaj nazwę gałęzi (lub naciśnij Enter, aby użyć bieżącej): ")
        push_to_remote(branch if branch else None)
    
    print("\nAktualizacja plików na GitHub zakończona.")
    remote_url = get_remote_url()
    if remote_url:
        print(f"Sprawdź swoje repozytorium: {remote_url}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika.")
    except Exception as e:
        print(f"\nWystąpił błąd: {e}")
