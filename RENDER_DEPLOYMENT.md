# Instrukcja wdrożenia aplikacji King Of theBay na Render.com

Ta instrukcja zawiera kroki potrzebne do wdrożenia aplikacji King Of theBay na platformie Render.com, która będzie obsługiwać zarówno frontend jak i serwer WebSocket.

## 1. Przygotowanie

### Wymagania

- Konto na [Render.com](https://render.com/)
- Repozytorium Git z kodem aplikacji (opcjonalnie)
- Klucz API Render.com (dla wdrożenia bez Git)

### Pliki konfiguracyjne

W projekcie znajdują się następujące pliki konfiguracyjne dla Render.com:

- `render.yaml` - konfiguracja usługi
- `wsgi_render.py` - plik WSGI dla Render.com
- `requirements.txt` - zależności Pythona
- `render_direct_deploy.py` - skrypt do wdrożenia bez użycia Git

## 2. Wdrożenie na Render.com

### Opcja 1: Wdrożenie z repozytorium Git

1. Zaloguj się do swojego konta na [Render.com](https://dashboard.render.com/)
2. Kliknij przycisk "New" i wybierz "Web Service"
3. Połącz swoje repozytorium Git
4. Render automatycznie wykryje plik `render.yaml` i skonfiguruje usługę
5. Kliknij "Create Web Service"

### Opcja 2: Wdrożenie ręczne przez panel Render.com

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
6. Kliknij "Create Web Service"

### Opcja 3: Wdrożenie bez użycia Git

Jeśli nie masz zainstalowanego Git lub nie chcesz korzystać z repozytorium Git, możesz użyć skryptu `render_direct_deploy.py` do bezpośredniego wdrożenia aplikacji na Render.com:

1. Uzyskaj klucz API Render.com:
   - Zaloguj się do swojego konta na [Render.com](https://dashboard.render.com/)
   - Przejdź do ustawień konta
   - Wygeneruj nowy klucz API

2. Uruchom skrypt wdrożeniowy:
   ```
   python render_direct_deploy.py
   ```

3. Postępuj zgodnie z instrukcjami skryptu:
   - Podaj klucz API Render.com
   - Wybierz, czy chcesz utworzyć nową usługę, czy zaktualizować istniejącą
   - Poczekaj na zakończenie wdrożenia

## 3. Konfiguracja WebSocketów

WebSockety są domyślnie włączone w Render.com, ale warto sprawdzić, czy wszystko działa poprawnie:

1. Po wdrożeniu, otwórz aplikację w przeglądarce
2. Otwórz konsolę przeglądarki (F12)
3. Sprawdź, czy połączenie WebSocket zostało nawiązane
4. Jeśli widzisz błędy, sprawdź logi w panelu Render.com

## 4. Testowanie

1. Otwórz aplikację w przeglądarce używając adresu URL Render.com (np. `https://king-of-the-bay.onrender.com`)
2. Zaloguj się do aplikacji
3. Sprawdź, czy śledzenie GPS działa poprawnie
4. Sprawdź, czy komunikacja między organizatorami a uczestnikami działa

## 5. Rozwiązywanie problemów

### Problem z połączeniem WebSocket

Jeśli masz problemy z połączeniem WebSocket:

1. Sprawdź konsolę przeglądarki, aby zobaczyć błędy
2. Sprawdź logi aplikacji w panelu Render.com
3. Upewnij się, że w pliku `js/tracking-communication.js` jest poprawna obsługa dla Render.com

### Problemy z uruchomieniem aplikacji

Jeśli aplikacja nie uruchamia się:

1. Sprawdź logi w panelu Render.com
2. Upewnij się, że wszystkie zależności są poprawnie zainstalowane
3. Sprawdź, czy plik `wsgi_render.py` jest poprawnie skonfigurowany

## 6. Aktualizacje

Aby zaktualizować aplikację:

1. Zaktualizuj kod w repozytorium Git
2. Render automatycznie wykryje zmiany i wdroży nową wersję
3. Możesz też ręcznie wywołać wdrożenie klikając "Manual Deploy" w panelu Render.com

## 7. Zalety Render.com

- **Pełna obsługa WebSocketów** - Render.com obsługuje WebSockety bez dodatkowej konfiguracji
- **Automatyczne wdrożenia** - zmiany w repozytorium Git są automatycznie wdrażane
- **Skalowanie** - możliwość skalowania aplikacji w miarę potrzeb
- **SSL/TLS** - automatyczne certyfikaty SSL dla bezpiecznych połączeń
- **Monitoring** - monitorowanie zasobów i logów aplikacji
