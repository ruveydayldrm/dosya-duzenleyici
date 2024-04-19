# Dosya Düzenleyici 🗂️

Dağınık bir klasördeki (ör. **İndirilenler**) dosyaları uzantılarına göre kategori klasörlerine ayıran küçük bir Python komut satırı aracı.

```
İndirilenler/
├── Resimler/   foto.png, ekran.jpg
├── Belgeler/   rapor.pdf, not.txt
├── Tablolar/   satis.xlsx
├── Arşivler/   proje.zip
└── Diğer/      garip.xyz
```

## Özellikler

- 10 kategori: Resimler, Belgeler, Tablolar, Sunumlar, Videolar, Müzik, Arşivler, Kurulum, Kodlar, Yazı Tipleri (ve **Diğer**).
- **Deneme modu** (`--dene`): hiçbir dosyayı taşımadan ne olacağını gösterir.
- **Geri alma** (`--geri-al`): son düzenlemeyi tamamen geri alır.
- **Üzerine yazmaz**: aynı adlı dosya varsa `foto (1).png` olarak taşır.
- Yarım kalmış indirmelere (`.crdownload`, `.part`), gizli dosyalara ve alt klasörlere dokunmaz.
- Ek kütüphane gerektirmez; yalnızca Python 3.9+.

## Kullanım

```bash
python duzenleyici.py                  # İndirilenler klasörünü düzenler
python duzenleyici.py "C:\Users\ben\Masaüstü\Karışık"
python duzenleyici.py --dene           # Önce bir bakalım
python duzenleyici.py --geri-al        # Vazgeçtim, geri al
```

Örnek çıktı:

```
  rapor.pdf  →  Belgeler/rapor.pdf
  foto.png  →  Resimler/foto.png
  satis.xlsx  →  Tablolar/satis.xlsx

Belgeler: 1, Resimler: 1, Tablolar: 1

3 dosya düzenlendi. Geri almak için: python duzenleyici.py --geri-al
```

## Testler

```bash
python -m unittest -v
```

## Kategorileri özelleştirme

`duzenleyici.py` içindeki `KATEGORILER` sözlüğüne yeni kategori ya da uzantı ekleyebilirsiniz.
