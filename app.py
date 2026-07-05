from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import parse_qs, unquote

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs" / "latest"
REPORTS_DIR = ROOT / "reports"
WEB_DIR = ROOT / "web"
STATIC_DIR = WEB_DIR / "static"


def _json_response(start_response, payload: dict, status: str = "200 OK"):
    body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
        ],
    )
    return [body]


def _text_response(start_response, text: str, status: str = "200 OK", content_type: str = "text/plain; charset=utf-8"):
    body = text.encode("utf-8")
    start_response(status, [("Content-Type", content_type), ("Content-Length", str(len(body)))])
    return [body]


def _file_response(start_response, path: Path):
    if not path.exists() or not path.is_file():
        return _text_response(start_response, "Not found", "404 Not Found")
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = path.read_bytes()
    start_response(
        "200 OK",
        [
            ("Content-Type", content_type),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "public, max-age=60"),
        ],
    )
    return [body]


def _safe_child(root: Path, relative: str) -> Path | None:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _latest_snapshot_dir() -> Path | None:
    if not REPORTS_DIR.exists():
        return None
    candidates = [path for path in REPORTS_DIR.iterdir() if path.is_dir() and (path / "report.html").exists()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: path.name)[-1]


def _active_data_dir() -> Path:
    if (OUTPUT_DIR / "latest_regime_alpha_0.05.csv").exists() or (OUTPUT_DIR / "report.html").exists():
        return OUTPUT_DIR
    snapshot = _latest_snapshot_dir()
    return snapshot if snapshot else OUTPUT_DIR


def _alpha_token(value: str | float | int | None) -> str | None:
    if value is None or value == "":
        return None
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return None


def _detect_alpha_token(data_dir: Path, requested: str | None = None) -> str:
    if requested and (data_dir / f"latest_regime_alpha_{requested}.csv").exists():
        return requested
    candidates = list(data_dir.glob("latest_regime_alpha_*.csv"))
    if not candidates:
        return requested or "0.05"
    latest = max(candidates, key=lambda path: path.stat().st_mtime)
    return latest.stem.removeprefix("latest_regime_alpha_")


def _read_csv(path: Path, limit: int | None = None, sort_by: str | None = None, ascending: bool = False) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    if sort_by and sort_by in frame.columns:
        frame = frame.sort_values(sort_by, ascending=ascending, na_position="last")
    if limit is not None:
        frame = frame.head(limit)
    return frame


def _records(frame: pd.DataFrame) -> list[dict]:
    if frame.empty:
        return []
    clean = frame.replace({np.nan: None})
    return clean.to_dict(orient="records")


def _first_existing(data_dir: Path, names: list[str]) -> Path | None:
    for name in names:
        path = data_dir / name
        if path.exists():
            return path
    return None


def _dashboard_payload(alpha: str | float | int | None = None) -> dict:
    data_dir = _active_data_dir()
    alpha_key = _detect_alpha_token(data_dir, _alpha_token(alpha))
    latest_regime = _read_csv(data_dir / f"latest_regime_alpha_{alpha_key}.csv")
    flow = _read_csv(data_dir / f"flow_candidates_alpha_{alpha_key}.csv", limit=30, sort_by="score")
    risk = _read_csv(data_dir / f"risk_contagion_candidates_alpha_{alpha_key}.csv", limit=30, sort_by="score")
    matched = _read_csv(data_dir / f"matched_sector_metrics_alpha_{alpha_key}.csv", limit=20)
    garch = _read_csv(data_dir / "garch_params.csv", limit=30)
    coverage = _read_csv(data_dir / "asset_coverage.csv", limit=30)
    metrics = _read_csv(data_dir / f"pair_metrics_alpha_{alpha_key}.csv")

    as_of = None
    regime_counts: dict[str, int] = {}
    if not latest_regime.empty:
        if "as_of_date" in latest_regime.columns:
            as_of = str(latest_regime["as_of_date"].dropna().iloc[0])
        if "regime" in latest_regime.columns:
            regime_counts = latest_regime["regime"].value_counts(dropna=False).to_dict()

    top_lower = pd.DataFrame()
    top_upper = pd.DataFrame()
    top_middle = pd.DataFrame()
    if not metrics.empty:
        top_lower = metrics.sort_values("lower_tail_dependence", ascending=False, na_position="last").head(15)
        top_upper = metrics.sort_values("upper_tail_dependence", ascending=False, na_position="last").head(15)
        top_middle = metrics.sort_values("middle_pearson", ascending=False, na_position="last").head(15)

    heatmap_names = [
        "lower_tail_dependence.svg",
        "upper_tail_dependence.svg",
        "middle_pearson_correlation.svg",
        "middle_spearman_correlation.svg",
        "lower_co_crash_lift.svg",
        "upper_co_rally_lift.svg",
        "pearson_correlation.svg",
        "spearman_correlation.svg",
    ]
    heatmaps = [
        {
            "name": name,
            "label": name.replace("_", " ").replace(".svg", "").title(),
            "url": f"/report-assets/{name}",
        }
        for name in heatmap_names
        if (data_dir / name).exists()
    ]

    report_path = _first_existing(data_dir, ["report.html"])
    summary = {
        "data_dir": str(data_dir.relative_to(ROOT)) if data_dir.exists() else str(data_dir),
        "as_of_date": as_of,
        "alpha": float(alpha_key),
        "alpha_file_token": alpha_key,
        "regime_counts": regime_counts,
        "flow_count": int(flow.shape[0]),
        "risk_count": int(risk.shape[0]),
        "latest_report_url": "/report-assets/report.html" if report_path else None,
        "uses_live_outputs": data_dir == OUTPUT_DIR,
    }

    return {
        "summary": summary,
        "latestRegime": _records(latest_regime),
        "flowCandidates": _records(flow),
        "riskCandidates": _records(risk),
        "matchedSectors": _records(matched),
        "garchParams": _records(garch),
        "coverage": _records(coverage),
        "topLower": _records(top_lower),
        "topUpper": _records(top_upper),
        "topMiddle": _records(top_middle),
        "heatmaps": heatmaps,
    }


def _refresh_from_body(environ) -> dict:
    length = int(environ.get("CONTENT_LENGTH") or 0)
    raw = environ["wsgi.input"].read(length) if length else b"{}"
    try:
        params = json.loads(raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        params = {}

    today = date.today()
    start = params.get("start") or (today - timedelta(days=365 * 7)).isoformat()
    end = params.get("end") or today.isoformat()
    alpha = _alpha_token(params.get("alpha")) or "0.05"
    no_garch = bool(params.get("noGarch"))

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_analysis.py"),
        "--start",
        start,
        "--end",
        end,
        "--alpha",
        alpha,
        "--output",
        str(OUTPUT_DIR),
    ]
    if no_garch:
        cmd.append("--no-garch")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=900)
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
        "dashboard": _dashboard_payload(alpha=alpha) if result.returncode == 0 else None,
    }


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = unquote(environ.get("PATH_INFO", "/"))

    if method == "GET" and path == "/":
        return _file_response(start_response, WEB_DIR / "index.html")
    if method == "GET" and path == "/healthz":
        return _json_response(start_response, {"ok": True})
    if method == "GET" and path == "/api/dashboard":
        try:
            query = parse_qs(environ.get("QUERY_STRING", ""))
            return _json_response(start_response, _dashboard_payload(alpha=(query.get("alpha") or [None])[0]))
        except Exception as exc:  # pragma: no cover - defensive web boundary.
            return _json_response(start_response, {"error": str(exc)}, "500 Internal Server Error")
    if method == "POST" and path == "/api/refresh":
        try:
            payload = _refresh_from_body(environ)
            status = "200 OK" if payload["ok"] else "500 Internal Server Error"
            return _json_response(start_response, payload, status)
        except subprocess.TimeoutExpired:
            return _json_response(start_response, {"ok": False, "error": "analysis timed out"}, "504 Gateway Timeout")
        except Exception as exc:  # pragma: no cover - defensive web boundary.
            return _json_response(start_response, {"ok": False, "error": str(exc)}, "500 Internal Server Error")

    if method == "GET" and path.startswith("/static/"):
        child = _safe_child(STATIC_DIR, path.removeprefix("/static/"))
        return _file_response(start_response, child) if child else _text_response(start_response, "Not found", "404 Not Found")

    if method == "GET" and path.startswith("/report-assets/"):
        data_dir = _active_data_dir()
        child = _safe_child(data_dir, path.removeprefix("/report-assets/"))
        return _file_response(start_response, child) if child else _text_response(start_response, "Not found", "404 Not Found")

    if method == "GET" and path == "/api/raw":
        query = parse_qs(environ.get("QUERY_STRING", ""))
        name = (query.get("file") or [""])[0]
        child = _safe_child(_active_data_dir(), name)
        return _file_response(start_response, child) if child else _text_response(start_response, "Not found", "404 Not Found")

    return _text_response(start_response, "Not found", "404 Not Found")


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    port = int(os.environ.get("PORT", "8000"))
    with make_server("127.0.0.1", port, app) as server:
        print(f"Serving on http://127.0.0.1:{port}")
        server.serve_forever()
