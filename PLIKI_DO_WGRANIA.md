# Pliki do wgrania na PythonAnywhere

Poniżej znajduje się lista plików i katalogów, które należy wgrać na PythonAnywhere, aby aplikacja działała poprawnie.

## Katalogi

- `css/` - zawiera pliki CSS
- `data/` - zawiera pliki danych JSON
- `img/` - zawiera obrazy
- `js/` - zawiera pliki JavaScript

## Pliki HTML

- `404.html` - strona błędu 404
- `index.html` - strona główna
- `login.html` - strona logowania
- `map-placeholder.html` - placeholder mapy
- `organizer-view.html` - widok organizatora
- `websocket_test.html` - strona testowa WebSocket (opcjonalnie)

## Pliki serwera

- `server.js` - serwer Node.js (opcjonalnie, jeśli używasz tylko PythonAnywhere)
- `websocket_server.py` - serwer WebSocket w Pythonie
- `wsgi.py` - plik konfiguracyjny WSGI dla PythonAnywhere

## Pliki konfiguracyjne

- `package.json` - konfiguracja npm (opcjonalnie)
- `package-lock.json` - lock file npm (opcjonalnie)
- `requirements.txt` - zależności Pythona

## Pliki pomocnicze

- `README.md` - dokumentacja (opcjonalnie)
- `DEPLOYMENT.md` - instrukcja wdrożenia (opcjonalnie)

## Pliki testowe (opcjonalnie)

- `test_websocket_client.py` - klient testowy WebSocket
- `test_websocket_server.py` - serwer testowy WebSocket
- `upload_to_pythonanywhere.py` - skrypt do automatycznego wgrywania plików

## Pliki, których NIE trzeba wgrywać

- `.gitignore` - plik konfiguracyjny Git
- `node_modules/` - zależności Node.js
- `.vercel/` - konfiguracja Vercel
- `vercel.json` - konfiguracja Vercel

## Automatyczne wgrywanie plików

Najłatwiejszym sposobem wgrania wszystkich potrzebnych plików jest użycie skryptu `upload_to_pythonanywhere.py`, który automatycznie wgra wszystkie potrzebne pliki z zachowaniem struktury katalogów.

1. Zainstaluj wymagane zależności:
   ```
   pip install requests
   ```

2. Uruchom skrypt:
   ```
   python upload_to_pythonanywhere.py
   ```

3. Postępuj zgodnie z instrukcjami w skrypcie:
   - Podaj nazwę użytkownika PythonAnywhere (kuba77)
   - Podaj token API (możesz go wygenerować na stronie https://www.pythonanywhere.com/account/#api_token)
   - Potwierdź ścieżkę docelową

Skrypt automatycznie utworzy wymagane katalogi i prześle wszystkie potrzebne pliki.
