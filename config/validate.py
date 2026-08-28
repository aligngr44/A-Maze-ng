from .read_file import Config

# GECICI/tahmini sinirlar - maze uretim algoritmasi yazildiktan sonra
# gercek RecursionError testiyle kesinlestirilmeli.
MAX_DIMENSION = 100
MAX_CELLS_PERFECT = 40000
MAX_CELLS_NON_PERFECT = 40000


def validate_config(cfg: Config) -> None:
    """Check whether the values in Config are logically valid."""
    errors: list[str] = []

    if cfg.width <= 0:
        errors.append(f"WIDTH must be positive, got: {cfg.width}")
    if cfg.height <= 0:
        errors.append(f"HEIGHT must be positive, got: {cfg.height}")

    if cfg.width > MAX_DIMENSION or cfg.height > MAX_DIMENSION:
        errors.append(
            f"WIDTH/HEIGHT too large (max {MAX_DIMENSION} per side), "
            f"got: {cfg.width}x{cfg.height}"
        )

    total_cells = cfg.width * cfg.height
    max_cells = MAX_CELLS_PERFECT if cfg.perfect else MAX_CELLS_NON_PERFECT
    if total_cells > max_cells:
        mode = "PERFECT=True" if cfg.perfect else "PERFECT=False"
        errors.append(
            f"Maze too large for {mode} mode ({cfg.width}x{cfg.height} = "
            f"{total_cells} cells, max {max_cells})"
        )

    ex, ey = cfg.entry
    xx, xy = cfg.exit

    if not (0 <= ex < cfg.width and 0 <= ey < cfg.height):
        errors.append(f"ENTRY is out of grid bounds: {cfg.entry}")
    if not (0 <= xx < cfg.width and 0 <= xy < cfg.height):
        errors.append(f"EXIT is out of grid bounds: {cfg.exit}")

    if cfg.entry == cfg.exit:
        errors.append(
            f"ENTRY and EXIT cannot be the same coordinate: {cfg.entry}"
        )

    if not cfg.output_file:
        errors.append("OUTPUT_FILE cannot be empty")

    if errors:
        raise ValueError("Config validation errors: " + "; ".join(errors))


def check_entry_exit_not_blocked(
    entry: tuple[int, int],
    exit_: tuple[int, int],
    blocked_cells: set[tuple[int, int]],
) -> None:
    if entry in blocked_cells or exit_ in blocked_cells:
        raise ValueError("Entry or exit overlaps with the '42' pattern")