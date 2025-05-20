#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup Git repository for Render.com deployment
This script helps create a Git repository and push the code to GitHub or GitLab
"""

import os
import sys
import subprocess
import getpass
import json
from pathlib import Path

def run_command(command, show_output=True):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, 
                               capture_output=True)
        if show_output and result.stdout:
            print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas wykonywania komendy: {command}")
        print(f"Kod błędu: {e.returncode}")
        if e.stdout:
            print(f"Standardowe wyjście: {e.stdout}")
        if e.stderr:
            print(f"Błąd: {e.stderr}")
        return None

def is_git_installed():
    """Check if Git is installed"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_git_repository():
    """Check if the current directory is a Git repository"""
    return os.path.isdir(".git")

def initialize_git_repository():
    """Initialize a new Git repository"""
    print("Inicjalizacja repozytorium Git...")
    run_command("git init")

def create_gitignore():
    """Create a .gitignore file if it doesn't exist"""
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

def add_files_to_git():
    """Add all files to Git"""
    print("Dodawanie plików do repozytorium...")
    run_command("git add .")

def commit_files():
    """Commit files to Git"""
    print("Zatwierdzanie plików...")
    run_command('git commit -m "Initial commit for Render.com deployment"')

def configure_git_user():
    """Configure Git user if not already configured"""
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

def setup_github_repository():
    """Setup a GitHub repository"""
    print("\n=== Konfiguracja repozytorium GitHub ===")
    print("Aby utworzyć repozytorium na GitHub, potrzebujesz konta GitHub i tokenu dostępu.")
    print("Token możesz wygenerować na stronie: https://github.com/settings/tokens")
    
    use_github = input("Czy chcesz utworzyć repozytorium na GitHub? (t/n): ")
    if use_github.lower() != "t":
        return False
    
    github_username = input("Podaj nazwę użytkownika GitHub: ")
    repo_name = input("Podaj nazwę repozytorium (domyślnie: king-of-the-bay): ") or "king-of-the-bay"
    repo_description = input("Podaj opis repozytorium (opcjonalnie): ")
    is_private = input("Czy repozytorium ma być prywatne? (t/n): ").lower() == "t"
    
    github_token = getpass.getpass("Podaj token dostępu GitHub: ")
    
    # Create repository on GitHub
    print(f"Tworzenie repozytorium {repo_name} na GitHub...")
    
    import requests
    
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": repo_description,
        "private": is_private
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Repozytorium zostało utworzone na GitHub.")
        repo_url = response.json()["clone_url"]
        
        # Add remote
        run_command(f'git remote add origin {repo_url}')
        
        # Push to GitHub
        print("Wysyłanie kodu do GitHub...")
        run_command(f'git push -u origin master')
        
        print(f"\nRepozytorium zostało utworzone i kod został wysłany do GitHub.")
        print(f"URL repozytorium: {repo_url}")
        print(f"Możesz teraz połączyć to repozytorium z Render.com.")
        
        return True
    else:
        print(f"Błąd podczas tworzenia repozytorium: {response.status_code}")
        print(response.json())
        return False

def setup_gitlab_repository():
    """Setup a GitLab repository"""
    print("\n=== Konfiguracja repozytorium GitLab ===")
    print("Aby utworzyć repozytorium na GitLab, potrzebujesz konta GitLab i tokenu dostępu.")
    print("Token możesz wygenerować na stronie: https://gitlab.com/-/profile/personal_access_tokens")
    
    use_gitlab = input("Czy chcesz utworzyć repozytorium na GitLab? (t/n): ")
    if use_gitlab.lower() != "t":
        return False
    
    gitlab_username = input("Podaj nazwę użytkownika GitLab: ")
    repo_name = input("Podaj nazwę repozytorium (domyślnie: king-of-the-bay): ") or "king-of-the-bay"
    repo_description = input("Podaj opis repozytorium (opcjonalnie): ")
    is_private = input("Czy repozytorium ma być prywatne? (t/n): ").lower() == "t"
    
    gitlab_token = getpass.getpass("Podaj token dostępu GitLab: ")
    
    # Create repository on GitLab
    print(f"Tworzenie repozytorium {repo_name} na GitLab...")
    
    import requests
    
    url = "https://gitlab.com/api/v4/projects"
    headers = {
        "PRIVATE-TOKEN": gitlab_token
    }
    data = {
        "name": repo_name,
        "description": repo_description,
        "visibility": "private" if is_private else "public"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Repozytorium zostało utworzone na GitLab.")
        repo_url = response.json()["http_url_to_repo"]
        
        # Add remote
        run_command(f'git remote add origin {repo_url}')
        
        # Push to GitLab
        print("Wysyłanie kodu do GitLab...")
        run_command(f'git push -u origin master')
        
        print(f"\nRepozytorium zostało utworzone i kod został wysłany do GitLab.")
        print(f"URL repozytorium: {repo_url}")
        print(f"Możesz teraz połączyć to repozytorium z Render.com.")
        
        return True
    else:
        print(f"Błąd podczas tworzenia repozytorium: {response.status_code}")
        print(response.json())
        return False

def main():
    """Main function"""
    print("=== Przygotowanie repozytorium Git dla wdrożenia na Render.com ===")
    
    # Check if Git is installed
    if not is_git_installed():
        print("Git nie jest zainstalowany. Zainstaluj Git i spróbuj ponownie.")
        return
    
    # Check if the current directory is a Git repository
    if not is_git_repository():
        initialize_git_repository()
    else:
        print("Katalog jest już repozytorium Git.")
    
    # Create .gitignore
    create_gitignore()
    
    # Configure Git user
    configure_git_user()
    
    # Add files to Git
    add_files_to_git()
    
    # Commit files
    commit_files()
    
    # Setup remote repository
    print("\nAby wdrożyć aplikację na Render.com, potrzebujesz repozytorium Git na GitHub lub GitLab.")
    
    # Try GitHub first
    if setup_github_repository():
        print("\nRepozytorium GitHub zostało skonfigurowane.")
    # If GitHub fails or user declines, try GitLab
    elif setup_gitlab_repository():
        print("\nRepozytorium GitLab zostało skonfigurowane.")
    else:
        print("\nNie skonfigurowano zdalnego repozytorium.")
        print("Możesz ręcznie utworzyć repozytorium na GitHub lub GitLab i połączyć je z lokalnym repozytorium.")
    
    print("\nPrzygotowanie repozytorium Git zakończone.")
    print("Teraz możesz wdrożyć aplikację na Render.com zgodnie z instrukcją w pliku RENDER_DEPLOYMENT.md.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika.")
    except Exception as e:
        print(f"\nWystąpił błąd: {e}")
