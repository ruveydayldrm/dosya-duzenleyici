import tempfile
import unittest
from pathlib import Path

from duzenleyici import GUNLUK_DOSYASI, bos_isim_bul, duzenle, geri_al, kategori_bul


class KategoriTesti(unittest.TestCase):
    def test_bilinen_uzantilar(self):
        self.assertEqual(kategori_bul(Path("tatil.JPG")), "Resimler")
        self.assertEqual(kategori_bul(Path("rapor.pdf")), "Belgeler")
        self.assertEqual(kategori_bul(Path("satis.xlsx")), "Tablolar")
        self.assertEqual(kategori_bul(Path("kurulum.exe")), "Kurulum")

    def test_bilinmeyen_ve_uzantisiz(self):
        self.assertEqual(kategori_bul(Path("garip.xyz")), "Diğer")
        self.assertEqual(kategori_bul(Path("BENIOKU")), "Diğer")


class DuzenlemeTesti(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.klasor = Path(self._tmp.name)
        for ad in ["foto.png", "not.txt", "sarki.mp3", "arsiv.zip", "garip.xyz", "yarim.crdownload", ".gizli"]:
            (self.klasor / ad).write_text(ad, encoding="utf-8")
        (self.klasor / "AltKlasor").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_dosyalar_kategorilere_tasinir(self):
        duzenle(self.klasor)
        self.assertTrue((self.klasor / "Resimler" / "foto.png").exists())
        self.assertTrue((self.klasor / "Belgeler" / "not.txt").exists())
        self.assertTrue((self.klasor / "Müzik" / "sarki.mp3").exists())
        self.assertTrue((self.klasor / "Arşivler" / "arsiv.zip").exists())
        self.assertTrue((self.klasor / "Diğer" / "garip.xyz").exists())

    def test_yarim_indirme_gizli_dosya_ve_klasorlere_dokunulmaz(self):
        duzenle(self.klasor)
        self.assertTrue((self.klasor / "yarim.crdownload").exists())
        self.assertTrue((self.klasor / ".gizli").exists())
        self.assertTrue((self.klasor / "AltKlasor").is_dir())

    def test_deneme_modu_hicbir_sey_tasimaz(self):
        hareketler = duzenle(self.klasor, deneme=True)
        self.assertEqual(len(hareketler), 5)
        self.assertTrue((self.klasor / "foto.png").exists())
        self.assertFalse((self.klasor / "Resimler").exists())
        self.assertFalse((self.klasor / GUNLUK_DOSYASI).exists())

    def test_ayni_isimli_dosyanin_uzerine_yazilmaz(self):
        (self.klasor / "Resimler").mkdir()
        (self.klasor / "Resimler" / "foto.png").write_text("eski", encoding="utf-8")
        duzenle(self.klasor)
        self.assertEqual((self.klasor / "Resimler" / "foto.png").read_text(encoding="utf-8"), "eski")
        self.assertEqual((self.klasor / "Resimler" / "foto (1).png").read_text(encoding="utf-8"), "foto.png")

    def test_geri_al_her_seyi_eski_haline_getirir(self):
        duzenle(self.klasor)
        sayi = geri_al(self.klasor)
        self.assertEqual(sayi, 5)
        for ad in ["foto.png", "not.txt", "sarki.mp3", "arsiv.zip", "garip.xyz"]:
            self.assertTrue((self.klasor / ad).exists(), ad)
        self.assertFalse((self.klasor / "Resimler").exists())
        self.assertFalse((self.klasor / GUNLUK_DOSYASI).exists())

    def test_geri_alinacak_bir_sey_yoksa(self):
        self.assertEqual(geri_al(self.klasor), 0)

    def test_bos_isim_bul(self):
        hedef = self.klasor / "a.txt"
        self.assertEqual(bos_isim_bul(hedef), hedef)
        hedef.write_text("x")
        (self.klasor / "a (1).txt").write_text("x")
        self.assertEqual(bos_isim_bul(hedef).name, "a (2).txt")


if __name__ == "__main__":
    unittest.main()
