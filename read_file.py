from dataclasses import dataclass  # dataclass: veri tutan basit sınıflar için hazır kod üreten araç


@dataclass  # bu sınıfın init/repr gibi kodlarını otomatik oluşturur, sadece alanları yazman yeterli
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool


def read_to_file(file: str) -> dict[str, str]:
    config: dict[str, str] = {}
    with open(file, "r", encoding="utf-8") as f:  # open: dosyayı açar, with bitince otomatik kapatır
        for line in f:
            line = line.strip()  # strip: baştaki/sondaki boşluk ve \n karakterlerini temizler
            if not line or line.startswith("#"):  # startswith: satır "#" ile mi başlıyor kontrol eder
                continue
            key, _, value = line.partition("=")  # partition: sadece ilk "=" işaretinden ikiye böler
            config[key.strip()] = value.strip()
    return config


REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}


def pars(config: dict[str, str]) -> Config:
    missing: set[str] = REQUIRED_KEYS - config.keys()
    if missing:
        raise ValueError(f"Eksik zorunlu anahtar(lar): {', '.join(sorted(missing))}")  # join+sorted: sıralayıp virgülle birleştirir

    try:
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])
        entry_x, entry_y = (int(v) for v in config["ENTRY"].split(","))  # split: string'i virgülden parçalara böler
        exit_x, exit_y = (int(v) for v in config["EXIT"].split(","))
        output_file = config["OUTPUT_FILE"]
        perfect = config["PERFECT"].strip().lower() == "true"  # lower: hepsini küçük harfe çevirir
    except ValueError as e:
        raise ValueError(f"Geçersiz config değeri: {e}") from e

    return Config(
        width=width,
        height=height,
        entry=(entry_x, entry_y),
        exit=(exit_x, exit_y),
        output_file=output_file,
        perfect=perfect,
    )
