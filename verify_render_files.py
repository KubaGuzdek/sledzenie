#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Skrypt weryfikujący pliki do wdrożenia na Render.com
Ten skrypt sprawdza, czy wszystkie niezbędne pliki do wdrożenia na Render.com są obecne
i czy mają poprawną konfigurację.
"""

import os
import sys
import json
import yaml
import re

def check_file_exists(file_path, description):
    """Sprawdza, czy plik istnieje"""
    exists = os.path.isfile(file_path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists

def check_directory_exists(dir_path, description):
    """Sprawdza, czy katalog istnieje"""
    exists = os.path.isdir(dir_path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dir_path}")
    return exists

def check_render_yaml():
    """Sprawdza konfigurację w pliku render.yaml"""
    if not os.path.isfile("render.yaml"):
        print("❌ Brak pliku render.yaml")
        return False
    
    try:
        with open("render.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        if not config or "services" not in config:
            print("❌ Niepoprawna struktura pliku render.yaml (brak sekcji 'services')")
            return False
        
        services = config["services"]
        if not services or not isinstance(services, list):
            print("❌ Niepoprawna struktura pliku render.yaml (sekcja 'services' nie jest listą)")
            return False
        
        web_service = None
        for service in services:
            if service.get("type") == "web":
                web_service = service
                break
        
        if not web_service:
            print("❌ Brak usługi typu 'web' w pliku render.yaml")
            return False
        
        # Sprawdź wymagane pola
        required_fields = ["name", "env", "buildCommand", "startCommand"]
        for field in required_fields:
            if field not in web_service:
                print(f"❌ Brak pola '{field}' w usłudze 'web' w pliku render.yaml")
                return False
        
        # Sprawdź, czy websocket jest włączony
        if "websocket" not in web_service or not web_service["websocket"]:
            print("⚠️ WebSocket nie jest włączony w pliku render.yaml")
        
        print("✅ Plik render.yaml ma poprawną strukturę")
        return True
    
    except Exception as e:
        print(f"❌ Błąd podczas analizy pliku render.yaml: {e}")
        return False

def check_wsgi_render_py():
    """Sprawdza konfigurację w pliku wsgi_render.py"""
    if not os.path.isfile("wsgi_render.py"):
        print("❌ Brak pliku wsgi_render.py")
        return False
    
    try:
        with open("wsgi_render.py", "r") as f:
            content = f.read()
        
        # Sprawdź, czy plik importuje TrackingServer
        if "from websocket_server import TrackingServer" not in content:
            print("❌ Brak importu TrackingServer w pliku wsgi_render.py")
            return False
        
        # Sprawdź, czy plik uruchamia serwer WebSocket
        if "websockets.serve" not in content:
            print("❌ Brak uruchomienia serwera WebSocket w pliku wsgi_render.py")
            return False
        
        # Sprawdź, czy plik obsługuje pliki statyczne
        if "serve static files" not in content.lower():
            print("⚠️ Możliwy brak obsługi plików statycznych w pliku wsgi_render.py")
        
        print("✅ Plik wsgi_render.py ma poprawną konfigurację")
        return True
    
    except Exception as e:
        print(f"❌ Błąd podczas analizy pliku wsgi_render.py: {e}")
        return False

def check_requirements_txt():
    """Sprawdza zależności w pliku requirements.txt"""
    if not os.path.isfile("requirements.txt"):
        print("❌ Brak pliku requirements.txt")
        return False
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        # Lista wymaganych zależności
        required_dependencies = ["websockets", "asyncio", "aiohttp"]
        
        missing_dependencies = []
        for dep in required_dependencies:
            if dep not in content:
                missing_dependencies.append(dep)
        
        if missing_dependencies:
            print(f"❌ Brak wymaganych zależności w pliku requirements.txt: {', '.join(missing_dependencies)}")
            return False
        
        print("✅ Plik requirements.txt zawiera wymagane zależności")
        return True
    
    except Exception as e:
        print(f"❌ Błąd podczas analizy pliku requirements.txt: {e}")
        return False

def check_tracking_communication_js():
    """Sprawdza konfigurację w pliku js/tracking-communication.js"""
    file_path = "js/tracking-communication.js"
    if not os.path.isfile(file_path):
        print(f"❌ Brak pliku {file_path}")
        return False
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        # Sprawdź, czy plik obsługuje Render.com
        if "window.location.hostname.includes('onrender.com')" not in content:
            print(f"❌ Brak obsługi Render.com w pliku {file_path}")
            return False
        
        print(f"✅ Plik {file_path} ma obsługę Render.com")
        return True
    
    except Exception as e:
        print(f"❌ Błąd podczas analizy pliku {file_path}: {e}")
        return False

def main():
    """Główna funkcja"""
    print("=== Weryfikacja plików do wdrożenia na Render.com ===\n")
    
    # Sprawdź pliki konfiguracyjne Render.com
    print("\n== Pliki konfiguracyjne Render.com ==")
    render_yaml_exists = check_file_exists("render.yaml", "Plik konfiguracyjny Render.com")
    wsgi_render_py_exists = check_file_exists("wsgi_render.py", "Plik WSGI dla Render.com")
    requirements_txt_exists = check_file_exists("requirements.txt", "Plik z zależnościami Pythona")
    
    # Sprawdź pliki backendu
    print("\n== Pliki backendu ==")
    websocket_server_exists = check_file_exists("websocket_server.py", "Serwer WebSocket")
    
    # Sprawdź pliki frontendu
    print("\n== Pliki HTML ==")
    html_files = [
        ("index.html", "Strona główna"),
        ("login.html", "Strona logowania"),
        ("organizer-view.html", "Widok organizatora"),
        ("404.html", "Strona błędu 404"),
        ("map-placeholder.html", "Placeholder mapy")
    ]
    
    html_exists = True
    for file_path, description in html_files:
        if not check_file_exists(file_path, description):
            html_exists = False
    
    # Sprawdź katalogi
    print("\n== Katalogi ==")
    directories = [
        ("css", "Katalog CSS"),
        ("js", "Katalog JavaScript"),
        ("img", "Katalog obrazów"),
        ("data", "Katalog danych")
    ]
    
    directories_exist = True
    for dir_path, description in directories:
        if not check_directory_exists(dir_path, description):
            directories_exist = False
    
    # Sprawdź szczegółową konfigurację
    print("\n== Szczegółowa weryfikacja konfiguracji ==")
    
    if render_yaml_exists:
        render_yaml_valid = check_render_yaml()
    else:
        render_yaml_valid = False
    
    if wsgi_render_py_exists:
        wsgi_render_py_valid = check_wsgi_render_py()
    else:
        wsgi_render_py_valid = False
    
    if requirements_txt_exists:
        requirements_txt_valid = check_requirements_txt()
    else:
        requirements_txt_valid = False
    
    if os.path.isdir("js"):
        tracking_communication_valid = check_tracking_communication_js()
    else:
        tracking_communication_valid = False
    
    # Podsumowanie
    print("\n== Podsumowanie ==")
    
    all_files_exist = (
        render_yaml_exists and 
        wsgi_render_py_exists and 
        requirements_txt_exists and 
        websocket_server_exists and 
        html_exists and 
        directories_exist
    )
    
    all_configs_valid = (
        render_yaml_valid and 
        wsgi_render_py_valid and 
        requirements_txt_valid and 
        tracking_communication_valid
    )
    
    if all_files_exist:
        print("✅ Wszystkie wymagane pliki są obecne")
    else:
        print("❌ Brakuje niektórych wymaganych plików")
    
    if all_configs_valid:
        print("✅ Wszystkie pliki konfiguracyjne mają poprawną strukturę")
    else:
        print("❌ Niektóre pliki konfiguracyjne mają niepoprawną strukturę")
    
    if all_files_exist and all_configs_valid:
        print("\n✅ Wszystko jest gotowe do wdrożenia na Render.com!")
        print("Możesz teraz użyć jednej z metod wdrożenia opisanych w pliku RENDER_DEPLOYMENT_GUIDE.md")
    else:
        print("\n❌ Przed wdrożeniem na Render.com należy poprawić błędy wymienione powyżej")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika")
    except Exception as e:
        print(f"\nWystąpił nieoczekiwany błąd: {e}")
