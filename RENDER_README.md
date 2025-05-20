# Wdrożenie aplikacji King Of theBay na Render.com

Ten katalog zawiera pliki i narzędzia potrzebne do wdrożenia aplikacji King Of theBay na platformie Render.com.

## Pliki pomocnicze

W ramach przygotowania do wdrożenia na Render.com, utworzono następujące pliki pomocnicze:

1. **RENDER_DEPLOYMENT_GUIDE.md** - Szczegółowa instrukcja wdrożenia aplikacji na Render.com, zawierająca:
   - Przygotowanie plików
   - Metody wdrożenia (przez Git, ręcznie, bezpośrednio)
   - Weryfikację wdrożenia
   - Rozwiązywanie problemów
   - Aktualizację aplikacji

2. **RENDER_CHECKLIST.md** - Lista kontrolna do sprawdzenia przed wdrożeniem, zawierająca:
   - Wymagane pliki konfiguracyjne
   - Wymagane pliki backendu i frontendu
   - Konfigurację WebSocket
   - Metody wdrożenia
   - Czynności do wykonania przed i po wdrożeniu

3. **verify_render_files.py** - Skrypt weryfikujący pliki do wdrożenia, który:
   - Sprawdza obecność wszystkich wymaganych plików
   - Weryfikuje poprawność konfiguracji w plikach
   - Wyświetla podsumowanie gotowości do wdrożenia

## Pliki konfiguracyjne Render.com

Aplikacja zawiera już następujące pliki konfiguracyjne dla Render.com:

1. **render.yaml** - Konfiguracja usługi na Render.com
2. **wsgi_render.py** - Plik WSGI dla Render.com, obsługujący zarówno statyczne pliki, jak i serwer WebSocket
3. **requirements.txt** - Lista zależności Pythona

## Narzędzia do wdrożenia

Aplikacja zawiera również narzędzia do wdrożenia na Render.com:

1. **setup_git_for_render.py** - Skrypt do przygotowania repozytorium Git dla wdrożenia przez Git
2. **render_direct_deploy.py** - Skrypt do bezpośredniego wdrożenia bez użycia Git
3. **create_render_zip.py** - Skrypt do tworzenia archiwum ZIP z plikami do wdrożenia ręcznego
4. **verify_render_files.py** - Skrypt weryfikujący pliki do wdrożenia
5. **test_render_websocket.py** - Skrypt do testowania konfiguracji WebSocket lokalnie przed wdrożeniem
6. **update_github.py** - Skrypt do aktualizacji plików na GitHub

## Jak zacząć

1. Przeczytaj **RENDER_DEPLOYMENT_GUIDE.md**, aby zapoznać się z procesem wdrożenia
2. Użyj **verify_render_files.py**, aby sprawdzić, czy wszystkie pliki są gotowe do wdrożenia:
   ```
   python verify_render_files.py
   ```
3. Przetestuj konfigurację WebSocket lokalnie za pomocą skryptu:
   ```
   python test_render_websocket.py
   ```
4. Przejrzyj **RENDER_CHECKLIST.md** i upewnij się, że wszystkie punkty są spełnione
5. Wybierz jedną z metod wdrożenia opisanych w instrukcji i postępuj zgodnie z krokami

## Metody wdrożenia

### Metoda 1: Wdrożenie przez Git (zalecana)

Użyj skryptu `setup_git_for_render.py`, aby utworzyć repozytorium Git i wysłać kod do GitHub lub GitLab, a następnie połącz to repozytorium z Render.com.

```
python setup_git_for_render.py
```

Po wprowadzeniu zmian w kodzie, możesz zaktualizować pliki na GitHub za pomocą skryptu:

```
python update_github.py
```

### Metoda 2: Wdrożenie ręczne przez panel Render.com

Użyj skryptu `create_render_zip.py`, aby utworzyć archiwum ZIP z plikami aplikacji, a następnie ręcznie skonfiguruj usługę w panelu Render.com i prześlij to archiwum.

```
python create_render_zip.py
```

### Metoda 3: Wdrożenie bezpośrednie bez Git

Użyj skryptu `render_direct_deploy.py`, aby bezpośrednio wdrożyć aplikację na Render.com bez użycia Git.

```
python render_direct_deploy.py
```

## Wsparcie

W przypadku problemów z wdrożeniem, sprawdź sekcję "Rozwiązywanie problemów" w pliku **RENDER_DEPLOYMENT_GUIDE.md** lub skontaktuj się z administratorem aplikacji.
