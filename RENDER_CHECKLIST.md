# Lista kontrolna wdrożenia na Render.com

Ta lista kontrolna pomoże Ci upewnić się, że masz wszystkie niezbędne pliki i konfiguracje przed wdrożeniem aplikacji King Of theBay na platformę Render.com.

## Pliki konfiguracyjne Render.com

- [ ] `render.yaml` - konfiguracja usługi
- [ ] `wsgi_render.py` - plik WSGI dla Render.com
- [ ] `requirements.txt` - zależności Pythona

## Pliki backendu

- [ ] `websocket_server.py` - serwer WebSocket w Pythonie

## Pliki frontendu

### Pliki HTML
- [ ] `index.html` - strona główna
- [ ] `login.html` - strona logowania
- [ ] `organizer-view.html` - widok organizatora
- [ ] `404.html` - strona błędu 404
- [ ] `map-placeholder.html` - placeholder mapy

### Katalogi
- [ ] `css/` - pliki CSS
- [ ] `js/` - pliki JavaScript
- [ ] `img/` - obrazy
- [ ] `data/` - pliki JSON

## Konfiguracja WebSocket

- [ ] Sprawdzono, czy w pliku `js/tracking-communication.js` jest obsługa Render.com
- [ ] Sprawdzono, czy w pliku `render.yaml` opcja `websocket` jest ustawiona na `true`
- [ ] Sprawdzono, czy w pliku `wsgi_render.py` serwer WebSocket jest uruchamiany poprawnie

## Metoda wdrożenia

Wybierz jedną z metod wdrożenia:

- [ ] **Wdrożenie przez Git**
  - [ ] Repozytorium Git jest skonfigurowane (GitHub, GitLab, Bitbucket)
  - [ ] Kod jest wysłany do repozytorium za pomocą skryptu `setup_git_for_render.py` lub `update_github.py`
  - [ ] Masz dostęp do konta Render.com

- [ ] **Wdrożenie ręczne przez panel Render.com**
  - [ ] Masz dostęp do konta Render.com
  - [ ] Skrypt `create_render_zip.py` jest dostępny
  - [ ] Utworzono archiwum ZIP z plikami aplikacji za pomocą skryptu

- [ ] **Wdrożenie bezpośrednie bez Git**
  - [ ] Zainstalowano wymagane zależności Pythona (`requests`)
  - [ ] Wygenerowano klucz API Render.com
  - [ ] Skrypt `render_direct_deploy.py` jest dostępny

## Przed wdrożeniem

- [ ] Sprawdzono, czy wszystkie pliki są zaktualizowane
- [ ] Sprawdzono, czy aplikacja działa lokalnie
- [ ] Przetestowano konfigurację WebSocket za pomocą skryptu `test_render_websocket.py`
- [ ] Sprawdzono, czy wszystkie zależności są wymienione w pliku `requirements.txt`
- [ ] Sprawdzono, czy konfiguracja w pliku `render.yaml` jest poprawna
- [ ] Uruchomiono skrypt `verify_render_files.py` i poprawiono wszystkie błędy

## Po wdrożeniu

- [ ] Sprawdzono, czy aplikacja jest dostępna pod adresem URL Render.com
- [ ] Sprawdzono, czy połączenie WebSocket działa poprawnie
- [ ] Sprawdzono, czy wszystkie funkcje aplikacji działają poprawnie
- [ ] Sprawdzono logi aplikacji w panelu Render.com

## Notatki

- Adres URL aplikacji: https://king-of-the-bay.onrender.com (lub inny)
- Data wdrożenia: ________________
- Wersja aplikacji: ________________
- Dodatkowe uwagi: ________________
