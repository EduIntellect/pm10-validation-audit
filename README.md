# Operational Predictability Limits in Multi-Step PM₁₀ Forecasting

**A Systematic Audit and Reproducible Evaluation Framework for Temporal Validation**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18675212.svg)](https://doi.org/10.5281/zenodo.18675212)

This repository contains all code and data supporting the systematic audit of temporal validation practices in PM₁₀ forecasting literature (García Crespi et al., 2026).

## Repository Structure

```
pm10-validation-audit/
├── screening/          # Lexical screening pipeline (Section 2.2)
├── benchmark/          # H* synthetic benchmark (Section 3.5)
├── audit/              # Full-text audit forms and data (Section 2.3-2.4)
├── figures/            # Scripts to reproduce Figures 1-4
├── data/               # Corpus metadata and audit results
├── requirements.txt    # Python dependencies
├── environment.yml     # Conda environment
└── README.md           # This file
```

## Quick Start

### Installation

```bash
# Option 1: pip
pip install -r requirements.txt

# Option 2: conda
conda env create -f environment.yml
conda activate pm10-audit
```

### Reproduce Main Results

```bash
# 1. Run lexical screening (generates prevalence estimates)
cd screening
python run_screening.py

# 2. Compute H* benchmark (Figure 4)
cd ../benchmark
python hstar_demo.py

# 3. Reproduce all figures
cd ../figures
python reproduce_figures.py
```

## Data Availability

### Scopus Corpus (n=2,425)
- **Query string**: See `data/scopus_query.txt`
- **Execution date**: February 14, 2026
- **Record identifiers**: `data/scopus_eids.csv` (compliance with Elsevier policy)
- **Export instructions**: `data/scopus_export_howto.md`

### Audit Sample (n=15)
- **Metadata**: `audit/audit_sample_metadata.csv` (DOIs, citations, eras)
- **Audit form**: `audit/audit_form_template.xlsx` (3 sheets: form, completed example, rubric)
- **Results**: `data/audit_results_table.csv`

## Reproducibility

All scripts are deterministic and produce identical outputs given the same inputs. Random operations (bootstrap CIs) use fixed seeds.

### System Requirements
- Python 3.11+
- 8 GB RAM (sufficient for all analyses)
- ~50 MB disk space

### Expected Runtime
- Screening: < 5 min
- Benchmark: < 2 min  
- Figures: < 1 min

Tested on Ubuntu 24.04, macOS 14, Windows 11.

## Citation

If you use this code or data, please cite:

```bibtex
@article{garcia2026operational,
  title={Operational Predictability Limits in Multi-Step PM$_{10}$ Forecasting: A Systematic Audit and Reproducible Evaluation Framework for Temporal Validation},
  author={Garc{\'\i}a Crespi, Federico and Yubero Funes, Eduardo and Alfosea Sim{\'o}n, Marina},
  journal={Environmental Modelling \& Software},
  year={2026},
  doi={10.XXXX/XXXXX}
}
```

## License

Code: MIT License  
Data: CC BY 4.0

## Contact

Federico García Crespi – f.garcia@umh.es

## Acknowledgments

Scopus bibliographic data provided by Elsevier. Inter-rater reliability assessment conducted with colleague from Universidad Miguel Hernández.
