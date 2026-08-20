from dataclasses import dataclass


@dataclass
class Config:
    """Validated, type-safe maze configuration settings."""
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool


def read_to_file(file: str) -> dict[str, str]:
    """Read a config file and return its raw KEY=VALUE pairs."""
    config: dict[str, str] = {}
    try:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.count("=") != 1:
                    raise ValueError(
                        f"Invalid line (must contain exactly one '='): {line}"
                    )
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
    except OSError as e:
        raise ValueError(f"Cannot read config file '{file}': {e}") from e
    except Exception as e:
        raise ValueError(f"Error reading config file '{file}': {e}") from e
    return config


REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}


def pars(config: dict[str, str]) -> Config:
    """Convert the raw string dictionary into a type-safe Config object."""
    missing: set[str] = REQUIRED_KEYS - config.keys()
    if missing:
        raise ValueError(f"Missing required key(s): {', '.join(sorted(missing))}")

    try:
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])
        entry_x, entry_y = (int(v) for v in config["ENTRY"].split(","))
        exit_x, exit_y = (int(v) for v in config["EXIT"].split(","))
        output_file = config["OUTPUT_FILE"]
        perfect = config["PERFECT"].strip().lower() == "true"
    except ValueError as e:
        raise ValueError(f"Invalid config value: {e}") from e

    return Config(
        width=width,
        height=height,
        entry=(entry_x, entry_y),
        exit=(exit_x, exit_y),
        output_file=output_file,
        perfect=perfect,
    )