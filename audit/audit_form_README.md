# Audit Form Template

The audit form is a 3-sheet Excel workbook (`.xlsx`) used for structured full-text assessment of validation protocols (Section 2.4).

## Sheet 1: Audit Form (Empty Template)

Columns:
- `paper_id`: Study identifier (e.g., C1, M1, D1)
- `doi`: Digital object identifier
- `first_author`: First author surname
- `year`: Publication year
- `journal`: Journal name
- `architecture`: Primary forecasting architecture
- `horizon_declared`: Reported maximum forecast horizon
- `validation_protocol`: Categorical (Random split / Static chronological / Rolling-origin global / Rolling-origin train-only / Not documented)
- `preprocessing_scope`: Categorical (Explicit train-only / Ambiguous / Global or test-inclusive / Not documented)
- `dynamic_updating`: Binary (Yes / No / Not documented)
- `leakage_risk_score`: Integer (0–3)
- `baseline_comparison`: Binary (Persistence baseline reported: Yes/No)
- `skill_score_reported`: Binary (Skill score vs. baseline: Yes/No)
- `notes`: Free text for ambiguous cases or additional context

## Sheet 2: Completed Example (n=15)

Same structure as Sheet 1, pre-filled with classifications for all 15 audited papers from Table 3 (Appendix B).

Example row:
```
C1 | 10.1016/j.atmosenv.2005.01.050 | Hooyberghs | 2005 | Atmospheric Environment | ANN | 1-day ahead | Static chronological | Ambiguous | No | 2 | No | No | "Preprocessing described as 'data normalization' without temporal scope"
```

## Sheet 3: Scoring Rubric Reference

### Validation Protocol Categories
1. **Random split**: k-fold CV with random shuffling (violates temporal ordering)
2. **Static chronological**: Single train/test partition, no iterative updating
3. **Rolling-origin global**: Sequential retraining with global preprocessing
4. **Rolling-origin train-only**: Sequential retraining with causal preprocessing (rigorous)
5. **Not documented**: Insufficient information to classify

### Leakage Risk Score (LRS)

Score = sum of:
- Random or inappropriate partitioning: +1
- Global preprocessing / normalization: +1  
- No dynamic model updating: +1

Ranges:
- **0** (no risk): Rolling-origin + train-only preprocessing
- **1** (low): Static split + explicit train-only preprocessing
- **2** (moderate): Static split + ambiguous or global preprocessing
- **3** (severe): Random split + global preprocessing

### Inter-rater Protocol

For inter-rater reliability (Section 2.4.1):
1. Randomly select 5 papers spanning all eras
2. Second rater independently completes audit form for those 5
3. Compare classifications across all categorical fields
4. Compute Cohen's κ for agreement
5. Resolve discrepancies via consensus discussion with reference to source text

## Creating the Excel File

To generate `audit_form_template.xlsx`:

```python
import pandas as pd

# Sheet 1: Empty template
template = pd.DataFrame(columns=[
    'paper_id', 'doi', 'first_author', 'year', 'journal', 
    'architecture', 'horizon_declared', 'validation_protocol',
    'preprocessing_scope', 'dynamic_updating', 'leakage_risk_score',
    'baseline_comparison', 'skill_score_reported', 'notes'
])

# Sheet 2: Load from audit_sample_metadata.csv and expand
completed = pd.read_csv('../data/audit_sample_metadata.csv')
# ... add classification columns from full audit results

# Sheet 3: Rubric text (formatted table)
rubric = pd.DataFrame({
    'Category': ['Validation Protocol', 'Preprocessing Scope', 'LRS'],
    'Options': [
        'Random / Static / Rolling-global / Rolling-train / Not doc',
        'Explicit train / Ambiguous / Global / Not doc',
        '0 (none) / 1 (low) / 2 (moderate) / 3 (severe)'
    ]
})

# Write to Excel
with pd.ExcelWriter('audit_form_template.xlsx', engine='openpyxl') as writer:
    template.to_excel(writer, sheet_name='Audit Form', index=False)
    completed.to_excel(writer, sheet_name='Completed Sample', index=False)
    rubric.to_excel(writer, sheet_name='Rubric Reference', index=False)
```

This Excel file is referenced in paper Section 2.4 and Supplementary Material B.
