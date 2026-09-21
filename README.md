# A-Maze-ing

*This project has been created as part of the 42 curriculum by bigungor, algungor.*

> Not: Subject bu satırın tam olarak bu İngilizce kalıpla ("This project has been created as part of the 42 curriculum by ...") yazılmasını istiyor; bu yüzden README'nin geri kalanı Türkçe olsa da bu ilk satır olduğu gibi bırakılmalı.

## Açıklama (Description)

**A-Maze-ing**, 42 School'un "A-Maze-ing" subject'i için geliştirilmiş bir Python labirent (maze) üretici projesidir. Basit bir `config.txt` dosyası verildiğinde program, ya **perfect maze** (giriş ile çıkış arasında tam olarak tek bir yol, hiç döngü yok) ya da **imperfect / Pac-Man tarzı board** (tamamen bağlantılı, döngülü, köşeleri ve merkezi açık — kovalanan bir oyuncunun her zaman alternatif rotası olan) üretir. Üretilen labirent hexadecimal (onaltılık) formatta bir çıktı dosyasına yazılır, tamamen kapalı hücrelerden oluşan görünür bir "42" deseni içerir ve terminalde ANSI truecolor renkli bir ızgara olarak görselleştirilebilir. Labirent üretim mantığının kendisi, ileride başka projelerde import edilip yeniden kullanılabilmesi için ayrı, bağımsız bir paket (`mazegen`) haline getirilmiştir.

## Kurulum ve Çalıştırma (Instructions)

### Gereksinimler

- Python 3.10 veya üzeri
- Bağımlılıkların izole tutulması için bir sanal ortam (venv) kullanılması önerilir

### Kurulum

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
make install
```

`make install`, gerekli araçları (flake8, mypy, pytest) doğrudan `pip` ile sanal ortama kurar — repoda ayrı bir `requirements.txt` yoktur:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install flake8 mypy pytest
```

### Programı çalıştırma

```bash
python3 a_maze_ing.py config.txt
```

- `a_maze_ing.py`, subject'in zorunlu kıldığı sabit giriş noktası dosya adıdır.
- `config.txt`, tek argüman olan düz metin yapılandırma dosyasıdır (format aşağıda); farklı bir dosya adı da verilebilir.

### Makefile hedefleri

| Hedef         | Ne yapar                                                          |
|---------------|---------------------------------------------------------------------|
| `install`     | Proje bağımlılıklarını kurar                                        |
| `run`         | Ana script'i çalıştırır                                              |
| `debug`       | Ana script'i Python'un yerleşik debugger'ı (`pdb`) ile çalıştırır   |
| `clean`       | `__pycache__`, `.mypy_cache` gibi geçici dosyaları temizler         |
| `lint`        | `flake8 .` ve subject'in istediği bayraklarla `mypy .` çalıştırır   |
| `lint-strict` | `flake8 .` ve `mypy . --strict` çalıştırır                          |

`lint` hedefinin çalıştırdığı tam komutlar:

```bash
flake8 .
mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

### Çıktı dosyasını doğrulama

Üretilen herhangi bir çıktı dosyasını kontrol etmek için bir analiz betiği bulunmaktadır:

```bash
python3 maze_analyzer.py <output_file>
python3 maze_analyzer.py <output_file> --min-loops 2 --max-dead-ends 2
```

Bu betik şunları kontrol eder: hexadecimal grid formatı ve satır uzunluğu tutarlılığı, komşu hücreler arasındaki duvar tutarlılığı, girişten tam erişilebilirlik, çıkışın erişilebilirliği, köşe/merkez hücrelerinin erişilebilirliği, bağımsız loop/cycle sayısı, dead-end sayısı, bağlantısız (disconnected) koridorlar, ve labirentin **perfect** (`loops == 0`) mi yoksa **playable** bir non-perfect board mu (bağlantılılık + minimum loop sayısı + sınırlı dead-end) olduğu.

## Yapılandırma Dosyası Formatı (Config File Format)

Her satırda bir `KEY=VALUE` çifti bulunur. `#` ile başlayan satırlar yorum satırıdır ve yok sayılır.

| Anahtar       | Açıklama                              | Örnek                  |
|---------------|----------------------------------------|--------------------------|
| `WIDTH`       | Labirent genişliği (hücre sayısı)      | `WIDTH=20`               |
| `HEIGHT`      | Labirent yüksekliği                    | `HEIGHT=15`              |
| `ENTRY`       | Giriş koordinatı `(x,y)`               | `ENTRY=0,0`              |
| `EXIT`        | Çıkış koordinatı `(x,y)`               | `EXIT=19,14`             |
| `OUTPUT_FILE` | Çıktı dosyası adı                      | `OUTPUT_FILE=maze.txt`   |
| `PERFECT`     | Labirentin perfect olup olmayacağı     | `PERFECT=True`           |
| `SEED`        | (Opsiyonel) tekrar üretilebilirlik için tohum değeri | `SEED=42`  |

Repository'nin kök dizininde varsayılan bir `config.txt` bulunmaktadır. Geçersiz/eksik anahtarlar, dosya bulunamaması, hatalı sözdizimi veya imkânsız labirent parametreleri gibi durumlar `try/except` blokları ile yakalanır; program hiçbir zaman çökmez, her zaman anlamlı bir hata mesajı verir.

## Labirent Üretim Algoritması

### Veri temsili

Her hücre tek bir tamsayı olarak saklanır; her bit **kapalı** bir duvarı işaretler:

| Bit | Yön |
|-----|------|
| `1` (0b0001) | Kuzey (North) |
| `2` (0b0010) | Doğu (East)   |
| `4` (0b0100) | Güney (South) |
| `8` (0b1000) | Batı (West)   |

Her hücre başlangıçta tamamen kapalıdır (`15` = `1111`). İki hücre arasında bir geçiş açıldığında, ortak duvarın karşılık gelen bitleri **her iki hücrede birden** aynı anda temizlenir (örn. A hücresinin `EAST` biti temizlenirken, komşusunun `WEST` biti de temizlenir). Bu, subject'in istediği "komşu hücreler arasında tutarlı duvar kodlaması" kuralını sağlar ve tek bir `remove_wall()` fonksiyonu ile yapılır; bu fonksiyon iki hücrenin birbirine göre konumunu belirleyip doğru bit çiftini temizler.

### Algoritma seçimi: Recursive Backtracking (DFS)

Ana üretim algoritması olarak **rastgele derinlik öncelikli arama (randomized DFS) / recursive backtracking** seçildi:

1. Başlangıç hücresi ziyaret edilir ve ziyaret edildi olarak işaretlenir.
2. Ziyaret edilmemiş komşular bulunur.
3. Bunlardan biri rastgele seçilir.
4. Mevcut hücre ile seçilen komşu arasındaki duvar kaldırılır.
5. Seçilen komşu stack'e eklenir ve oraya geçilir.
6. Çıkmaza gelindiğinde, stack üzerinden ziyaret edilmemiş komşusu olan son hücreye geri dönülür (backtrack).
7. Ulaşılabilir tüm hücreler ziyaret edilene kadar devam edilir.

**Neden bu algoritma:** Bu yöntem ızgaranın doğal olarak bir **spanning tree**'sini (yayılma ağacı) üretir — yani herhangi iki hücre arasında tam olarak tek bir yol bulunan, hiç döngüsü olmayan bir perfect maze — ki bu tam olarak `PERFECT=True` modunun istediği şeydir. Stack tabanlı, yinelemeli (iterative) bir uygulama derin recursion sorunlarını da önler. Ayrıca anlaşılması ve üzerine geliştirme yapılması kolay bir algoritmadır.

`PERFECT=False` (varsayılan, Pac-Man tarzı board) için önce aynı spanning tree üretilir, ardından **üzerine ek geçişler açılarak** döngüler oluşturulur; bu sayede tam bağlantılılık korunurken alanlar arasında en az iki bağımsız rota garanti edilir ve dead-end sayısı düşük tutulur.

### Tekrar üretilebilirlik (Seed / PRNG)

Global `random` modülü yerine, üretici kendine ait bir PRNG (pseudo-random number generator) örneği kullanır:

```python
self.random = random.Random(seed)
```

Aynı `width`, `height` ve `seed` değerleri verildiğinde, tamamen aynı labirent tekrar üretilir; bu da üretim sürecini deterministik ve test edilebilir kılar.

### "42" Deseni

"42" şeklini (ve geliştirme sırasında test edilen "BYG", "Ç", "ALİ", "BİLAL" gibi diğer örnek desenleri) tanımlayan sabit bir lokal `(x, y)` koordinat kümesi, yapılandırılabilir bir `(pattern_x, pattern_y)` başlangıç noktasına göre kaydırılıp mutlak labirent koordinatlarına çevrilir:

```
(maze_x, maze_y) = (pattern_x + local_x, pattern_y + local_y)
```

Bu koordinatlar bir `blocked_cells` kümesinde tutulur ve normal koridor üretiminin dışında bırakılır — üretici bu hücreleri, labirenti içlerinden geçirmek yerine tamamen kapalı, izole hücreler olarak ele alır. Bu, subject'in "42" deseni için tanıdığı bağlantılılık istisnasına karşılık gelir. Labirent boyutu deseni sığdırmayacak kadar küçükse, "42" deseni atlanır ve konsola bir hata/uyarı mesajı yazdırılır (subject'in bu duruma özel gerekliliği).

### Komşuluk tespiti ve en kısa yol

`get_neighbors()`, bir hücreden dört ana yöne bakar; ızgara sınırları dışında kalan ya da `blocked_cells` içindeki koordinatları eler. Giriş-çıkış arasındaki en kısa yol, ağırlıksız bir ızgara olduğu için Dijkstra'ya gerek kalmadan **BFS (Breadth-First Search)** ile hesaplanır ve çıktı dosyası için `N`/`E`/`S`/`W` harflerinden oluşan bir string'e çevrilir.

### Dead-end tespiti

Yalnızca tek bir açık geçişi olan hücre dead-end (çıkmaz sokak) olarak sınıflandırılır. Bu, non-perfect labirentlerin kalitesini denetlemek (dead-end'lerin nadir olması gerekir) ve bonus olan "braided maze" (`--max-dead-ends 0`) hedefinin doğrulanması için kullanılır.

### Çıktı formatı

Hücreler satır satır, her hücre için bir hexadecimal karakter (4 bitlik duvar maskesi) olacak şekilde yazılır. Ardından bir boş satır ve şu üç satır gelir: giriş koordinatı, çıkış koordinatı, en kısa yolun N/E/S/W harfleriyle ifadesi. Tüm satırlar `\n` ile biter.

## Yeniden Kullanılabilir Modül (mazegen)

Labirent üretim mantığı, CLI, config parser ve görselleştirme kodundan bağımsız, kendi başına duran bir `MazeGenerator` sınıfı içinde (`mazegen` paketi) toplanmıştır; böylece `pip` ile kurulup başka bir projede import edilebilir.

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=15, seed=42)
gen.generate_perfect()                       # PERFECT modu; imperfect için gen.generate_imperfect()

grid = gen.grid                              # üretilen yapıya erişim (bitmask grid)
path = gen.get_solution((0, 0), (19, 14))    # en az bir çözüme erişim: (x, y) hücrelerinin listesi
gen.write_grid("maze.txt")                   # grid'i doğrudan bir dosyaya yazabilme
```

### Paketi build etme

```bash
pip install build
python -m build --outdir .
```

Bu komut `mazegen-*.whl` ve `mazegen-*.tar.gz` dosyalarını üretir (paketleme yapılandırması `pyproject.toml` içinde tanımlıdır).

> **Dikkat:** Subject, paket dosyasının **repository'nin kökünde** bulunmasını şart koşuyor. `python -m build` varsayılan olarak `dist/` klasörüne yazar — bu yüzden `--outdir .` ile doğrudan köke build edin, ya da build ettikten sonra `.whl`/`.tar.gz` dosyasını `dist/`'ten köke taşıyıp commit'leyin. Değerlendirme sırasında paket, verilen kaynaklardan bir virtualenv içinde yeniden build edilebilir olmalıdır.

### Lisans

Modül, repository kökündeki `LICENSE.md` dosyasında belirtilen **MIT Lisansı** ile dağıtılır. MIT, izin verici ve basit bir lisans olduğu için tercih edildi: sonraki projelerde bu labirent üreticisinin serbestçe yeniden kullanılmasına, değiştirilmesine ve dağıtılmasına, sadece orijinal lisans/telif bildirimi korunması şartıyla açıkça izin verir.

## Görselleştirme (Visualization)

Subject'in izin verdiği iki seçenekten (terminal ASCII / MLX) **terminal render** tercih edildi; proje MLX (MiniLibX) kullanmıyor.

- **Terminal render:** Bitmask'ten oluşturulan çift-çözünürlüklü piksel ızgarası (`visualization/ascii.py`) üzerinden ANSI truecolor blok render'ı. Duvarlar, giriş, çıkış ve "42" deseni ayrı renklerle gösterilir; en kısa yol için bir overlay (üst katman) desteği vardır.
- **Kullanıcı etkileşimleri (`a_maze_ing.py` içindeki interaktif menü):**
  1. Yeni bir labirent üret (seed varsa bir artırılarak yeniden üretilir),
  2. En kısa yolu göster/gizle,
  3. Duvar renklerini döndür (`WALL_PALETTE` içindeki renkler arasında geçiş),
  4. Çıkış.

## Ekip ve Proje Yönetimi (Team & Project Management)

- **Roller:** Bilal, labirent üretim algoritmalarına odaklandı (recursive backtracking, imperfect mod için döngü ekleme, seed/PRNG desteği, pattern/blocked-cell sistemi, hexadecimal çıktı, dead-end tespiti ve `maze_analyzer.py` doğrulama aracı). Ali ise yapılandırma dosyası okuma/doğrulama, ASCII/ANSI ve MLX görselleştirme, BFS ile en kısa yol bulma ve genel kod kalitesine (flake8/mypy uyumu, paketleme) odaklandı.
- **Planlama:** Çalışma, ayrı `ali` ve `bilal` dallarına (branch) bölündü; her iki taraf da kendi parçasını stabilize ettikten sonra `main`'e merge edildi. Bu sayede üretim ve görselleştirme birbirini bloklamadan paralel geliştirilebildi.
- **İyi giden şeyler:** Üretim ve görselleştirme sorumluluklarının en baştan ayrılması, iki tarafın da birbirini beklemeden ilerlemesini sağladı; duvar bitmask kuralının (N=1, E=2, S=4, W=8) en baştan sabitlenip paylaşılması, iki tarafın kodunu veri yeniden kodlamaya gerek kalmadan kolayca birleştirmeyi mümkün kıldı.
- **Geliştirilebilecek noktalar:** `config.txt` formatı ve varsayılan değerleri üzerinde daha erken senkronize olunması, dallar arasında farklılaşan config dosyalarını sonradan birleştirme zahmetini ortadan kaldırırdı; imperfect mod döngü mantığı, ilk planlanandan daha fazla iterasyon gerektirdi.
- **Kullanılan araçlar:** Git/GitHub (özellik dalları), kod kalitesi için flake8 ve mypy (subject'in istediği bayraklarla), birim testleri için pytest, çıktı doğruluğunu kontrol etmek için sağlanan `maze_analyzer.py`.

## Bonus Özellikler

- **Braided maze (dead-end'siz non-perfect labirent):** `generate_imperfect()`, tespit ettiği her dead-end hücresinden kapalı bir komşuya doğru bir duvar açtığı için pratikte neredeyse hiç dead-end bırakmıyor; test edilen örneklerde `maze_analyzer.py --max-dead-ends 0` ile "bonus-grade (perfectly braided)" sonucu alındı.
- **Çoklu algoritma desteği** ve **üretim sırasında animasyon** subject'te önerilen diğer bonus fikirlerdir; bu projede öncelik verilmemiştir (bkz. "Yol Haritası").

## Mevcut Durum

`ali` ve `bilal` dalları `main`'e merge edildi; proje mandatory kısım itibarıyla tamamlanmış durumda: config parser/validator, `MAX_DIMENSION`/`MAX_CELLS` sınırları, `check_entry_exit_not_blocked`, DFS tabanlı perfect/imperfect üretim, "42" deseni, hexadecimal çıktı, BFS ile en kısa yol, terminal ASCII/ANSI render ve interaktif menü, `mazegen` paketi, `maze_analyzer.py`, 17 pytest testi, flake8/mypy (subject'in istediği bayraklarla) temiz şekilde çalışıyor.

Teslimden önce hâlâ bakılması gereken noktalar:

- **Paket dosyasının konumu:** Subject, `mazegen-*.whl`/`.tar.gz` dosyasının repository'nin **kökünde** olmasını istiyor; şu an `dist/` klasöründe. `python -m build --outdir .` ile köke build edilmeli ya da build sonrası dosya köke taşınıp commit'lenmeli.


*(Bu bölüm, teslimden önce projenin gerçek son durumuna göre tekrar gözden geçirilmelidir.)*

## Kaynaklar (Resources)

- Jamis Buck, *Mazes for Programmers* — recursive backtracking, Prim's ve Kruskal's labirent üretim algoritmaları için temel kaynak.
- [Mazes for Programmers — Displaying a Maze on the Console](https://educative.io/courses/mazes-for-programmers/displaying-a-maze-on-the-console)
- [Real Python — Build a Maze Solver in Python Using Graphs](https://realpython.com/python-maze-solver/) (grid temsili, graf gezinme, BFS)
- [Invent with Python — How to Represent a 2D Grid in Python Code](https://inventwithpython.com/blog/represent-a-2d-grid-in-python.html)
- [Python resmi belgeleri — Sanal Ortamlar ve Paketler](https://docs.python.org/3/tutorial/venv.html)
- [MLX42 (Codam)](https://github.com/codam-coding-college/MLX42) / [42 Docs — MiniLibX Prototypes](https://harm-smits.github.io/42docs/libs/minilibx/prototypes.html)

**AI kullanımı:** Proje boyunca AI desteği (Claude), her zaman anlaşılıp gözden geçirildikten sonra tutulan bir öğrenme ve verimlilik aracı olarak kullanıldı:
- Uygulamadan önce temel kavramların (spanning tree, BFS ve DFS farkı, bitmask duvar temsili, sanal ortamlar, paketleme) açıklanması.
- Labirent üretim algoritması seçeneklerinin (recursive backtracking vs. Prim's vs. Kruskal's) karşılaştırılıp nihai yaklaşımın gerekçelendirilmesi.
- Kod yapısının gözden geçirilmesi ve hataların (örn. bağlantılılık kontrolündeki bir komşu-karşılaştırma hatası) tüm bir özelliği üretmek yerine tespit edilmesi.
- Bu README'nin, ekibin kendi çalışma notlarından ve subject gereksinimlerinden derlenip düzenlenmesi.

Hiçbir AI tarafından üretilen kod, onu commit eden kişi tarafından okunup test edilip anlaşılmadan projeye dahil edilmedi.
