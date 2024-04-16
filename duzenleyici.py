"""
Dosya Düzenleyici
Bir klasördeki dosyaları uzantılarına göre kategori klasörlerine ayırır.

Kullanım:
    python duzenleyici.py                    # İndirilenler klasörünü düzenler
    python duzenleyici.py C:\\Klasor          # Belirli bir klasörü düzenler
    python duzenleyici.py --dene             # Hiçbir şeyi taşımadan ne olacağını gösterir
    python duzenleyici.py --geri-al          # Son düzenlemeyi geri alır
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

KATEGORILER: dict[str, set[str]] = {
    "Resimler": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic", ".ico", ".tiff"},
    "Belgeler": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".pages"},
    "Tablolar": {".xls", ".xlsx", ".csv", ".ods", ".numbers"},
    "Sunumlar": {".ppt", ".pptx", ".odp", ".key"},
    "Videolar": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm", ".flv"},
    "Müzik": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Arşivler": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Kurulum": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".apk"},
    "Kodlar": {".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".c", ".cpp", ".cs", ".sql", ".ipynb", ".sh", ".ps1"},
    "Yazı Tipleri": {".ttf", ".otf", ".woff", ".woff2"},
}
DIGER = "Diğer"

# Yarım kalmış indirmeler ve geçici dosyalar taşınmaz
ATLANACAK_UZANTILAR = {".crdownload", ".part", ".tmp", ".download", ".partial"}
GUNLUK_DOSYASI = ".duzenleyici-gunluk.json"


def kategori_bul(dosya: Path) -> str:
    """Dosyanın uzantısına göre kategori adını döndürür (büyük/küçük harf duyarsız)."""
    uzanti = dosya.suffix.lower()
    for kategori, uzantilar in KATEGORILER.items():
        if uzanti in uzantilar:
            return kategori
    return DIGER


def bos_isim_bul(hedef: Path) -> Path:
    """Hedefte aynı adlı dosya varsa 'ad (1).uzanti', 'ad (2).uzanti' ... şeklinde boş bir ad bulur."""
    if not hedef.exists():
        return hedef
    sayac = 1
    while True:
        aday = hedef.with_name(f"{hedef.stem} ({sayac}){hedef.suffix}")
        if not aday.exists():
            return aday
        sayac += 1


def tasinacaklar(klasor: Path) -> list[tuple[Path, str]]:
    """Klasördeki taşınacak dosyaları ve kategorilerini listeler (alt klasörlere girmez)."""
    sonuc = []
    for dosya in sorted(klasor.iterdir()):
        if not dosya.is_file():
            continue
        if dosya.name.startswith(".") or dosya.name == GUNLUK_DOSYASI:
            continue
        if dosya.suffix.lower() in ATLANACAK_UZANTILAR:
            continue
        sonuc.append((dosya, kategori_bul(dosya)))
    return sonuc


def duzenle(klasor: Path, deneme: bool = False) -> list[dict[str, str]]:
    """Dosyaları kategori klasörlerine taşır. Yapılan taşımaları (geri alma için) döndürür."""
    hareketler: list[dict[str, str]] = []
    for dosya, kategori in tasinacaklar(klasor):
        hedef_klasor = klasor / kategori
        hedef = bos_isim_bul(hedef_klasor / dosya.name)
        if not deneme:
            hedef_klasor.mkdir(exist_ok=True)
            shutil.move(str(dosya), str(hedef))
        hareketler.append({"kaynak": str(dosya), "hedef": str(hedef), "kategori": kategori})

    if hareketler and not deneme:
        gunluk = {"tarih": datetime.now().isoformat(timespec="seconds"), "hareketler": hareketler}
        (klasor / GUNLUK_DOSYASI).write_text(json.dumps(gunluk, ensure_ascii=False, indent=2), encoding="utf-8")
    return hareketler


def geri_al(klasor: Path) -> int:
    """Son düzenlemeyi geri alır; geri taşınan dosya sayısını döndürür."""
    gunluk_yolu = klasor / GUNLUK_DOSYASI
    if not gunluk_yolu.exists():
        return 0
    gunluk = json.loads(gunluk_yolu.read_text(encoding="utf-8"))
    sayi = 0
    for h in reversed(gunluk["hareketler"]):
        hedef, kaynak = Path(h["hedef"]), Path(h["kaynak"])
        if hedef.exists():
            shutil.move(str(hedef), str(bos_isim_bul(kaynak)))
            sayi += 1
    # Boş kalan kategori klasörlerini temizle
    for kategori in {h["kategori"] for h in gunluk["hareketler"]}:
        k = klasor / kategori
        if k.is_dir() and not any(k.iterdir()):
            k.rmdir()
    gunluk_yolu.unlink()
    return sayi


def indirilenler_klasoru() -> Path:
    return Path.home() / "Downloads"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dosyaları uzantılarına göre klasörlere ayırır.")
    parser.add_argument("klasor", nargs="?", type=Path, default=indirilenler_klasoru(), help="Düzenlenecek klasör (varsayılan: İndirilenler)")
    parser.add_argument("--dene", action="store_true", help="Hiçbir şeyi taşımadan ne olacağını göster")
    parser.add_argument("--geri-al", action="store_true", help="Son düzenlemeyi geri al")
    args = parser.parse_args(argv)

    klasor: Path = args.klasor.expanduser().resolve()
    if not klasor.is_dir():
        print(f"Klasör bulunamadı: {klasor}")
        return 1

    if args.geri_al:
        sayi = geri_al(klasor)
        print(f"{sayi} dosya eski yerine taşındı." if sayi else "Geri alınacak bir düzenleme bulunamadı.")
        return 0

    hareketler = duzenle(klasor, deneme=args.dene)
    if not hareketler:
        print("Taşınacak dosya yok, klasör zaten düzenli. ✨")
        return 0

    for h in hareketler:
        print(f"  {Path(h['kaynak']).name}  →  {h['kategori']}/{Path(h['hedef']).name}")
    ozet = Counter(h["kategori"] for h in hareketler)
    print()
    print(", ".join(f"{k}: {v}" for k, v in ozet.most_common()))
    if args.dene:
        print(f"\nDeneme modu: {len(hareketler)} dosya taşınacaktı, hiçbir şey değişmedi.")
    else:
        print(f"\n{len(hareketler)} dosya düzenlendi. Geri almak için: python duzenleyici.py --geri-al")
    return 0


if __name__ == "__main__":
    # Windows konsolunda Türkçe karakterler bozulmasın
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
