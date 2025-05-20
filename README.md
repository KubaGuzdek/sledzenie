# King Of theBay - Aplikacja do śledzenia GPS

Interfejs aplikacji mobilnej do śledzenia GPS w czasie rzeczywistym dla uczestników zawodów Wingfoil "King Of theBay".

## Opis projektu

Ten projekt przedstawia interaktywny prototyp interfejsu aplikacji mobilnej do śledzenia GPS dla zawodników Wingfoil. Interfejs został zaprojektowany z myślą o użytkowaniu w trudnych warunkach - mokrymi rękami i w pełnym słońcu, dlatego posiada duże, czytelne elementy dotykowe i wysoki kontrast.

## Funkcjonalności

Aplikacja zawiera następujące ekrany:

1. **Ekran główny** - pokazuje status sygnału GPS, przycisk "Rozpocznij śledzenie" oraz informacje o stanie baterii i sieci.
2. **Mapa na żywo** - prezentuje aktualną lokalizację zawodnika na mapie w czasie rzeczywistym, wraz z przyciskiem "Wyślij SOS".
3. **Ekran gotowości** - umożliwia zawodnikowi potwierdzenie gotowości przed startem, wyświetla odliczanie lub komunikat "oczekiwanie na start".
4. **Wyniki zawodów** - pokazuje aktualną pozycję zawodnika w klasyfikacji oraz pełne wyniki wszystkich uczestników.
5. **Ustawienia** - pozwala na edycję profilu (imię, numer żagla, kolor śledzenia).
6. **Podsumowanie trasy** - po zakończeniu śledzenia pokazuje przebytą trasę na mapie, dystans, średnią prędkość, maksymalną prędkość i czas trwania.

## Technologie

Prototyp został zbudowany przy użyciu:
- HTML5
- CSS3
- JavaScript

## Jak uruchomić

Aby uruchomić prototyp:

1. Otwórz plik `index.html` w przeglądarce internetowej.
2. Interfejs jest responsywny i najlepiej wygląda na urządzeniach mobilnych lub w trybie responsywnym przeglądarki.

## Interaktywne elementy

Prototyp zawiera następujące interaktywne elementy:

- Przełączanie między ekranami za pomocą menu nawigacyjnego lub przycisków
- Wybór koloru śledzenia w ustawieniach
- Symulacja odliczania na ekranie gotowości
- Przycisk SOS z alertem
- Wyświetlanie trasy na mapie

## Styl i design

Aplikacja wykorzystuje nowoczesny, sportowy design z następującymi cechami:

- Duże przyciski i elementy dotykowe dla łatwej obsługi mokrymi rękami
- Wysoki kontrast dla dobrej widoczności w pełnym słońcu
- Kolory przewodnie: morski niebieski, biały i czarny
- Czytelne ikony i teksty

## Struktura projektu

- `index.html` - interfejs dla zawodników
- `organizer-view.html` - panel organizatora zawodów
- `css/styles.css` - arkusz stylów CSS
- `map-placeholder.html` - przykładowe mapy (pomocniczy plik do wizualizacji)
- `img/` - folder na logo zawodów i inne grafiki
- `README.md` - dokumentacja projektu

## Panel Organizatora

Projekt zawiera również panel organizatora zawodów, który umożliwia:

- Śledzenie wszystkich zawodników na jednej mapie w czasie rzeczywistym
- Monitorowanie statusu GPS każdego zawodnika
- Natychmiastowe powiadomienia o sygnałach SOS
- Filtrowanie zawodników według statusu (wszyscy, na trasie, oczekujący, SOS)
- Zarządzanie wyścigiem (start, wstrzymanie, zakończenie)
- Zarządzanie wynikami wyścigów (dodawanie, edycja, publikacja)
- Wysyłanie komunikatów do zawodników

Panel organizatora jest dostępny w pliku `organizer-view.html` i stanowi uzupełnienie aplikacji mobilnej dla zawodników. Dzięki temu rozwiązaniu organizator ma pełny wgląd w przebieg zawodów i może szybko reagować na sytuacje awaryjne.

## Dodawanie logo zawodów

Aby dodać logo zawodów do aplikacji:

1. Przygotuj plik logo w formacie PNG z przezroczystym tłem
2. Nazwij plik "logo.png"
3. Umieść plik w folderze `img/`
4. Logo pojawi się automatycznie w nagłówku każdego ekranu aplikacji

Szczegółowe instrukcje znajdują się w pliku `img/README.txt`.

## Potencjalne rozszerzenia

W przyszłości interfejs mógłby zostać rozbudowany o:

- Integrację z rzeczywistymi mapami (np. Google Maps, OpenStreetMap)
- Funkcje społecznościowe (porównywanie wyników z innymi zawodnikami)
- Historię tras i statystyki
- Tryb treningowy z analizą techniki
- Powiadomienia o warunkach pogodowych
- Komunikację głosową między organizatorem a zawodnikami
- Automatyczne wykrywanie niebezpiecznych sytuacji
