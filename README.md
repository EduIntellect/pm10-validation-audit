````markdown
# A PRISMA-Based Quantitative Audit of Validation Practices in Particulate Matter Forecasting Studies

**Evidence of Systematic Methodological Failures and a Minimum Evaluation Checklist**

[![DOI](https://zenodo.org/badge/DOI/[to-be-updated].svg)](https://doi.org/[to-be-updated])

This repository contains the materials supporting a **PRISMA-based quantitative audit** of methodological practices in particulate matter forecasting studies.

The repository is designed to document, reproduce, and archive the review workflow used to identify, screen, assess, and audit the selected literature, with a specific focus on:

- temporal validation practices,
- leakage risk,
- use of persistence and other simple baselines,
- horizon-wise reporting,
- and the operational interpretability of forecasting results.

This repository corresponds to the **systematic review / methodological audit paper** and should not be confused with the separate repository associated with the PM10 forecasting framework paper.

## Repository Scope

This repository supports a review study centered on the following question:

> **To what extent do recent particulate matter forecasting studies implement methodologically sound validation and evaluation practices?**

The repository is intended to provide:

- a transparent PRISMA workflow,
- structured screening and eligibility materials,
- full-text audit forms,
- coded methodological variables,
- quantitative summary tables,
- and the basis for the final **minimum evaluation checklist**.

## Repository Structure

```text
slr-prisma-pm-forecasting/
├── screening/          # Search, screening, and eligibility materials
├── audit/              # Full-text audit forms, coding rules, and completed audits
├── data/               # PRISMA counts, study metadata, and audit summary tables
├── figures/            # Scripts and assets used to reproduce manuscript figures
├── tables/             # Exportable tables for manuscript integration
├── docs/               # Supplementary notes, protocol details, and working documents
├── requirements.txt    # Python dependencies, if applicable
├── environment.yml     # Conda environment, if applicable
└── README.md           # This file
````

## Review Workflow

The review was conducted as a structured PRISMA-style workflow including:

1. **Database search**
2. **Deduplication**
3. **Title/abstract screening**
4. **Eligibility assessment**
5. **Full-text methodological audit**
6. **Quantitative synthesis of audit variables**

## Search Sources

* **Databases**: Scopus and Web of Science
* **Search and filtering period**: March 21–23, 2026
* **Search strings**: stored in the repository query files
* **Export metadata**: stored in repository data files

## PRISMA Materials

The repository includes, where applicable:

* search strings,
* export instructions,
* screening rules,
* inclusion/exclusion criteria,
* PRISMA flow counts,
* full-text audit template,
* completed audit forms,
* and aggregated methodological results.

## Data Availability

### Search and Screening Records

Repository files document the search sources, screening process, and eligibility decisions used in the review.

### Audit Dataset

The methodological audit dataset contains the coded variables used to quantify recurrent weaknesses in the reviewed studies, including:

* validation design,
* temporal split adequacy,
* leakage risk,
* baseline usage,
* metric reporting,
* and forecast horizon treatment.

### Reproducibility Note

This repository is intended to make the review process **transparent, inspectable, and reproducible**.
Because bibliographic database licenses may restrict redistribution of full raw exports, the repository may store **record identifiers, derived tables, and documentation of export procedures** instead of full proprietary exports.

## Main Outputs Supported by This Repository

This repository supports the generation or archiving of the following outputs:

* PRISMA flow information,
* corpus and eligibility metadata,
* full-text audit evidence,
* methodological frequency tables,
* quantitative summaries of recurrent failures,
* and the final **minimum evaluation checklist** proposed in the paper.

Where applicable, scripts are included to regenerate summary tables and figures from the coded audit data.

## Reproducibility

All repository materials are organized to support transparent reconstruction of the review workflow and audit results.

### System Requirements

* Python **[version to be inserted]**
* Standard scientific Python stack **[if applicable]**

### Expected Runtime

If scripts are provided, runtime depends on the specific task:

* table generation: **[to be inserted]**
* figure generation: **[to be inserted]**

If no computational scripts are required for a given release, this repository should be interpreted primarily as a **transparent review archive** rather than a model-execution package.

## Citation

If you use this repository, please cite the associated archive and the review paper:

**[Full citation to be inserted]**

**Zenodo DOI:** **[to be inserted]**

## License

* **Code**: MIT License **[or to be confirmed]**
* **Audit tables and derived materials**: CC BY 4.0 **[or to be confirmed]**

## Contact

**Federico García Crespi**
Universidad Miguel Hernández
**[email to be inserted]**

## Acknowledgments

Bibliographic records were retrieved from **Scopus** and **Web of Science** in accordance with the access conditions and export limitations of those services.

Inter-rater agreement and methodological audit consistency checks were conducted within the review workflow described in the manuscript.

```
```
