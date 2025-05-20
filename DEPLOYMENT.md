# Instrukcja wdrożenia aplikacji King Of theBay na PythonAnywhere

Ta instrukcja zawiera kroki potrzebne do wdrożenia aplikacji King Of theBay na platformie PythonAnywhere, która będzie obsługiwać zarówno frontend jak i serwer WebSocket.

## 1. Wdrożenie aplikacji na PythonAnywhere

### Przygotowanie

1. Utwórz konto na [PythonAnywhere](https://www.pythonanywhere.com/) jeśli jeszcze go nie masz.
2. Zaloguj się do swojego konta PythonAnywhere.

### Konfiguracja aplikacji

1. Przejdź do zakładki "Web" i kliknij "Add a new web app".
2. Wybierz "Manual configuration" i wybierz Python 3.9 lub nowszy.
3. Skonfiguruj ścieżkę do pliku WSGI:
   - Edytuj plik WSGI klikając na link do pliku wskazany w konfiguracji.
   - Usuń cały przykładowy kod.
   - Wklej zawartość pliku `wsgi.py` z tego repozytorium.
   - Zapisz plik.

### Przesyłanie plików

#### Opcja 1: Użycie skryptu automatycznego przesyłania

W projekcie znajduje się skrypt `upload_to_pythonanywhere.py`, który automatycznie prześle wszystkie pliki do PythonAnywhere:

1. Zainstaluj wymagane zależności:
   ```
   pip install requests
   ```

2. Uruchom skrypt:
   ```
   python upload_to_pythonanywhere.py
   ```

3. Postępuj zgodnie z instrukcjami w skrypcie:
   - Podaj nazwę użytkownika PythonAnywhere
   - Podaj token API (możesz go wygenerować na stronie https://www.pythonanywhere.com/account/#api_token)
   - Potwierdź ścieżkę docelową

Skrypt automatycznie utworzy wymagane katalogi i prześle wszystkie pliki z zachowaniem struktury.

#### Opcja 2: Ręczne przesyłanie plików

Jeśli wolisz przesłać pliki ręcznie:

1. Przejdź do zakładki "Files" w PythonAnywhere.
2. Przejdź do katalogu swojej aplikacji (zwykle `/home/kuba77/mysite/`).
3. Utwórz następujące podkatalogi:
   ```
   mkdir -p css js data img
   ```
4. Prześlij wszystkie pliki z projektu, zachowując strukturę katalogów:
   - Pliki HTML (*.html) do katalogu głównego
   - Pliki CSS do katalogu `css/`
   - Pliki JavaScript do katalogu `js/`
   - Pliki danych JSON do katalogu `data/`
   - Obrazy do katalogu `img/`
   - Pliki serwera WebSocket:
     - `websocket_server.py`
     - `wsgi.py`
     - `requirements.txt`

### Instalacja zależności

1. Przejdź do zakładki "Consoles" i otwórz nową konsolę Bash.
2. Przejdź do katalogu aplikacji:
   ```
   cd ~/mysite/
   ```
3. Utwórz i aktywuj wirtualne środowisko:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
4. Zainstaluj zależności:
   ```
   pip install -r requirements.txt
   ```

### Konfiguracja aplikacji webowej

1. Wróć do zakładki "Web".
2. W sekcji "Virtualenv" wpisz ścieżkę do utworzonego wirtualnego środowiska:
   ```
   /home/kuba77/mysite/venv
   ```
3. W sekcji "Static files" dodaj mapowanie dla plików statycznych (jeśli potrzebne):
   - URL: `/static/`
   - Directory: `/home/kuba77/mysite/static/`

4. Kliknij przycisk "Reload" aby zrestartować aplikację.

### Konfiguracja HTTPS

PythonAnywhere automatycznie obsługuje HTTPS dla Twojej aplikacji, co jest wymagane dla WebSocketów w przeglądarkach.

## 3. Testowanie

1. Otwórz aplikację w przeglądarce używając adresu URL PythonAnywhere (np. `https://kuba77.pythonanywhere.com`).
2. Aplikacja powinna automatycznie połączyć się z serwerem WebSocket na tej samej domenie.
3. Sprawdź konsolę przeglądarki, aby upewnić się, że połączenie WebSocket działa poprawnie.

## 4. Rozwiązywanie problemów

### Problem z połączeniem WebSocket

Jeśli masz problemy z połączeniem WebSocket:

1. Sprawdź konsolę przeglądarki, aby zobaczyć błędy.
2. Upewnij się, że adres WebSocket w pliku `js/tracking-communication.js` jest poprawny.
3. Sprawdź logi aplikacji w PythonAnywhere (zakładka "Web" > "Log files").

### Problemy z CORS

Jeśli występują problemy z CORS:

1. Edytuj plik `websocket_server.py` i dodaj obsługę CORS.
2. Zrestartuj aplikację w PythonAnywhere.

## 5. Aktualizacje

Aby zaktualizować aplikację:

1. Prześlij zaktualizowane pliki do katalogu aplikacji na PythonAnywhere.
2. W PythonAnywhere kliknij przycisk "Reload" w zakładce "Web".
3. Odśwież stronę w przeglądarce, aby zobaczyć zmiany.
