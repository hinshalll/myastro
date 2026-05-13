# WeasyPrint on Windows — one-time setup

The kundli PDF builder uses WeasyPrint (HTML/CSS → PDF). On Linux it
works out of the box. On **Windows dev**, WeasyPrint additionally needs
the **GTK3 runtime** DLLs (`libgobject-2.0-0`, `pango`, `cairo`, etc.).

Without GTK3, `build_kundli_pdf()` falls back to returning the **rendered
HTML** as bytes. The user can open the HTML in any browser and use
"Print → Save as PDF" — the result is visually identical to the WeasyPrint PDF.

## Quick install (5 min)

1. Download the GTK3 runtime installer:
   https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

2. Pick the latest `gtk3-runtime-X.Y.Z-YYYY-MM-DD-ts-win64.exe` and run it.
   Default install path is fine.

3. Important: tick **"Set up PATH environment variable"** during install.

4. Close + reopen your terminal/IDE, then verify:
   ```
   python -c "import weasyprint; print(weasyprint.HTML(string='<p>hi</p>').write_pdf()[:4])"
   ```
   It should print `b'%PDF'`. If you get an `OSError: cannot load library
   'libgobject-2.0-0'`, restart your shell or reboot to refresh PATH.

## Deploy targets

- **Streamlit Cloud** (Linux) — works out of the box; nothing to install.
- **Mobile-app backend** (Linux/Docker) — add `weasyprint pango libcairo2` to
  your apt list or use a `weasyprint`-ready base image.

## When PDF still fails

`build_kundli_pdf()` is designed to never crash the UI:
1. It tries WeasyPrint first.
2. On any failure, it returns the rendered HTML bytes.
3. The Streamlit `views/kundli.py` view detects this (checks for the `%PDF`
   magic header) and presents either a `.pdf` download or a `.html` download
   with a banner explaining the situation.
