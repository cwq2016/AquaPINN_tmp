# AquaPINN Tracker 3D

AquaPINN estimates aquatic acoustic-tag positions and trajectories from detections recorded by hydrophones. The project includes a Python research pipeline and a Windows Auto desktop installer.

The pipeline can decode receiver recordings, synchronize receiver clocks using beacon tags, estimate trajectories with two solvers, and compare saved tracks with GPS references.

## What the terms mean

- A hydrophone is an acoustic receiver.
- A beacon is a tag placed near a receiver and used to estimate clock offsets.
- TOA means time of arrival. TDOA is the difference between arrival times at two receivers.
- PRI is the expected interval between transmissions from a tag.
- TagID is the zero-based row number in the tag catalogue. The tag code identifies the physical transmitter.

## Windows desktop installer

The Auto Online Setup is in [Windows_installer](Windows_installer/AquaPINN-Tracker-Auto-0.3.1-auto-rc4-Online-Setup.exe).

The installer is a single EXE. Internet access is required during setup to download the locked dependencies. After installation, tracking runs locally. No separate Python, pip, CUDA Toolkit, or terminal installation is required.

Choose Automatic to check for a usable NVIDIA GPU; if one is unavailable, the app can use CPU processing. GPU use requires a compatible NVIDIA driver. AMD and Intel graphics use CPU processing. The interface runs in the CPU environment, with numerical fitting isolated in a worker process.

The included candidate installer is unsigned. Follow your organization’s software installation policies. For setup details, see [Installation](docs/installation.md). For the desktop workflows, see the [User Guide](docs/user-guide.md).

The Auto desktop application is delivered as an installer; its application source is not included in this checkout.

## Research pipeline

The stages can be run separately through the Python package and example launchers:

1. Decode raw receiver CSV recordings into tag and beacon detections.
2. Synchronize receiver clocks from beacon detections when required.
3. Prepare TOA observations and estimate tag trajectories.
4. Compare saved trajectories with GPS references and generate plots or reports.

FishHeart uses raw receiver CSV files and normally runs all three processing stages. Sequim starts from time-corrected MATLAB detections, converts them to the tracking format, and does not require a new synchronization run. Synthetic scenarios provide controlled data for method comparisons.

More detail is in [Research workflows](docs/research-workflows.md).

## Tracking methods

| Method | Description | Configuration |
| --- | --- | --- |
| AML | Analytical multilateration; fast, pointwise position estimates | trackMethod = ["AML"] |
| NN | Neural trajectory model | trackMethod = ["NN"], nSamples = [1] |
| NN+ | Repeated NN fits; summarizes between-fit spread | trackMethod = ["NN"], nSamples greater than 1 |

NN+ spread is a sample-based estimate and is not a calibrated confidence interval. The valid trackMethod value remains NN; NNplus is the saved output label for repeated fits.

## Included examples

| Example | Inputs and workflow | Configuration |
| --- | --- | --- |
| FishHeart | Receiver CSV recordings, beacon synchronization, then tracking | Examples/fishHeart/run/params.toml |
| Sequim | Corrected MATLAB detections, conversion, then tracking | Examples/Sequim/run/params.toml |
| Synthetic | Generated trajectories and detections for benchmark scenarios | Examples/Synthetic/run/params.toml |

Check each configuration before running. Confirm the input paths, selected tag, time range, timezone, receiver geometry, and output folder. A TagID selects a row in the configured tag catalogue; it is not the tag code or receiver ID.

## Run in Jupyter or Google Colab

The Sequim notebook loads the existing `params.toml` directly; the other notebooks provide editable setup blocks. Colab copies results to Google Drive, and local Jupyter follows the configured output folder. Open a workflow directly in Colab:

| Workflow | Colab |
| --- | --- |
| Sequim Quickstart | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cwq2016/AquaPINN_tmp/blob/main/Examples/Colab/01_Sequim_Quickstart.ipynb) |
| Synthetic Benchmark | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cwq2016/AquaPINN_tmp/blob/main/Examples/Colab/02_Synthetic_Benchmark.ipynb) |
| FishHeart Full Pipeline | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cwq2016/AquaPINN_tmp/blob/main/Examples/Colab/03_FishHeart_Full_Pipeline.ipynb) |

See [the notebook guide](Examples/Colab/README.md) for input paths and output storage details. The repository must be public and the notebooks pushed to the `main` branch for these badges to open successfully.

## Research environment

Python 3.11 or later is recommended. The research pipeline uses PyTorch, NumPy, SciPy, pandas, Matplotlib, utm, NetworkX, scikit-learn, tqdm, and six. NumPy versions below 2.5 are recommended for the existing coordinate-conversion code.

There is no general package-install manifest or editable package setup. Install a PyTorch build appropriate for the machine, then install the remaining dependencies in an isolated environment. For example:

    python -m pip install torch "numpy<2.5" scipy pandas matplotlib utm networkx scikit-learn tqdm six

This is an unpinned starting point, not a fully reproduced research environment. CUDA is optional for the research scripts. Use the supplied example launchers rather than the legacy pipeline module.

## Run an example

Run commands from the repository root. Review the selected example’s parameters first.

    python Examples/fishHeart/run/main_FishHeart.py

The Sequim launcher follows its conversion-and-tracking workflow:

    python Examples/Sequim/run/main_Sequim.py

Synthetic data must be generated before tracking. The following commands perform generation, tracking, and comparison in sequence:

    python Examples/Synthetic/dataGenerator/caseDesign_CabotSynthetic.py
    python Examples/Synthetic/run/main.py
    python Examples/Synthetic/run/run_comparison.py

Training can take substantial time, especially on CPU. Repeated NN+ fits take longer than a single NN fit.

## Compare results

After generating the desired track files, run the example’s comparison launcher. For example:

    python Examples/fishHeart/run/run_comparison.py

Comparison scripts read existing results; they do not run missing solvers. The report script can summarize metrics from the comparison configuration:

    python AquaPINN_Tracker3D/PostProcess/report.py Examples/fishHeart/run/compare.toml

Use separate result directories for methods when comparing NN and NNplus. Confirm that the comparison selected the intended CSV files and that the GPS reference covers the interval being evaluated.

## Configuration notes

Pipeline parameter values are represented as lists to allow parameter combinations. For a single run, use one choice per setting. Vector settings are nested lists, for example region_lb = [[-200, -200, -20]].

Several boolean-like settings are strings, including ignoreZ and split_by_TestFile. Use ["True"] or ["False"] where the example configuration does so. Do not replace these with TOML booleans unless a parameter is documented as a real boolean.

Important settings include phoneFile, tagFile, dataFolder, GPSFile, time_start, time_end, timeZone, temperature_ref, trackMethod, nSamples, badPhones, and output_folder. Units, timezone conventions, receiver IDs, and tag-catalogue ordering must match the input data.

## Outputs

Depending on the stages and example, results can include:

- Decoded and synchronized detection pickle files.
- Corrected receiver-location CSV files.
- Prepared TOA data and detection summaries.
- Per-tag trajectory CSV files and solver sidecar files.
- Track plots, training histories, and parameter snapshots.
- GPS comparison plots, statistics, and report CSV files.

Outputs are written beneath the output folder configured for each example. Use a fresh output location when changing source data or preprocessing settings; some intermediate files are reused based on their existence.

## Interpretation limits

A completed run does not establish positional or clock accuracy. Coordinate units, vertical datum, time basis, sound-speed assumptions, GPS coverage, and receiver/tag offsets affect interpretation. Exported Z is elevation and should not automatically be interpreted as depth below water. Comparison reports may summarize error fields already stored in track CSVs rather than recomputing them from a newly selected GPS file.

For more, see [Limitations and validation](docs/limitations.md).

## License

The project is distributed under GNU GPL version 3 or later. Preserve the included license and disclaimer notices when redistributing. Confirm redistribution rights for example datasets and third-party components.

