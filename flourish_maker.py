import argparse
import csv
import math
from pathlib import Path
from typing import List, Optional, Tuple


def discover_input_files(directory: Path, include_glob: Optional[str]) -> List[Path]:
    if include_glob:
        return sorted(p for p in directory.glob(include_glob) if p.is_file())
    return sorted(
        p
        for p in directory.glob("*.csv")
        if (
            p.is_file()
            and p.name.lower().startswith("frameview_")
            and p.name != "FrameView_Summary.csv"
        )
    )


def parse_float(value: str) -> Optional[float]:
    if value is None:
        return None
    s = value.strip()
    if not s or s.upper() == "NA":
        return None
    try:
        return float(s)
    except ValueError:
        # Sometimes decimals can contain commas depending on locale.
        try:
            return float(s.replace(",", "."))
        except ValueError:
            return None


def pick_row_name(file_path: Path, header: List[str], first_row: List[str]) -> str:
    # Use filename as base for label
    stem = file_path.stem
    name = stem

    # Clean up common filename patterns
    if stem.startswith("FrameView_"):
        name = stem[len("FrameView_") :]

    # Remove common suffixes
    if name.endswith("_Log"):
        name = name[: -len("_Log")]

    # Remove timestamp patterns like _2025_08_05T111448
    tokens = name.split("_")
    filtered: List[str] = []
    for tok in tokens:
        # Skip timestamp-like tokens
        if "T" in tok and len(tok) > 8 and tok.replace("T", "").isdigit():
            continue
        # Skip pure date tokens like 2025, 08, 05
        if tok.isdigit() and len(tok) in [2, 4]:
            continue
        filtered.append(tok)
    name = "_".join(filtered) if filtered else stem

    # Clean up the name for Flourish compatibility
    # Remove file extensions and special characters that might cause issues
    name = name.replace(".exe", "").replace(".dll", "").replace(".", "_")
    # Replace other potentially problematic characters
    name = name.replace("(", "").replace(")", "").replace("%", "pct").replace(" ", "_")

    # Ensure the name is not empty and starts with a letter or underscore
    if not name or name[0].isdigit():
        name = f"App_{name}" if name else "Unknown"

    return name


class MetricKind:
    AVG_FPS = "avg_fps"  # uses displayed frame time by default
    PRESENT_FPS = "present_fps"  # uses MsBetweenPresents
    DISPLAY_FPS = "display_fps"  # uses MsBetweenDisplayChange
    COLUMN_PREFIX = "column:"  # e.g., column:GPU0Util(%)


def resolve_metric_column(header: List[str], metric: str) -> Tuple[str, bool]:
    """
    Returns (column_name, transform_is_ms_to_fps).
    If transform_is_ms_to_fps is True, convert ms to FPS as 1000/ms.
    """
    # Normalize header mapping for quick checks
    header_set = set(header)

    if metric == MetricKind.AVG_FPS:
        # Default to display time; fall back to present if display not
        # available
        if "MsBetweenDisplayChange" in header_set:
            return "MsBetweenDisplayChange", True
        if "MsBetweenPresents" in header_set:
            return "MsBetweenPresents", True
        raise ValueError(
            "Neither MsBetweenDisplayChange nor MsBetweenPresents found in CSV header"
        )

    if metric == MetricKind.PRESENT_FPS:
        if "MsBetweenPresents" in header_set:
            return "MsBetweenPresents", True
        raise ValueError("MsBetweenPresents column not found")

    if metric == MetricKind.DISPLAY_FPS:
        if "MsBetweenDisplayChange" in header_set:
            return "MsBetweenDisplayChange", True
        raise ValueError("MsBetweenDisplayChange column not found")

    if metric.startswith(MetricKind.COLUMN_PREFIX):
        col = metric[len(MetricKind.COLUMN_PREFIX) :]
        if col not in header_set:
            raise ValueError(f"Column not found in CSV header: {col}")
        return col, False

    # Legacy option: allow metric == some exact header
    if metric in header_set:
        return metric, False

    raise ValueError(f"Unsupported metric: {metric}")


def compute_per_second_series(
    file_path: Path,
    metric: str,
    fps_mode: str = "per-frame-mean",
) -> Tuple[str, List[Optional[float]]]:
    """
    Streams the CSV, computes a per-second series for the chosen metric.
    Returns (row_name, series) where series is a list where index 0 corresponds
    to second 1.
    """
    sums: List[float] = []  # For FPS: sum ms; for others: sum values
    counts: List[int] = []
    row_name: str = file_path.stem
    base_time: Optional[float] = None

    with file_path.open("r", newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return (row_name, [])

        # Peek the first data row to get a friendlier name; keep it too
        try:
            first_row = next(reader)
        except StopIteration:
            return (row_name, [])

        row_name = pick_row_name(file_path, header, first_row)

        # Resolve columns
        try:
            t_idx = header.index("TimeInSeconds")
        except ValueError as exc:
            raise ValueError("TimeInSeconds column not found in CSV") from exc

        metric_col, transform_ms_to_fps = resolve_metric_column(header, metric)
        m_idx = header.index(metric_col)

        def process_row(row: List[str]):
            nonlocal base_time, sums, counts
            if t_idx >= len(row) or m_idx >= len(row):
                return
            t = parse_float(row[t_idx])
            if t is None:
                return
            if base_time is None:
                base_time = t
            rel_t = t - base_time
            if rel_t < 0:
                # Should not happen, but guard anyway
                rel_t = 0.0
            # 0-based index for second buckets
            sec_idx = int(math.floor(rel_t))

            val_raw = parse_float(row[m_idx])
            if val_raw is None:
                return
            if transform_ms_to_fps:
                # Accumulate milliseconds; later compute FPS as
                # 1000 * count / sum_ms
                if val_raw <= 0:
                    return
                value = val_raw
            else:
                value = val_raw

            # Ensure capacity
            if sec_idx >= len(sums):
                grow_by = sec_idx + 1 - len(sums)
                sums.extend([0.0] * grow_by)
                counts.extend([0] * grow_by)
            sums[sec_idx] += value
            counts[sec_idx] += 1

        # Process the first row and the rest
        process_row(first_row)
        for row in reader:
            process_row(row)

    # Finalize series: average per second (or use count if fps_mode == 'count')
    series: List[Optional[float]] = []
    if fps_mode == "count":
        for c in counts:
            series.append(float(c))
    else:
        for s, c in zip(sums, counts):
            if c <= 0:
                series.append(None)
                continue
            if metric in (
                MetricKind.AVG_FPS,
                MetricKind.PRESENT_FPS,
                MetricKind.DISPLAY_FPS,
            ):
                # s is sum of ms; compute average FPS over the second window
                if s <= 0:
                    series.append(None)
                else:
                    series.append(1000.0 * c / s)
            else:
                # Simple arithmetic mean for arbitrary columns
                series.append(s / c)

    # Trim trailing None seconds if present
    while series and series[-1] is None:
        series.pop()

    return row_name, series


def write_flourish_wide_csv(
    output_path: Path,
    rows: List[Tuple[str, List[Optional[float]]]],
):
    if not rows:
        # Create an empty file with just the header
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Label"])
        return

    # Determine common length: shortest series
    min_len = min(len(series) for _, series in rows)
    if min_len == 0:
        # No data; still write header only
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Label"])
        return

    header = ["Label"] + [str(i + 1) for i in range(min_len)]

    def fmt(x: Optional[float]) -> str:
        if x is None or math.isnan(x):
            return ""
        # Limit to 3 decimal places, drop trailing zeros
        return f"{x:.3f}".rstrip("0").rstrip(".")

    # Ensure unique labels by adding suffixes if needed
    seen_labels = {}
    unique_rows = []
    for name, series in rows:
        if name in seen_labels:
            seen_labels[name] += 1
            unique_name = f"{name}_{seen_labels[name]}"
        else:
            seen_labels[name] = 1
            unique_name = name
        unique_rows.append((unique_name, series))

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for name, series in unique_rows:
            trimmed = series[:min_len]
            formatted_values = [fmt(v if v is not None else 0.0) for v in trimmed]
            row = [name] + formatted_values
            writer.writerow(row)


def compute_difference_series(
    base: List[Optional[float]],
    other: List[Optional[float]],
) -> List[Optional[float]]:
    min_len = min(len(base), len(other))
    diff: List[Optional[float]] = []
    for i in range(min_len):
        a = base[i]
        b = other[i]
        if a is None or b is None or a == 0:
            diff.append(None)
            continue
        diff.append(100.0 * (b / a - 1.0))
    return diff


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convert NVIDIA FrameView logs to Flourish wide CSV (Bar chart race)."
        )
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="in",
        help="Directory containing FrameView CSV logs (default: in)",
    )
    parser.add_argument(
        "--glob",
        type=str,
        default=None,
        help="Glob pattern to filter input files (e.g. 'FrameView_*.csv')",
    )
    parser.add_argument(
        "--inputs",
        type=str,
        nargs="*",
        default=None,
        help=(
            "Explicit paths to CSV logs. If provided, overrides --glob and "
            "--dir discovery"
        ),
    )
    parser.add_argument(
        "--output",
        type=str,
        default="flourish_out.csv",
        help="Output CSV path (default: flourish_out.csv)",
    )
    parser.add_argument(
        "--metric",
        type=str,
        default=MetricKind.AVG_FPS,
        help=(
            "Metric to compute per second. Options: "
            f"'{MetricKind.AVG_FPS}' (default, uses displayed frame time), "
            f"'{MetricKind.PRESENT_FPS}', '{MetricKind.DISPLAY_FPS}', or "
            f"{MetricKind.COLUMN_PREFIX}<ExactHeader> (e.g., "
            "column:GPU0Util(%) to average that column)."
        ),
    )
    parser.add_argument(
        "--fps-mode",
        type=str,
        default="per-frame-mean",
        choices=["per-frame-mean", "count"],
        help=(
            "For FPS metrics, average per-frame FPS within each second or "
            "just count frames per second (default: per-frame-mean)"
        ),
    )
    parser.add_argument(
        "--compare",
        type=str,
        nargs=2,
        default=None,
        help=(
            "Compare two logs and add a third row with percentage difference "
            "relative to the first"
        ),
    )
    parser.add_argument(
        "--difference-only",
        action="store_true",
        help="When using --compare, output only the difference row",
    )

    args = parser.parse_args()

    directory = Path(args.dir)
    if args.inputs:
        files = [Path(p) for p in args.inputs]
    else:
        files = discover_input_files(directory, args.glob)

    rows: List[Tuple[str, List[Optional[float]]]] = []

    if args.compare:
        # Compare mode: override inputs with the two specified files
        comp_files = [Path(p) for p in args.compare]
        series_data: List[Tuple[str, List[Optional[float]]]] = []
        for p in comp_files:
            if not p.exists():
                raise FileNotFoundError(f"Input not found: {p}")
            name, series = compute_per_second_series(
                p, args.metric, fps_mode=args.fps_mode
            )
            series_data.append((name, series))
        # Compute difference
        (name_a, series_a), (name_b, series_b) = series_data
        diff_series = compute_difference_series(series_a, series_b)
        if args.difference_only:
            rows = [("%", diff_series)]
        else:
            rows = [
                (name_a, series_a),
                (name_b, series_b),
                ("%", diff_series),
            ]
    else:
        if not files:
            raise SystemExit(
                "No input files found. Use --inputs or adjust --dir/--glob."
            )
        for p in files:
            if not p.exists():
                raise FileNotFoundError(f"Input not found: {p}")
            name, series = compute_per_second_series(
                p, args.metric, fps_mode=args.fps_mode
            )
            rows.append((name, series))

    output_path = Path(args.output)
    write_flourish_wide_csv(output_path, rows)
    print(f"Wrote {output_path} with {len(rows)} row(s).")


if __name__ == "__main__":
    main()
