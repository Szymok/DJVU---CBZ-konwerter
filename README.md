# DJVU do CBZ Konwerter

Skrypt Python do konwersji plików DJVU na format CBZ (Comic Book ZIP), idealny do korzystania z serwerem Komga.

## Opis

Ten skrypt umożliwia konwersję plików DJVU (często używanych dla zeskanowanych dokumentów i starszych publikacji) do formatu CBZ, który jest lepiej obsługiwany przez serwery mediów takie jak Komga. Format CBZ zapewnia:

- Lepszą kompatybilność z czytnikami ebooków i aplikacjami do komiksów
- Brak problemów z przycinaniem stron (które mogą występować w PDF)
- Dobry stosunek jakości do rozmiaru pliku
- Pełne wsparcie w Komga

## Wymagania

- Python 3.6 lub nowszy
- DjVuLibre (dla poleceń ddjvu i djvused)
- Biblioteka Pillow (PIL)

## Instalacja

1. Zainstaluj Python 3.x z [oficjalnej strony](https://www.python.org/downloads/)

2. Zainstaluj DjVuLibre:
   - Pobierz instalator DjVuLibre dla Windows
   - Zainstaluj w domyślnej lokalizacji (zazwyczaj `C:\Program Files (x86)\DjVuLibre`)

3. Zainstaluj wymagane biblioteki Python:
   ```
   pip install Pillow tqdm
   ```

4. Pobierz skrypt `djvu_to_cbz.py` z tego repozytorium

## Konfiguracja

Przed uruchomieniem skryptu, upewnij się, że ścieżki do plików wykonywalnych DjVuLibre są poprawne:

```python
# Zdefiniuj pełne ścieżki do plików wykonywalnych
DDJVU_PATH = r"C:\Program Files (x86)\DjVuLibre\ddjvu.exe"
DJVUSED_PATH = r"C:\Program Files (x86)\DjVuLibre\djvused.exe"
```

Jeśli zainstalowałeś DjVuLibre w innej lokalizacji, zaktualizuj te ścieżki.

## Użycie

```
python djvu_to_cbz.py [folder_wejściowy] -o [folder_wyjściowy] -q [jakość] -w [liczba_wątków]
```

### Parametry:

- `folder_wejściowy`: Folder zawierający pliki DJVU do konwersji
- `-o, --output_folder`: Folder, w którym zostaną zapisane pliki CBZ (domyślnie: folder wejściowy)
- `-q, --quality`: Jakość obrazu (1-100, wyższa wartość = lepsza jakość, ale większy rozmiar pliku) (domyślnie: 85)
- `-w, --workers`: Maksymalna liczba równoległych konwersji (domyślnie: 1)

### Przykład:

```
python djvu_to_cbz.py "C:\Moje Dokumenty\Książki DJVU" -o "C:\Moje Dokumenty\Książki CBZ" -q 90 -w 1
```

## Rozwiązywanie problemów

### Błąd: "No module named 'PIL'"

Zainstaluj bibliotekę Pillow:
```
pip install Pillow
```

### Błąd: "ddjvu executable not found"

Upewnij się, że DjVuLibre jest zainstalowane i ścieżki w skrypcie są poprawne.

### Błąd podczas konwersji stron

Spróbuj zmniejszyć jakość obrazu (-q 70) lub użyj trybu sekwencyjnego (-w 1).

## Zalecenia dla Komga

- Umieść pliki CBZ w folderze biblioteki Komga
- Upewnij się, że nazwy plików są zgodne z konwencją nazewnictwa Komga
- Dla najlepszych wyników, używaj jakości 80-90, co zapewnia dobry balans między jakością a rozmiarem pliku

## Licencja

Ten skrypt jest udostępniany na licencji MIT. Możesz go swobodnie modyfikować i rozpowszechniać.

## Autor

Ten skrypt został stworzony, aby ułatwić konwersję starszych dokumentów DJVU do formatu lepiej obsługiwanego przez nowoczesne czytniki i serwery mediów.

## Podziękowania

- DjVuLibre za narzędzia do obsługi formatu DJVU
- Twórcom Komga za świetny serwer do komiksów i ebooków
