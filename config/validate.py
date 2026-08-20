from .read_file import Config


def validate_config(cfg: Config) -> None:
    """Check whether the values in Config are logically valid."""
    errors: list[str] = []

    if cfg.width <= 0:
        errors.append(f"WIDTH must be positive, got: {cfg.width}")
    if cfg.height <= 0:
        errors.append(f"HEIGHT must be positive, got: {cfg.height}")

    ex, ey = cfg.entry
    xx, xy = cfg.exit

    if not (0 <= ex < cfg.width and 0 <= ey < cfg.height):
        errors.append(f"ENTRY is out of grid bounds: {cfg.entry}")
    if not (0 <= xx < cfg.width and 0 <= xy < cfg.height):
        errors.append(f"EXIT is out of grid bounds: {cfg.exit}")

    if cfg.entry == cfg.exit:
        errors.append(f"ENTRY and EXIT cannot be the same coordinate: {cfg.entry}")

    if not cfg.output_file:
        errors.append("OUTPUT_FILE cannot be empty")

    if errors:
        raise ValueError("Config validation errors: " + "; ".join(errors))
