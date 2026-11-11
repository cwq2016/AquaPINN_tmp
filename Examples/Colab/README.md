# AquaPINN Colab notebooks

These notebooks provide guided parameter setup for the existing AquaPINN workflows. In Colab, run outputs are written to Google Drive by default; local Jupyter uses a local results folder.

## Notebooks

1. **01_Sequim_Quickstart.ipynb** — corrected Sequim MAT detections, AML by default, and a Simple Example-compatible run.json.
2. **02_Synthetic_Benchmark.ipynb** — generated synthetic scenario, tracking, and comparison with known reference positions.
3. **03_FishHeart_Full_Pipeline.ipynb** — one selected tag through decode, synchronization, and tracking, with a Full Study-style run record.

## Before publishing

This checkout has no Git remote configured. Set REPO_URL in each notebook to the public clone URL before publishing. Add Colab badges after the repository owner and branch are known.

Default input paths point to bundled examples. Custom paths can be entered in each notebook and may point to Drive. Only publish data approved for redistribution. Colab storage is temporary, so use the Drive-backed output folder for results you want to keep.
