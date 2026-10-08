# Pisiman Proje İnceleme ve Durum Raporu

**Rapor tarihi:** 25 Eylül 2026  
**İncelenen dizin:** `/media/yedekleme/projects/prj_orj/rmys/new-pisiman-py2/pisiman`  
**İlgili kardeş dizinler:** `../project-files`, `../release-files`

## 1. Yönetici özeti

Pisiman; Pisi Linux/PiSi depolarından paket seçilmesini, yerel depolar ve yaşayan sistem görüntüsü oluşturulmasını, initramfs ile SquashFS üretilmesini ve BIOS/UEFI destekli hibrit ISO oluşturulmasını hedefleyen bir masaüstü uygulamasıdır.

Projenin üretim hattı anlaşılır ve aşamaları birbirinden ayrılmıştır. Ancak mevcut kaynak ağacı güvenli, tekrarlanabilir ve test edilmiş bir sürüm olarak değerlendirilemez. Başlıca nedenler:

- Uygulama Python 2.7 ve PyQt5'e bağlı; Python 2 artık desteklenmeyen bir çalışma zamanıdır.
- Build sırasında çok sayıda root yetkisiyle shell komutu çalıştırılmaktadır.
- HTTPS sertifika doğrulaması kapatılmış, depo bütünlüğü için yalnızca SHA-1 kullanılmaktadır.
- Live kullanıcıya PolicyKit üzerinden çok geniş yetkiler verilmektedir.
- Proje XML'i kaydetme işlemi veri modelini bozmaktadır.
- Initramfs seçimi, paket temizleme ve release dosyası kopyalama akışlarında hatalı/eksik yollar bulunmaktadır.
- Calamares varsayılanları disk silme riski oluşturabilecek şekilde yapılandırılmıştır.
- Test, CI, sürüm/paket metadata'sı ve build manifesti bulunmamaktadır.

**Genel değerlendirme:** Temel üretim fikri ve mimari kullanılabilir; fakat güvenlik, doğruluk ve modernizasyon tamamlanmadan yeni kullanıcılara veya güvenilmeyen proji/depo dosyalarına açılmamalıdır. Mevcut haliyle yalnızca kontrollü bir build makinesinde, güvenilir yerel proje ve depo dosyalarıyla kullanılmalıdır.

---

## 2. İnceleme yöntemi ve sınırlar

Yapılan işlemler:

- Kaynak ağacı, UI dosyaları, shell scriptleri, Calamares ayarları ve initramfs/boot varlıkları incelendi.
- 14 örnek proje XML'i ayrıştırıldı.
- Bir örnek proje XML'i Python 2 ile geçici bir dosyaya kaydedilerek round-trip sonucu kontrol edildi.
- Tüm `.py` dosyaları Python 2 ve Python 3 ile bellek içinde derlenerek kontrol edildi.
- Ana Python 2 modülleri içe aktarıldı.
- Calamares YAML dosyaları duplicate anahtar açısından kontrol edildi.
- Symlink'ler ve dosya envanteri kontrol edildi.

Bilerek yapılmayan işlemler:

- `sudo` çalıştırılmadı.
- GUI açılmadı.
- `make.sh`/`make` çalıştırılmadı.
- Gerçek PiSi index indirilmedi.
- ISO üretilmedi.
- BIOS/UEFI veya Calamares boot/install testi yapılmadı.

Bu nedenle bulgular statik kod incelemesi ve güvenli, etkisiz kontrollerle doğrulanmıştır; tam entegrasyon testi değildir.

---

## 3. Proje envanteri

Rapor hazırlanma anındaki `pisiman/` ağacı:

| Ölçüt | Değer |
|---|---:|
| Disk kullanımı | Yaklaşık 26 MiB |
| Düzenli dosya | 976 |
| Dizin | 166 |
| Symlink | 55 |
| Python dosyası | 27 |

### Önemli dizinler ve dosyalar

| Yol | Görev |
|---|---|
| `pisiman.py` | CLI komut girişi ve GUI/CLI seçimi |
| `gui/` | PyQt5 arayüzü, diyaloglar, terminal ve generated UI dosyaları |
| `repotools/project.py` | Proje XML okuma/yazma ve proje çalışma dizini yardımcıları |
| `repotools/packages.py` | PiSi index indirme, cache, paket bağımlılıkları ve yerel repo üretimi |
| `repotools/maker.py` | Image, initramfs, SquashFS, EFI ve ISO üretim motoru |
| `repotools/desktop_config.py` | KDE/XFCE/Calamares/YALI/SDDM dosya kopyalama işlemleri |
| `repotools/utility.py` | Biçimleme ve terminal/DBus yardımcıları |
| `data/` | ISO içine kopyalanan sistem, desktop, installer, boot ve initramfs varlıkları |
| `icons/` | GUI collection ikonları |
| `Makefile`, `make.sh` | Qt UI ve resource dosyalarının üretimi/temizlenmesi |
| `run.sh` | İlk kurulum ve root yetkisiyle GUI başlatma yardımcısı |
| `required_packages.txt` | Pisi paketi biçiminde temel bağımlılık listesi |
| `../project-files/` | 14 adet örnek `PardusmanProject` XML dosyası |
| `../release-files/` | ISO `index.html`, release-notes, license ve görsel dosyaları |

Birincil kod modüllerinde yaklaşık 4.710 satır Python bulunmaktadır. En büyük modül `repotools/maker.py` (~1.836 satır), ardından `gui/main.py` (~941 satır) ve `repotools/project.py` (~651 satır) gelmektedir.

### Mevcut olmayan proje altyapısı

Bu snapshot içinde bulunmayanlar:

- Git deposu metadata'sı (`.git`)
- Testler ve test klasörü
- CI/CD ayarı
- `pyproject.toml`, `setup.py`, `tox.ini`, `pytest.ini`
- Proje sürümü veya build provenance kaydı
- `pisiman/` altında `COPYING` veya `LICENSE`

Üst dizinde `../LICENSE` içinde GPLv2 metni bulunmaktadır. Kaynak dosya başlıklarında öncelikle `COPYING` dosyasına atıf yapılmaktadır.

---

## 4. Projenin amacı ve kullanıcı akışı

### GUI akışı

Parametre verilmeden çalıştırıldığında uygulama şu sırayla çalışır:

1. Proje XML'i açılır veya yeni proje oluşturulur.
2. PiSi repository index indirilir.
3. Bileşen, paket, dil ve collection seçimleri yapılır.
4. Proje çalışma dizininde yerel image/install repo oluşturulur.
5. image dizinine paketler kurulur.
6. Kullanıcı ve sistem ayarları uygulanır.
7. initramfs ve SquashFS üretilir.
8. BIOS/UEFI boot dosyaları hazırlanır.
9. Hibrit ISO oluşturulur.

Aktif arayüz `mainv2` sürümüdür. Eski `main.ui` arayüzü yorum satırıyla devre dışı bırakılmıştır (`gui/main.py:29-33`).

### CLI akışı

`pisiman.py:93-102` içinde aşağıdaki komutlar tanımlıdır:

| Komut | İşlev |
|---|---|
| `make-repo` | Yerel image/install depolarını hazırlar |
| `check-repo` | İndirilen paketlerin SHA-1 değerlerini kontrol eder |
| `make-live` | Image dizinine paketleri kurar ve sistemi yapılandırır |
| `pack-live` | Initramfs ve SquashFS üretir |
| `make-iso` | ISO boot yapılarını ve ISO dosyasını üretir |
| `make` | Tüm aşamaları çalıştırır |

Örnek:

```bash
./pisiman.py make ../project-files/proje.xml
```

### Üretim hattı

```text
Proje XML
   │
   ▼
PiSi index + bağımlılık çözümü
   │
   ▼
repo_cache + image_repo + install_repo
   │
   ▼
pisi ar / pisi it + chroot + sistem yapılandırması
   │
   ▼
initcpio veya eski initramfs
   │
   ▼
pisi.sqfs (mksquashfs)
   │
   ▼
Syslinux/ISOLINUX + GRUB/UEFI + EFI image
   │
   ▼
xorriso ile hibrit ISO
```

---

## 5. Veri modeli ve çalışma dizini

### Proje XML'i

Kök etiket `PardusmanProject` olmalıdır. Başlıca alanlar:

- `Title`
- `WorkDir`
- `ReleaseFiles`
- `PluginPackage`
- `ExtraParameters`
- `LiveRepo`
- `IsoOutputDir`
- `PackageSelection` veya `PackageCollections`
- `InstallImagePackages`
- `LanguageSelection`

XML şeması/XSD bulunmadığından alan adları ve cardinality yalnızca kodla uygulanmaktadır.

### PiSi indexi

`repotools/packages.py` şu index biçimlerini okumaya çalışır:

- Düz `pisi-index.xml`
- `.bz2`
- `.xz`

Paketler hakkında ad, sürüm, release, build, boyut, `PackageURI`, `PackageHash`, component ve runtime bağımlılıkları okunur.

### Çalışma dizini çıktıları

`Project` sınıfı tipik olarak şu alt dizinleri oluşturur:

| Çıktı | Açıklama |
|---|---|
| `repo_cache/` | İndirilen index ve paket dosyaları |
| `image_repo/` | Image kurulumu için yerel PiSi deposu |
| `install_repo/` | Installer/collection için yerel PiSi deposu |
| `image/` | Chroot yapılacak kök dosya sistemi |
| `efi_tmp/` | Geçici EFI FAT image içeriği |
| `iso/` | ISO ağacının geçici dosya sistemi |
| `pisi.sqfs` | Üretilen SquashFS image |
| `finished.txt` | GUI'nin kullandığı son aşama göstergesi |
| `missing.txt` | Hash kontrolünde eksik/bozuk paket listesi |

---

## 6. Çalıştırma ve build akışı

README'nin önerdiği temel komut:

```bash
sh ./run.sh
```

`run.sh` ilk çalışmada `make.sh` fonksiyonunu kaynak olarak alır, generated UI dosyalarını üretmeye çalışır ve uygulamayı şu şekilde başlatır:

```bash
sudo ./pisiman.py --style=breeze
```

Önemli noktalar:

- `make.sh:1` ve `run.sh:1` `/bin/sh` kullanıyor.
- Buna rağmen `make.sh` içinde `function`, `[[ ... ]]` ve `BASH_SOURCE`; `run.sh` içinde `source` kullanılıyor.
- İncelenen sistemde `/bin/sh` Bash'e bağlı olduğu için örnek komut çalışabilir; POSIX uyumu yoktur.
- Uygulamanın kendisi root yetkisiyle çalıştırılır.
- Generated UI üretimi `py2uic5` ve `py2rcc5` kullanır.
- `.firstRun` mevcutsa generated dosyalar yeniden üretilmeden çalıştırılabilir.

### İncelenen ortamdaki araç durumu

Güvenli kontrolde bulunanlar:

- Python 2.7.18
- PyQt5
- QTermWidget
- piksemel
- Python DBus
- requests
- pisi.graph
- py2uic5 / py2rcc5
- pisi
- mksquashfs
- xorriso

Ana modüller (`pisiman`, `gui.main`, `repotools.maker`, `repotools.project`, `repotools.packages`) Python 2 altında içe aktarılabiliyor. Bu, tam build başarısını kanıtlamaz.

### Build komutlarında kullanılan ancak bağımlılık listesinde açıkça verilmeyen bileşenler

- `pisi`
- `grub2-mkstandalone` / GRUB paketleri
- `mkfs.vfat` / dosfstools
- `dd`
- mount/umount/chroot ve ilgili util-linux araçları
- DBus daemon araçları
- cpio/gzip veya ilgili initramfs araçları
- py2uic5/py2rcc5 sağlayan geliştirici paketleri
- PiSi graph/modül bağımlılıkları

`required_packages.txt` eksiksiz bir build bağımlılık manifesti değildir.

---

## 7. Doğrulanan olumlu yönler

- CLI ve GUI aynı build fonksiyonlarını kullanıyor.
- Repo, image, initramfs ve ISO aşamaları ayrı fonksiyonlara ayrılmış.
- PiSi bağımlılık grafiğinde döngü kontrolü var (`repotools/packages.py:329-338`).
- Yerel repo için index ve SHA-1 checksum üretiliyor.
- BIOS ISOLINUX ve UEFI GRUB yolları ayrıca ele alınıyor.
- `xorriso` ile hibrit BIOS/UEFI ISO üretimi hedefleniyor.
- 14 örnek proje XML'inin tamamı standart XML ayrıştırıcısıyla geçerli.
- Mevcut Python 2 ortamında birincil modüller içe aktarılabiliyor.
- 27 Python dosyasının 26'sı Python 2 sözdizimi kontrolünden geçiyor; tek hatalı dosya aktif kaynak değil, eski yedek dosya.
- Build sonuçları aşamaya göre `finished.txt` ile ayrılıyor.
- ISO içeriğinin büyük bölümü `data/` altında tek bir image ağacında tutuluyor.

---

## 8. Riskler ve bulgular

Önem sırası: **Kritik**, **Yüksek**, **Orta**, **Düşük**.

### KRİTİK — K-01: Root seviyesinde shell komutları ve komut enjeksiyonu yüzeyi

Temel komut çalıştırıcı doğrudan `os.system()` kullanıyor:

- `repotools/maker.py:47-52`
- `repotools/project.py:526-534`
- `repotools/desktop_config.py:20-103`
- `repotools/system_config.py:17-21`

Proje XML'indeki yollar, repo URI'leri ve paket adları shell komutlarına string olarak giriyor. GUI de build komutlarını root terminaline gönderiyor (`gui/main.py:481-617`). Uygulama root yetkisiyle çalıştığı için bu tür kotarma ve komut enjeksiyonu hataları doğrudan sistem güvenliğini etkiler.

**Öneri:** `subprocess.run([...], shell=False)` kullan; yolları normalize edilmiş ve izinli çalışma kökü içinde sınırla; build'i ayrı VM/namespace içinde çalıştır; `sudo`yu yalnızca gerekli adımlara daralt.

### KRİTİK — K-02: HTTPS sertifika doğrulaması kapalı ve depo bütünlüğü zayıf

- `repotools/packages.py:22-25`: urllib3 uyarıları bastırılıyor.
- `repotools/packages.py:110-115`: `requests.get(..., verify=False)`.
- `repotools/maker.py:995`: `--ignore-check`.
- `repotools/maker.py:1187-1188`: `--ignore-check`.

Index veya paket dosyası için GPG/imza doğrulama görünmüyor. SHA-1 yalnızca cache ile index arasında tutarlılık kontrolü sağlıyor; modern saldırı modelinde güvenilir imza doğrulamasının yerini tutmaz.

**Öneri:** TLS doğrulamasını aç, HTTP(S) redirect ve içerik limitlerini doğrula, PiSi index imzasını ve paket hash algoritmasını güvenilir değerlerle doğrula, `--ignore-check` kullanımını kaldır.

### KRİTİK — K-03: Calamares varsayılanları disk silme riski taşıyor

- `data/installer/calamares/usr/share/calamares/modules/partition.conf:149`: `initialPartitioningChoice: erase`.
- `data/installer/calamares/settings.conf:174-180`: `prompt-install: false`.

Bu iki ayar birlikte kullanıcıyı bilinçli disk seçimi yapmadan erase akışına yönlendirebilir.

Ayrıca `shellprocess.conf:128-139` içinde iki ayrı `script:` anahtarı var. Duplicate-key denetimi ikinci `script` değerinin hata vermesine veya parser davranışına bağlı olarak sessizce ilk/son değerin kullanılmasına yol açabilir. YAML kontrolü `script` duplicate hatasını doğruladı.

**Öneri:** Varsayılan seçim `none` olsun; son onay zorunlu olsun; duplicate YAML anahtarları birleştirilsin; destructive seçenekler açıkça ve iki aşamalı onay istesin.

### KRİTİK — K-04: Live kullanıcıya aşırı geniş sistem yetkileri veriliyor

- `repotools/maker.py:610-648`: `pisi` kullanıcısı için `Action=*` ve bütün sonuçlarda `yes`.
- `repotools/maker.py:1300-1304`: kullanıcı `wheel`, `sudo` ve diğer sistem gruplarına ekleniyor.
- `repotools/desktop_config.py:27`: `/home/pisi/.config` için `chmod -R 777`.

Bu, live kullanıcısını sistemde yüksek yetkiye sahip hale getirir.

**Öneri:** Live ve installer kullanıcılarını ayır; PolicyKit kurallarını installer'a özel action'larla sınırla; `sudo`/wheel yetkisini yalnız gerekli aşamada aç; `chmod 777` uygulamasını kaldır.

### YÜKSEK — Y-01: Python 2 yaşam döngüsü sona ermiş, kod Python 3'e hazır değil

Kod köken olarak Python 2'ye bağlıdır:

- `repotools/project.py:235`: eski exception syntax.
- `repotools/project.py:304-305`: `unicode()`.
- `repotools/packages.py:16`: `urllib2`.
- `repotools/packages.py:241-244`: Python 2 `map` davranışına bağlı liste kullanımı.
- `repotools/utility.py:26,33`: integer division ve `has_key`.
- GUI dosyalarında `xrange`, `iteritems`, `unicode` ve eski `print` kullanımı.

Python 3 bellek içi derleme sonucunda 27 dosyanın 23'ü geçerli, 4'ü hatalıdır. Generated UI dosyaları Python 3 sözdizimine uygun olsa da sonlarında `import raw_rc` bulunur (`gui/ui/mainv2.py:400` gibi); Python 3 package import düzeninde bu `raw_rc` modülüne ulaşılmayabilir.

**Öneri:** Python 3'e kontrollü geçiş yap; `piksemel`, `pisi.graph` ve PyQt5 uyumluluğunu doğrula; generated UI üretimini sabitlenmiş `pyuic5`/`pyrcc5` ile package-aware hale getir.

### YÜKSEK — Y-02: Proje XML kaydetme işlemi veri modelini bozuyor

`repotools/project.py:443-449` her collection için ayrı `InstallImagePackages` yazıyor; ardından `project.py:470-485` genel bir `InstallImagePackages` daha yazıyor. Sonrasında `project.py:487-488` şu şekilde beklenmeyen bir etiket oluşturuyor:

```xml
<installationPackages>
    <peri>...</peri>
</installationPackages>
```

`item` değişkeni güvenilir şekilde tanımlı değil ve her zaman son paket adını temsil ediyor.

14 örnek XML'in tamamında:

- 2 adet `InstallImagePackages`
- 1 adet `installationPackages`

bulunuyor. Bir örnek Python 2 ile geçici dosyaya kaydedildiğinde aynı hatalı yapı yeniden üretildi.

Ayrıca `find_all_packages()` içinde collection listesi her collection için sıfırlanıyor ve `self.all_packages` yalnızca son collection'a ekleniyor (`project.py:564-580`).

**Öneri:** Proje formatı için şema tanımla; tek canonical `InstallImagePackages` yaz; package collection toplamını tüm collection'lardan birleştir; round-trip testi ekle.

### YÜKSEK — Y-03: “Release dosyalarını kaydet” düğmesi aynı zamanda kendisini siliyor

Kaynak UI'da `releaseSave` düğmesi `deleteLater()` slotuna bağlı:

- `gui/ui/mainv2.ui:666-670`

Aynı düğme uygulama kodunda ayrıca `slotReleaseSave()` fonksiyonuna bağlanıyor:

- `gui/main.py:167`
- `gui/main.py:703-730`

**Etki:** Düğme ilk tıklamadan sonra kaybolabilir veya beklenmeyen davranış gösterebilir. Release dosyalarını ayrıca `data/etc` içine yazması, uygulama root çalışıyorsa tüm projeleri etkileyen kaynak dosyası değişikliği oluşturur.

**Öneri:** `deleteLater()` bağlantısını `.ui` kaynağından kaldır; release dosyalarını proje çalışma dizinine kaydet.

### YÜKSEK — Y-04: Initramfs seçiminde tanımsız değişken ve bozuk yardımcı yol var

`mkinitcpio()` içinde yalnızca `mkinitcpio` veya `mkinitramfs` paketlerinden biri varsa `binary`, `config_path` ve `extra_args` atanıyor (`repotools/maker.py:170-188`). Aşağıdaki iki noktada değişkenler kullanılıyor:

- `repotools/maker.py:201-202`
- `repotools/maker.py:1583-1586`

İkisi de yoksa `UnboundLocalError` oluşur.

Ayrıca `squash_live_config_image()` içinde tanımsız `chrun2` çağrılıyor (`maker.py:762-767`). Fonksiyon şu an çağrılmıyor, ancak bozuk.

**Öneri:** Initramfs aracını proje açılışında seç ve doğrula; yoksa erken, anlaşılır hata ver; kullanılmayan bozuk fonksiyonu kaldır veya testle.

### YÜKSEK — Y-05: `PackageURI` için cache/path sınırı yok

`fetch_uri()` URL bileşenini doğrudan cache altında birleştiriyor (`repotools/packages.py:91-145`):

```python
path = os.path.join(cache_dir, filename)
```

`filename` mutlak yol veya `../` içeriyorsa beklenen cache dışına çıkabilir. Bu değer uzak indexden geldiğinden güvenilmeyen girdi olarak ele alınmalıdır.

**Öneri:** URI şemasını doğrula; cache altında çözümlenen gerçek yolun cache içinde kaldığını test et; sembolik link ve özel dosya durumlarını engelle.

### YÜKSEK — Y-06: Bozuk paket temizliği ilgili dizindeki tüm dosyaları silebilir

`gui/main.py:791-803`, eksik paketin bulunduğu dizindeki bütün dosyaları silmek için liste oluşturuyor. Aynı dizinde başka paketler veya metadata varsa bunlar da silinir. `missing.txt` sonundaki newline nedeniyle boş bir paket adı da oluşabilir.

**Öneri:** Yalnızca doğrulanmış paket URI'sine karşılık gelen dosyayı sil; yolu ve hash'i doğrula; boş satırları ayıkla.

### YÜKSEK — Y-07: Release dosyası kopyalama yolu bazı örnek projelerde bozuk

`repotools/maker.py:1631-1636`, `ReleaseFiles` içeriğini ISO köküne düz kopyalıyor. Daha sonra `index.html` ve `release-notes/` altında dosya bekleniyor (`maker.py:1653-1684`).

Bazı örnekler `ReleaseFiles` olarak doğrudan `.../release-notes` dizinini gösteriyor. Bu durumda:

- HTML dosyaları ISO köküne dağılır,
- `index.html` oluşmaz,
- `release-notes/` dizini oluşmaz.

**Öneri:** Beklenen release şemasını tek yerde doğrula; dizin yapısını normalize et; eksik şablon veya release dizininde build'i kontrollü durdur.

### ORTA — O-01: Aşama durumu yalnızca metin dosyasına güveniyor

`gui/main.py:58-66`, `finished.txt` içeriğini doğrudan `status.index()` ile kullanıyor. Geçersiz içerik exception üretir. Dosya, ilgili image/repo/ISO çıktılarının gerçekten üretilmiş ve güncel olduğunu doğrulamıyor.

**Öneri:** Her aşama için manifest; tarih, kaynak revision, index hash'i ve artifact hash'i tut. GUI yalnız doğrulanmış manifest durumuna göre aşamayı etkinleştirsin.

### ORTA — O-02: Mount/overlay temizliği hata durumlarında garanti değil

Mount, bind mount, overlay, DBus ve chroot işlemleri çok sayıda ayrı komutla yapılıyor. `try/finally` ve bağlam yöneticisi kullanılmadığından hata veya `KeyboardInterrupt` sonrasında yarım mount/overlay kalabilir.

`repotools/project.py:530` ayrıca çalışma dizinlerini `rm -rf` ile temizler; path güvenlik kontrolleri sınırlıdır.

**Öneri:** Build durum makinesi, context manager ve ön/son kontrolleri kullan; işlem sonunda mount ağacını doğrula ve temizle.

### ORTA — O-03: SquashFS ISO ağacına hard-link ile bağlanıyor

`repotools/maker.py:1619-1620`:

```python
os.link(image_file, ...)
```

Image ve ISO çalışma dizinleri farklı dosya sistemlerindeyse build başarısız olur.

**Öneri:** Önceden aynı dosya sistemini doğrula veya kontrollü copy/fallback kullan.

### ORTA — O-04: Build komutları aşırı miktarda “ignore” ve hata yutma kullanıyor

Birçok önemli komutta `ignore_error=True`, `ignore-check`, `ignore-dependency`, `ignore-comar` veya geniş `except` kullanılıyor. Bazı hatalar yalnız ekrana yazılıp akış devam ediyor.

**Öneri:** Her aşama için zorunlu kontroller ve anlaşılır hata sınıfları tanımla; yalnız belgelenmiş, geri dönülebilir işlemlerde hata yut.

### ORTA — O-05: GRUB kaynaklarında font tutarsızlığı var

`data/grub.cfg.template:30-31` iki font yüklemeye çalışıyor:

- `terminus-14.pf2`
- `unifont-regular-16.pf2`

Kaynak ağacında yalnız `terminus-14.pf2` bulunuyor. Image içindeki başka paketler fontu sağlamıyorsa UEFI menüsü etkilenebilir.

**Öneri:** Fontları image build çıktısında zorunlu kontrole tabi tut; eksikse build'i erken durdur.

### DÜŞÜK — D-01: Generated, cache ve yedek dosyalar kaynak ağacını kirletiyor

Örnekler:

- Çok sayıda `.pyc` ve `repotools/__pycache__/`
- `gui/ui/eskiler/`
- `repotools/yedekler ilerde silinecek/`
- `data/yedeklerim/`
- `data/Yeni Klasör/`
- `data/initcpio/hooks/miso copy`
- `data/initramfs/**/*copy*`
- `data/initramfs/**/*saglam*`

Yedek `maker_orig.py` Python 2 derleme kontrolünden geçmiyor. Generated UI'lar PyQt 5.15.9, resource dosyası ise 5.15.16 ile üretilmiş; sürüm tutarlılığı yok.

**Öneri:** Canonical kaynakları belirle; generated dosyalar build çıktısına taşı; yedekleri history dışına çıkar veya ayrı arşivle.

### DÜŞÜK — D-02: Bir symlink bozuk

Bulunan tek bozuk symlink:

```text
data/.../cursors/n-resize -> size-size_ver
```

Hedef muhtemelen `size_ver` olmalıdır.

### DÜŞÜK — D-03: Örnek proje dosyaları taşınabilir değil

14 örnek XML'in tamamında `/home/erkanisik`, `/home/mus1` veya eski `/media/yedekleme/projects/iso-work` yolları bulunuyor. Bir kısmı `ReleaseFiles` olarak doğrudan `release-notes` dizinini gösteriyor.

**Öneri:** Örnekleri makineden bağımsız değişkenler veya göreli/placeholder yollarla yeniden üret.

---

## 9. Yapılan kontrollerin sonuçları

| Kontrol | Sonuç |
|---|---|
| 14 örnek XML'in XML parse testi | 14/14 geçerli |
| Python 2 bellek içi derleme | 26/27 geçerli |
| Python 2 içe aktarma | Ana modüllerin tamamı başarılı |
| Python 3 bellek içi derleme | 23/27 geçerli |
| Proje XML round-trip | Hatalı duplicate tag'ler yeniden üretildi |
| Calamares YAML duplicate kontrolü | `shellprocess.conf` içinde duplicate `script` bulundu |
| Bozuk symlink kontrolü | 1 bozuk symlink bulundu |
| Test/CI varlığı | Bulunamadı |
| Tam ISO buildi | Çalıştırılmadı |
| BIOS/UEFI boot testi | Yapılmadı |
| Calamares kurulum testi | Yapılmadı |

### Python 3 derleme hataları

- `data/initramfs/sbin/mkinitramfs-live.py:52`
- `gui/packages.py:211`
- `repotools/project.py:235`
- `repotools/yedekler ilerde silinecek/maker_orig.py:52`

---

## 10. Önceliklendirilmiş düzeltme planı

### Aşama 0 — Koruma ve tekrarlanabilirlik

1. Kaynak ağacı bir Git deposuna alınmalı.
2. Temiz ve sürümlü bir baseline oluşturulmalı.
3. Generated/yedek dosyaların canonical sahipliği belirlenmeli.
4. Her build için manifest üretilmeli:
   - kaynak revision,
   - proje XML hash'i,
   - repository URL ve index hash'i,
   - seçili paket listesi,
   - araç sürümleri,
   - image/SquashFS/ISO hash'leri.
5. Mevcut örnek XML'ler canonical veri modeline göre yeniden üretilmeli.

### Aşama 1 — Kritik güvenlik

1. `os.system()` ve shell string birleştirmeleri kaldırılmalı.
2. `subprocess` argv listesi ve `shell=False` kullanılmalı.
3. URL, path ve paket adı doğrulama katmanı eklenmeli.
4. TLS doğrulaması açılmalı.
5. Repo index ve paket bütünlüğü için imza doğrulama eklenmeli.
6. `--ignore-check` ve benzeri bayraklar kaldırılmalı.
7. Calamares `erase` ve `prompt-install` varsayılanları güvenli hale getirilmeli.
8. Duplicate `script` YAML anahtarı giderilmeli.
9. Live kullanıcı yetkileri installer-specific action'lara daraltılmalı.
10. `chmod 777` kaldırılmalı.

### Aşama 2 — Doğruluk

1. Python 3 geçişi tamamlanmalı veya Python 2 legacy olarak açıkça izole edilmeli.
2. Project XML şeması ve round-trip testleri eklenmeli.
3. Collection paket birleştirme hatası düzeltilmeli.
4. Multi-repo davranışı ya uygulanmalı ya da şemada açıkça sınırlandırılmalı.
5. `releaseSave/deleteLater` bağlantısı kaldırılmalı.
6. Initramfs aracı başlangıçta doğrulanmalı.
7. Eksik paket temizliği dosya ve hash ile sınırlandırılmalı.
8. Release dizin şeması normalize edilmeli.
9. Mount/DBus/overlay temizliği `try/finally` ile garanti altına alınmalı.
10. Hard-link öncesi dosya sistemi kontrolü veya copy fallback eklenmeli.

### Aşama 3 — Test ve kalite

En az şu testler eklenmeli:

- Proje XML open/save round-trip.
- Duplicate tag regresyonu.
- Birden fazla collection birleşimi.
- Eksik/bozuk `IsoOutputDir` senaryosu.
- Her iki initramfs aracının bulunmadığı senaryo.
- Zararlı URI ve path traversal testleri.
- Bozuk release dizini testi.
- TLS/signature hatası testleri.
- BIOS ISO boot.
- UEFI ISO boot.
- ISO checksum doğrulama.
- Calamares disk seçimi ve iptal/onay akışı.
- Live kullanıcı yetki testi.
- Başarısız build sonrasında mount temizliği.

### Aşama 4 — Modernizasyon ve temizlik

1. Python 2 API'leri kaldırılmalı.
2. Qt generated dosyaları build sırasında üretilmeli.
3. `pyuic5`/`pyrcc5` sürümü sabitlenmeli.
4. `raw_rc` import sorunu kaynak üretim aşamasında çözülmeli.
5. README/NOT tek ve doğru shell kullanımını göstermeli.
6. Bağımlılık kontrolü ve sürüm sabitleme eklenmeli.
7. Ölü kod, eski UI'lar, yedekler, `.pyc` ve `__pycache__` temizlenmeli.
8. Bozuk cursor symlink'i düzeltilmeli.
9. `COPYING`/lisans dağıtımı netleştirilmeli.

---

## 11. Önerilen ilk 10 düzenleme

Aşağıdaki sıra en yüksek fayda/bağımlılık oranını hedefler:

1. `run()` ve tüm `os.system()` çağrılarını güvenli subprocess katmanına taşı.
2. HTTPS `verify=False` kullanımını kaldır.
3. Repo/paket imza ve hash doğrulamasını tanımla.
4. Calamares `erase`, `prompt-install` ve duplicate YAML problemini düzelt.
5. Live kullanıcı PolicyKit ve `chmod 777` yetkilerini daralt.
6. `Project.save()` XML üretimini ve collection birleşimini düzelt.
7. `releaseSave` düğmesinin `deleteLater()` bağlantısını kaldır.
8. Initramfs seçiminde erken doğrulama ekle.
9. Eksik paket silme işlemini yalnız doğrulanmış dosyayla sınırla.
10. XML round-trip ve temel build aşamaları için otomatik test ekle.

---

## 12. `io` dosyasıyla ilgili gözlem

İnceleme başlangıcında kök dizinde `io` adlı, uzantısız ve yaklaşık 11,8 MiB boyutunda bir PostScript dosyası vardı. Dosya ImageMagick tarafından üretilmiş, 1920×1010 sınırlarında düz renkli bir görseldi ve kaynak kodda referansı bulunmadı.

Rapor hazırlanması sırasında dosya kök dizinden artık bulunmuyordu. Bu raporu hazırlarken dosya silinmedi veya yeniden oluşturulmadı; değişiklik bu inceleme sırasında dışarıdan gerçekleşmiş görünüyor. Kaynak kod açısından kullanım zorunluluğu tespit edilmedi.

---

## 13. Sonuç

Pisiman'ın üretim hattı anlaşılabilir ve mevcut Python 2 ortamında temel modüllerinin içe aktarılabildiği doğrulandı. Buna rağmen proje şu anda:

- güvenilmeyen proje veya depo girdilerine karşı,
- tekrarlanabilir release üretimine,
- modern ve desteklenen bir Python çalışma zamanına,
- otomatik test ve CI doğrulamasına

hazır değildir.

En önemli ilk hedef **XML kaydetme hatası, root shell kullanımı, TLS/doğrulama ve Calamares güvenlik varsayılanları** olmalıdır. Bu dört konu düzeltilmeden proje yalnız izole ve kontrollü test ortamında kullanılmalıdır.
