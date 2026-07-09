# Personel Takip Sistemi

Personel mesai, izin ve rapor takibi icin masaustu uygulamasi.

## Calistirma

Python ile calistirmak icin:

```text
IK_Takip_Baslat.bat
```

Exe uretmek icin PyInstaller kurulu oldugunda:

```text
build_exe.bat
```

Exe ciktisi:

```text
dist/Personel_Takip_Sistemi/Personel_Takip_Sistemi.exe
dist/Personel_Takip_Sistemi/config.json
```

`config.json` exe disinda, exe ile ayni klasorde kalir. Kullanici kodu degistirmeden saatleri, tatilleri, sekmeleri, kolonlari ve secenekleri bu dosyadan duzenleyebilir.

## Ayarlar

Tum duzenlenebilir degerler `config.json` icindedir:

- Program adi ve logo metni/renkleri
- Mesai baslangic ve bitis saatleri
- Mola saatleri
- Cumartesi ve pazar calisma ayarlari
- Tam gun ve yarim gun resmi tatiller
- Sekme adlari
- Arama/filtre alanlari
- Acilir liste secenekleri
- Varsayilan degerler
- Tablo kolonlari

`config.json` yoksa program acilista otomatik varsayilan dosyayi olusturur. JSON hataliysa program anlasilir bir hata mesaji gosterir.

## Kullanim

- Ana sekmede satir satir kayit girilir.
- `Açıklama` alani son kolon olarak eklenmistir ve secenekleri `config.json` icinden gelir.
- Tablo ustundeki filtre kutulari `config.json` icindeki `search_fields` listesine gore aktif olur.
- `Ctrl+C` secili satirlari kopyalar.
- `Ctrl+V` Excel benzeri satirlari tabloya ekler.
- Tabloda bir satira tiklayinca kayit ustteki giris alanlarina gelir.
