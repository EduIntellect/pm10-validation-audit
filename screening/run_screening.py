#!/usr/bin/env python3
"""
Lexical screening pipeline for PM10 forecasting literature audit.
Implements regex-based classification of multi-step task declarations
and rigorous temporal validation mentions (Section 2.2).

Usage:
    python run_screening.py
    
Output:
    - screening_results.csv (n=2,425 classifications)
    - prevalence_summary.txt (corpus-level statistics with Wilson CIs)
"""

import re
import pandas as pd
import numpy as np
from scipy import stats

# Regex patterns from Section 2.2 and Supplementary Material A
TASK_PATTERNS = [
    r'multi[-\s]?step',
    r'[\d]+[-\s]?(hour|day|step)[-\s]?ahead',
    r'extended[-\s]?horizon',
    r'[\d]+h\s+forecasting'
]

VALIDATION_PATTERNS = [
    r'rolling[-\s]?origin',
    r'walk[-\s]?forward',
    r'expanding[-\s]?window',
    r'time[-\s]?series[-\s]?cross[-\s]?validation',
    r'sequential[-\s]?retraining'
]


def load_corpus():
    """
    Load Scopus corpus abstracts.
    
    In production: replace with actual Scopus export CSV.
    For demonstration: generates synthetic corpus matching paper statistics.
    """
    print("Loading corpus (n=2,425)...")
    
    # Placeholder: actual corpus would be loaded from data/scopus_export.csv
    # For demo, generate synthetic data matching reported prevalences
    np.random.seed(42)
    n = 2425
    
    # 2.2% multi-step, 0.08% validation (from paper)
    n_multistep = int(n * 0.022)  # 53 papers
    n_validation = int(n * 0.0008)  # 2 papers
    
    corpus = pd.DataFrame({
        'eid': [f'2-s2.0-{85000000000 + i}' for i in range(n)],
        'title': [f'Study {i}' for i in range(n)],
        'abstract': [''] * n,
        'year': np.random.randint(2000, 2027, n)
    })
    
    # Mark synthetic multi-step papers
    multistep_idx = np.random.choice(n, n_multistep, replace=False)
    corpus.loc[multistep_idx, 'abstract'] = 'multi-step forecasting PM10 24-hour ahead'
    
    # Mark synthetic validation papers (subset of multistep)
    validation_idx = np.random.choice(multistep_idx, n_validation, replace=False)
    corpus.loc[validation_idx, 'abstract'] = 'walk-forward validation PM10 forecasting'
    
    print(f"  Loaded {len(corpus)} records")
    return corpus


def classify_abstract(text):
    """
    Binary classification: task declaration (yes/no), validation mention (yes/no).
    
    Args:
        text: Abstract text (title + abstract + keywords concatenated)
    
    Returns:
        (has_task, has_validation): tuple of booleans
    """
    text_lower = text.lower()
    
    # Task indicators
    has_task = any(re.search(pattern, text_lower, re.IGNORECASE) 
                   for pattern in TASK_PATTERNS)
    
    # Validation indicators
    has_validation = any(re.search(pattern, text_lower, re.IGNORECASE) 
                         for pattern in VALIDATION_PATTERNS)
    
    return has_task, has_validation


def wilson_ci(p, n, alpha=0.05):
    """
    Wilson score confidence interval for binomial proportion.
    
    Recommended for small proportions (Brown et al. 2001).
    """
    z = stats.norm.ppf(1 - alpha/2)
    denominator = 1 + z**2/n
    centre = (p + z**2/(2*n)) / denominator
    spread = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denominator
    return centre - spread, centre + spread


def main():
    # Load corpus
    corpus = load_corpus()
    
    # Run classification
    print("\nRunning lexical screening...")
    results = corpus['abstract'].apply(classify_abstract)
    corpus['task_declared'] = results.apply(lambda x: x[0])
    corpus['validation_mentioned'] = results.apply(lambda x: x[1])
    
    # Compute prevalences
    n_total = len(corpus)
    n_task = corpus['task_declared'].sum()
    n_validation = corpus['validation_mentioned'].sum()
    
    p_task = n_task / n_total
    p_validation = n_validation / n_total
    
    # Wilson CIs
    ci_task = wilson_ci(p_task, n_total)
    ci_validation = wilson_ci(p_validation, n_total)
    
    # Print summary
    print("\n" + "="*60)
    print("CORPUS-LEVEL PREVALENCE (n={:,})".format(n_total))
    print("="*60)
    print(f"\nMulti-step declarations:    {n_task:4d} ({p_task*100:.2f}%)")
    print(f"  95% CI (Wilson):          [{ci_task[0]*100:.2f}% – {ci_task[1]*100:.2f}%]")
    print(f"\nRigorous validation:        {n_validation:4d} ({p_validation*100:.2f}%)")
    print(f"  95% CI (Wilson):          [{ci_validation[0]*100:.2f}% – {ci_validation[1]*100:.2f}%]")
    print(f"\nRatio (task : validation):  {n_task}:{n_validation} ≈ {n_task/max(n_validation,1):.0f}:1")
    print("="*60)
    
    # Save results
    output_file = 'screening_results.csv'
    corpus[['eid', 'year', 'task_declared', 'validation_mentioned']].to_csv(
        output_file, index=False
    )
    print(f"\n✓ Saved classifications to {output_file}")
    
    # Save summary
    summary_file = 'prevalence_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("Lexical Screening Results\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total corpus:              {n_total:,}\n")
        f.write(f"Multi-step declarations:   {n_task} ({p_task*100:.2f}%)\n")
        f.write(f"  Wilson 95% CI:           [{ci_task[0]*100:.2f}%, {ci_task[1]*100:.2f}%]\n")
        f.write(f"Validation mentions:       {n_validation} ({p_validation*100:.2f}%)\n")
        f.write(f"  Wilson 95% CI:           [{ci_validation[0]*100:.2f}%, {ci_validation[1]*100:.2f}%]\n")
        f.write(f"Task:Validation ratio:     {n_task}:{n_validation}\n")
    
    print(f"✓ Saved summary to {summary_file}\n")


if __name__ == '__main__':
    main()
