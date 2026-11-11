"""Internal helpers used by the Sequim Colab notebook."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


def prepare_output_folder(repo_dir: Path) -> Path:
    """Use Google Drive in Colab, or a local folder in Jupyter."""
    try:
        from google.colab import drive
        drive.mount("/content/drive")
        parent = Path("/content/drive/MyDrive/AquaPINN_Results")
    except ImportError:
        parent = Path(repo_dir) / "AquaPINN_Colab_Runs"
    parent.mkdir(parents=True, exist_ok=True)
    return parent


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")


def run_sequim(*, repo_dir: Path, output_parent: Path, mat_file: Path,
               phone_file: Path, tag_file: Path, test_file: Path | None,
               gps_file: Path | None, method: str, nnplus_samples: int,
               time_start: str, time_end: str, time_zone_hours: int,
               temperature_c: float, horizontal_only: bool, device: str):
    """Run the existing Sequim launcher and save a desktop-style result folder."""
    import tomllib
    import tomli_w

    repo_dir = Path(repo_dir).resolve()
    output_parent = Path(output_parent).resolve()
    mat_file = Path(mat_file).expanduser().resolve()
    phone_file = Path(phone_file).expanduser().resolve()
    tag_file = Path(tag_file).expanduser().resolve()
    test_file = Path(test_file).expanduser().resolve() if test_file else None
    gps_file = Path(gps_file).expanduser().resolve() if gps_file else None
    for label, path in (("MAT detections", mat_file), ("receiver locations", phone_file),
                        ("tag catalogue", tag_file)):
        if not path.is_file():
            raise FileNotFoundError(f"{label} not found: {path}")

    run_id = uuid.uuid4().hex
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_parent / f"Sequim_{stamp}_{run_id[:8]}"
    run_dir.mkdir(parents=True, exist_ok=False)
    inputs = run_dir / "inputs"
    inputs.mkdir()
    staged_mat = inputs / mat_file.name
    shutil.copy2(mat_file, staged_mat)
    results = run_dir / "results"

    seq_run = repo_dir / "Examples/Sequim/run"
    with (seq_run / "params.toml").open("rb") as stream:
        params = tomllib.load(stream)
    engine_method = "AML" if method == "AML" else "NN"
    fit_count = 1 if method != "NNplus" else int(nnplus_samples)
    params.update({
        "TagID": [2],
        "phoneFile": [str(phone_file)],
        "tagFile": [str(tag_file)],
        "testFile": [str(test_file) if test_file else ""],
        "GPSFile": [str(gps_file) if gps_file else ""],
        "dataFolder": [str(inputs)],
        "output_folder": [str(results)],
        "time_start": [str(time_start)],
        "time_end": [str(time_end)],
        "timeZone": [int(time_zone_hours)],
        "temperature_ref": [float(temperature_c)],
        "ignoreZ": ["True" if horizontal_only else "False"],
        "trackMethod": [engine_method],
        "nSamples": [fit_count],
    })
    effective_toml = run_dir / "params_effective.toml"
    effective_toml.write_text(tomli_w.dumps(params), encoding="utf-8")
    _write_json(run_dir / "params_effective.json", params)

    track_rel = f"results/Track/track/track_Tag2_G726777EF_{method}.csv"
    record = {"schema": 1, "run_id": run_id, "state": "starting",
              "method": method, "track_csv": track_rel}
    _write_json(run_dir / "run.json", record)
    sources = [mat_file, staged_mat, phone_file, tag_file]
    sources += [path for path in (test_file, gps_file) if path]
    _write_json(run_dir / "source-input-hashes.json",
                {str(path): _sha256(path) for path in sources})
    _write_json(run_dir / "worker.json",
                {"run_id": run_id, "state": "running", "stage": "Tracking"})

    launcher_source = (seq_run / "main_Sequim.py").read_text(encoding="utf-8")
    launcher_source = launcher_source.replace(
        'SCRIPT_DIR   = Path(__file__).resolve().parent',
        f'SCRIPT_DIR   = Path(r"{seq_run}")')
    launcher_source = launcher_source.replace(
        'param_file = str(SCRIPT_DIR / "params.toml")',
        f'param_file = r"{effective_toml}"')
    launcher = run_dir / "colab_launcher.py"
    launcher.write_text(launcher_source, encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(seq_run) + os.pathsep + env.get("PYTHONPATH", "")
    if device == "CPU only":
        env["CUDA_VISIBLE_DEVICES"] = ""
    with (run_dir / "console.log").open("w", encoding="utf-8") as log:
        completed = subprocess.run([sys.executable, str(launcher)], cwd=seq_run,
                                   env=env, stdout=log,
                                   stderr=subprocess.STDOUT, text=True)

    track_csv = run_dir / track_rel
    if completed.returncode != 0 or not track_csv.is_file() or not Path(str(track_csv) + ".pickle").is_file():
        record["state"] = "failed"
        _write_json(run_dir / "run.json", record)
        _write_json(run_dir / "worker.json",
                    {"run_id": run_id, "state": "failed", "exit_code": completed.returncode})
        raise RuntimeError(f"Sequim did not complete. See the run folder: {run_dir}")

    track_hash = _sha256(track_csv)
    record.update(state="completed", track_sha256=track_hash)
    _write_json(run_dir / "run.json", record)
    _write_json(run_dir / "worker.json",
                {"run_id": run_id, "state": "completed", "track_csv": track_rel,
                 "track_sha256": track_hash})
    return run_dir, track_csv
