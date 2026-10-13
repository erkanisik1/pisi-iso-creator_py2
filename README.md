# Pisi ISO Creator (py2)

Pisi Linux için canlı/kurulabilir ISO üretme aracı. PiSi deposundan paket seçimi, yerel repo üretimi, chroot ile imaj kurulumu, initramfs + SquashFS ve BIOS/UEFI hibrit ISO adımlarını tek GUI/CLI altında toplar.

> Not: Bu dal Python 2.7 + PyQt5 tabanlıdır. Pisi Linux üzerinde, root yetkisiyle çalıştırılmak üzere tasarlanmıştır.

## Özellikler

- PyQt5 GUI ile proje yönetimi (paket/collection, dil seçimi)
- PiSi index (`pisi-index.xml[.bz2|.xz]`) okuma, bağımlılık çözümleme
- Yerel `image_repo` / `install_repo` üretimi
- `make-live`: chroot içine paket kurulumu ve sistem yapılandırması
- `pack-live`: initramfs + `pisi.sqfs` (mksquashfs)
- `make-iso`: Syslinux/ISOLINUX (BIOS) + GRUB (UEFI) + xorriso hibrit ISO
- Calamares / Yalı kurulumcu dosya desteği (`data/installer`)
- KDE, XFCE, LXQt, Mate masaüstü yapılandırmaları (`data/desktop_conf`)
- ISO içeriği yalnızca `PackageSelection` / `PackageCollections` içindeki paketlerden üretilir (`InstallImagePackages` kaldırıldı)

## Üretim hattı

```text
Proje XML
  → PiSi index + bağımlılık çözümü
  → repo_cache + image_repo + install_repo
  → image/ (pisi + chroot + yapılandırma)
  → initramfs + pisi.sqfs
  → BIOS/UEFI boot ağacı + xorriso hibrit ISO
```

CLI aşamaları (`pisiman.py`):

| Komut | İşlev |
|---|---|
| `make-repo` | Yerel depoları hazırlar |
| `check-repo` | Paket SHA-1 kontrolü |
| `make-live` | İmaj dizinine kurulum |
| `pack-live` | SquashFS üretimi |
| `make-iso` | ISO üretimi |
| `make` | Tümü |

## Gereksinimler

`required_packages.txt`:

```text
make, pyqtermwidget5, python-chardet, python-idna, python-qt5,
python-qt5-devel, python-requests, python-sip, python-urllib3,
squashfs-tools, syslinux, xorriso
```

Ayrıca sistemde olması gerekenler: `pisi`, `mksquashfs`, `xorriso`, `grub2-mkstandalone`, `mkfs.vfat` (dosfstools), `py2uic5`/`py2rcc5`, mount/chroot araçları.

Yalnızca Pisi Linux üzerinde çalışır.

## Kurulum ve çalıştırma

İlk kurulum + GUI (önerilen):

```bash
sh ./run.sh
# make.sh UI dosyalarını üretir, gerekli paketleri kurar,
# ardından sudo ./pisiman.py --style=breeze çalıştırır
```

Manuel:

```bash
sh ./make.sh          # UI üretimi + paket kurulumu
sudo ./pisiman.py     # GUI
```

Temizlik:

```bash
sh ./make.sh clean
```

CLI ile tam ISO:

```bash
sudo ./pisiman.py make project-files/pisi-2.4_minimal.xml
```

Aşamalı:

```bash
sudo ./pisiman.py make-repo project-files/pisi-2.4_minimal.xml
sudo ./pisiman.py check-repo project-files/pisi-2.4_minimal.xml
sudo ./pisiman.py make-live project-files/pisi-2.4_minimal.xml
sudo ./pisiman.py pack-live project-files/pisi-2.4_minimal.xml
sudo ./pisiman.py make-iso project-files/pisi-2.4_minimal.xml
```

## Proje dosyaları

`project-files/` altında örnek `PardusmanProject` XML'leri bulunur:

- `pisi-2.4_minimal.xml` / `-cpio.xml`
- `Pisi-Linux-2.4.4-KDE6-x86_64.xml` ve `cpio` / `cpio-calamares` / `cpio-yalirs` varyantları

Ana alanlar: `Title`, `WorkDir`, `ReleaseFiles`, `LiveRepo`, `IsoOutputDir`, `PackageCollections` / `PackageSelection`, `LanguageSelection`.

Örnek XML'lerdeki `WorkDir` ve `ReleaseFiles` yolları makineye özeldir; kullanmadan önce kendi yollarınıza göre düzenleyin.

## Çalışma dizini çıktıları

| Çıktı | Açıklama |
|---|---|
| `repo_cache/` | İndirilen index ve paketler |
| `image_repo/` | İmaj için yerel PiSi deposu |
| `install_repo/` | Kurulumcu için yerel depo |
| `image/` | Chroot kök dosya sistemi |
| `efi_tmp/` | Geçici EFI FAT içeriği |
| `iso/` | ISO ağacı |
| `pisi.sqfs` | SquashFS imajı |
| `finished.txt` | Tamamlanan aşama göstergesi |
| `missing.txt` | Eksik/bozuk paket listesi |

## Dizin yapısı

```text
pisiman.py            CLI girişi + GUI seçimi
gui/                  PyQt5 arayüz (main.py, diyaloglar, ui/)
repotools/            project.py, packages.py, maker.py, desktop_config.py
data/                 ISO içine giren sistem/desktop/installer/boot/initramfs dosyaları
icons/                GUI collection ikonları
project-files/        Örnek proje XML'leri
release-files/        index.html, release-notes, lisans şablonları
Makefile, make.sh     Qt UI/resource üretimi
run.sh                İlk kurulum + root ile başlatma
```

## Uyarılar

- Uygulama root olarak çalışır; yalnızca güvendiğiniz proje/depo dosyalarıyla, izole bir build makinesinde kullanın.
- TLS/imza doğrulaması ve Calamares `erase` varsayılanları gibi güvenlik başlıkları gözden geçirilmeyi bekliyor (bkz. `PROJE_RAPORU.md`).
- Örnek projeler taşınabilir değil; sabit kullanıcı yolları içerir.

## Lisans

GPLv2 — bkz. `LICENSE`.
