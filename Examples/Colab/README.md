# AquaPINN Colab notebooks

Open a workflow directly in Google Colab:

| Workflow | Colab |
| --- | --- |
| Sequim Quickstart | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cwq2016/AquaPINN_tmp/blob/main/Examples/Colab/01_Sequim_Quickstart.ipynb) |
| Synthetic Benchmark | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cwq2016/AquaPINN_tmp/blob/main/Examples/Colab/02_Synthetic_Benchmark.ipynb) |
| FishHeart Full Pipeline | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cwq2016/AquaPINN_tmp/blob/main/Examples/Colab/03_FishHeart_Full_Pipeline.ipynb) |

The Sequim notebook reads its settings from the supplied `params.toml`. The Synthetic notebook has an editable setup block; FishHeart also reads its settings from `params.toml`. Colab saves results to Google Drive; local Jupyter uses the configured output folder.

Default input paths point to bundled examples. Custom paths can be entered in each notebook and may point to Drive. Only publish data approved for redistribution. Colab storage is temporary, so use the Drive-backed output folder for results you want to keep.
