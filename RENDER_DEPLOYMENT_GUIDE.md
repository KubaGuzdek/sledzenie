# Instrukcja wdrożenia aplikacji King Of theBay na Render.com

Ta instrukcja zawiera szczegółowe kroki potrzebne do wdrożenia aplikacji King Of theBay na platformie Render.com. Aplikacja składa się z frontendu (HTML, CSS, JS) oraz backendu (serwer WebSocket w Pythonie).

## Spis treści

1. [Przygotowanie plików](#1-przygotowanie-plików)
2. [Metody wdrożenia](#2-metody-wdrożenia)
   - [Wdrożenie przez Git](#opcja-1-wdrożenie-przez-git)
   - [Wdrożenie ręczne przez panel Render.com](#opcja-2-wdrożenie-ręczne-przez-panel-rendercom)
   - [Wdrożenie bezpośrednie bez Git](#opcja-3-wdrożenie-bezpośrednie-bez-git)
3. [Weryfikacja wdrożenia](#3-weryfikacja-wdrożenia)
4. [Rozwiązywanie problemów](#4-rozwiązywanie-problemów)
5. [Aktualizacja aplikacji](#5-aktualizacja-aplikacji)

## 1. Przygotowanie plików

Przed wdrożeniem aplikacji na Render.com, upewnij się, że masz wszystkie niezbędne pliki i przetestuj konfigurację lokalnie:

### Pliki wymagane do wdrożenia

- **Pliki konfiguracyjne Render.com**:
  - `render.yaml` - konfiguracja usługi
  - `wsgi_render.py` - plik WSGI dla Render.com
  - `requirements.txt` - zależności Pythona

- **Pliki backendu**:
  - `websocket_server.py` - serwer WebSocket w Pythonie

- **Pliki frontendu**:
  - Pliki HTML: `index.html`, `login.html`, `organizer-view.html`, `404.html`, `map-placeholder.html`
  - Katalog `css/` z plikami CSS
  - Katalog `js/` z plikami JavaScript
  - Katalog `img/` z obrazami
  - Katalog `data/` z plikami JSON

### Sprawdzenie konfiguracji

1. Upewnij się, że plik `render.yaml` zawiera poprawną konfigurację:
   ```yaml
   services:
     - type: web
       name: king-of-the-bay
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python wsgi_render.py
       envVars:
         - key: PYTHON_VERSION
           value: 3.9.0
       healthCheckPath: /
       websocket: true
   ```

2. Sprawdź, czy plik `wsgi_render.py` jest skonfigurowany do obsługi zarówno statycznych plików, jak i połączeń WebSocket.

3. Upewnij się, że plik `requirements.txt` zawiera wszystkie wymagane zależności:
   ```
   websockets==11.0.3
   asyncio==3.4.3
   flask==2.3.3
   werkzeug==2.3.7
   requests==2.31.0
   aiohttp==3.9.1
   gunicorn==21.2.0
   ```

4. Sprawdź, czy plik `js/tracking-communication.js` zawiera obsługę Render.com:
   ```javascript
   if (window.location.hostname.includes('onrender.com')) {
       // We're on Render.com, use WebSocket server on the same domain
       const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
       url = `${protocol}//${window.location.host}`;
       console.log('Using Render.com WebSocket server');
   }
   ```

5. Przetestuj konfigurację WebSocket lokalnie za pomocą skryptu `test_render_websocket.py`:
   ```
   python test_render_websocket.py
   ```
   
   Skrypt uruchomi lokalny serwer HTTP i WebSocket, a następnie otworzy przeglądarkę z testową stroną, która pozwoli sprawdzić, czy połączenie WebSocket działa poprawnie.

6. Użyj skryptu `verify_render_files.py` do sprawdzenia, czy wszystkie pliki są gotowe do wdrożenia:
   ```
   python verify_render_files.py
   ```
   
   Skrypt sprawdzi obecność wszystkich wymaganych plików i poprawność konfiguracji.

## 2. Metody wdrożenia

Istnieją trzy główne metody wdrożenia aplikacji na Render.com:

### Opcja 1: Wdrożenie przez Git

Ta metoda wymaga repozytorium Git (GitHub, GitLab, Bitbucket).

1. **Przygotowanie repozytorium Git**:
   - Użyj skryptu `setup_git_for_render.py`, aby utworzyć repozytorium Git i wysłać kod do GitHub lub GitLab:
     ```
     python setup_git_for_render.py
     ```
   - Postępuj zgodnie z instrukcjami skryptu:
     - Podaj dane do konfiguracji Git
     - Wybierz platformę (GitHub lub GitLab)
     - Podaj nazwę użytkownika i token dostępu
     - Podaj nazwę i opis repozytorium

2. **Wdrożenie na Render.com**:
   - Zaloguj się do swojego konta na [Render.com](https://dashboard.render.com/)
   - Kliknij przycisk "New" i wybierz "Web Service"
   - Wybierz opcję "Connect a repository"
   - Wybierz swoje repozytorium z listy
   - Render automatycznie wykryje plik `render.yaml` i skonfiguruje usługę
   - Kliknij "Create Web Service"

### Opcja 2: Wdrożenie ręczne przez panel Render.com

Ta metoda nie wymaga repozytorium Git, ale wymaga ręcznej konfiguracji usługi.

1. Zaloguj się do swojego konta na [Render.com](https://dashboard.render.com/)
2. Kliknij przycisk "New" i wybierz "Web Service"
3. Wybierz opcję "Build and deploy from source"
4. Wprowadź następujące ustawienia:
   - **Name**: king-of-the-bay
   - **Environment**: Python
   - **Region**: Frankfurt (lub najbliższy region)
   - **Branch**: main (lub inna gałąź)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python wsgi_render.py`
5. W sekcji "Advanced" dodaj następujące zmienne środowiskowe:
   - **PYTHON_VERSION**: 3.9.0
6. W sekcji "Advanced" włącz obsługę WebSocketów
7. Kliknij "Create Web Service"
8. Po utworzeniu usługi, przejdź do zakładki "Manual Deploy" i wybierz opcję "Upload Files"
9. Użyj skryptu `create_render_zip.py` do utworzenia archiwum ZIP z plikami aplikacji:
   ```
   python create_render_zip.py
   ```
10. Prześlij utworzone archiwum ZIP do Render.com

### Opcja 3: Wdrożenie bezpośrednie bez Git

Ta metoda wykorzystuje skrypt `render_direct_deploy.py` do bezpośredniego wdrożenia aplikacji na Render.com bez użycia Git.

1. **Uzyskaj klucz API Render.com**:
   - Zaloguj się do swojego konta na [Render.com](https://dashboard.render.com/)
   - Przejdź do ustawień konta (Account Settings)
   - W sekcji "API Keys" kliknij "Create API Key"
   - Skopiuj wygenerowany klucz API

2. **Uruchom skrypt wdrożeniowy**:
   ```
   python render_direct_deploy.py
   ```

3. **Postępuj zgodnie z instrukcjami skryptu**:
   - Podaj klucz API Render.com
   - Wybierz, czy chcesz utworzyć nową usługę, czy zaktualizować istniejącą
   - Podaj nazwę usługi (np. king-of-the-bay)
   - Poczekaj na zakończenie wdrożenia

## 3. Weryfikacja wdrożenia

Po wdrożeniu aplikacji na Render.com, należy sprawdzić, czy wszystko działa poprawnie:

1. **Otwórz aplikację w przeglądarce**:
   - Przejdź do adresu URL Render.com (np. `https://king-of-the-bay.onrender.com`)
   - Sprawdź, czy strona główna ładuje się poprawnie

2. **Sprawdź połączenie WebSocket**:
   - Otwórz konsolę przeglądarki (F12)
   - Sprawdź, czy w logach pojawia się komunikat "Connected to tracking server"
   - Sprawdź, czy nie ma błędów związanych z połączeniem WebSocket

3. **Przetestuj funkcjonalność**:
   - Zaloguj się do aplikacji
   - Sprawdź, czy śledzenie GPS działa poprawnie
   - Sprawdź, czy komunikacja między organizatorami a uczestnikami działa

## 4. Rozwiązywanie problemów

### Problem z połączeniem WebSocket

Jeśli masz problemy z połączeniem WebSocket:

1. **Sprawdź konfigurację WebSocket w Render.com**:
   - Przejdź do ustawień usługi na Render.com
   - Upewnij się, że opcja "WebSockets" jest włączona

2. **Sprawdź logi aplikacji**:
   - Przejdź do zakładki "Logs" w panelu Render.com
   - Sprawdź, czy nie ma błędów związanych z uruchomieniem serwera WebSocket

3. **Sprawdź konfigurację w kodzie**:
   - Upewnij się, że plik `js/tracking-communication.js` poprawnie obsługuje Render.com
   - Sprawdź, czy w pliku `wsgi_render.py` serwer WebSocket jest uruchamiany na odpowiednim porcie

### Problemy z uruchomieniem aplikacji

Jeśli aplikacja nie uruchamia się:

1. **Sprawdź logi budowania**:
   - Przejdź do zakładki "Events" w panelu Render.com
   - Sprawdź, czy nie ma błędów podczas instalacji zależności

2. **Sprawdź logi aplikacji**:
   - Przejdź do zakładki "Logs" w panelu Render.com
   - Sprawdź, czy nie ma błędów podczas uruchamiania aplikacji

3. **Sprawdź zależności**:
   - Upewnij się, że plik `requirements.txt` zawiera wszystkie wymagane zależności
   - Sprawdź, czy wersje zależności są kompatybilne ze sobą

## 5. Aktualizacja aplikacji

Aby zaktualizować aplikację na Render.com:

### Aktualizacja przez Git

Jeśli wdrożyłeś aplikację przez Git:

1. Wprowadź zmiany w kodzie
2. Użyj skryptu `update_github.py` do aktualizacji plików na GitHub:
   ```
   python update_github.py
   ```
   
   Skrypt przeprowadzi Cię przez proces:
   - Wyboru plików do aktualizacji
   - Dodania plików do repozytorium
   - Zatwierdzenia zmian z odpowiednim komunikatem
   - Wypchnięcia zmian do zdalnego repozytorium

3. Render automatycznie wykryje zmiany i wdroży nową wersję

### Aktualizacja bezpośrednia

Jeśli wdrożyłeś aplikację bezpośrednio:

1. Wprowadź zmiany w kodzie
2. Uruchom skrypt `render_direct_deploy.py`:
   ```
   python render_direct_deploy.py
   ```
3. Postępuj zgodnie z instrukcjami skryptu, wybierając opcję aktualizacji istniejącej usługi

### Aktualizacja ręczna

Jeśli wdrożyłeś aplikację ręcznie:

1. Wprowadź zmiany w kodzie
2. Spakuj wszystkie pliki aplikacji do archiwum ZIP
3. Przejdź do zakładki "Manual Deploy" w panelu Render.com
4. Wybierz opcję "Upload Files" i prześlij archiwum ZIP
