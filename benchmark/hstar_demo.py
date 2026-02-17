#!/usr/bin/env python3
"""
H* (Operational Predictability Limit) benchmark demonstration.
Implements synthetic PM10 forecasting comparison: static vs. rolling-origin.

Generates Figure 4 from paper (Section 3.5, Supplementary Material C).

Usage:
    python hstar_demo.py
    
Output:
    - hstar_results.csv (skill scores by horizon and protocol)
    - figure4_hstar_comparison.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


def generate_synthetic_pm10(n_hours=17520, seed=42):
    """
    Generate synthetic hourly PM10 series matching paper description:
    - Daily + weekly seasonal cycles
    - Positive trend
    - Moderate noise (σ=5 µg/m³)
    
    Args:
        n_hours: Length of series (default 17520 = 2 years)
        seed: Random seed for reproducibility
    
    Returns:
        pd.Series with DatetimeIndex
    """
    np.random.seed(seed)
    t = np.arange(n_hours)
    
    # Seasonal components
    daily = 8 * np.sin(2 * np.pi * t / 24)              # Diurnal cycle
    weekly = 4 * np.sin(2 * np.pi * t / (24*7))         # Weekly cycle
    trend = 0.002 * t                                    # Positive trend
    noise = 5 * np.random.randn(n_hours)                # σ=5 µg/m³
    
    # Baseline + components
    pm10 = 25 + daily + weekly + trend + noise
    pm10 = np.maximum(pm10, 0)  # Non-negative constraint
    
    # Create series with hourly index
    start_date = '2020-01-01'
    index = pd.date_range(start=start_date, periods=n_hours, freq='h')
    
    return pd.Series(pm10, index=index, name='PM10')


def static_leaky_protocol(y, train_frac=0.75, horizons=[1,6,12,24,48,72], p=24):
    """
    Static validation with GLOBAL preprocessing (data leakage).
    
    Computes 24-hour rolling mean over ENTIRE series before split.
    This encodes future information into training features.
    """
    n = len(y)
    split_idx = int(n * train_frac)
    
    # LEAKAGE: compute rolling mean on full series
    y_rolled = y.rolling(window=24, min_periods=1).mean()
    
    # Split after global feature construction
    y_train = y_rolled.iloc[:split_idx].values
    y_test = y.iloc[split_idx:].values
    
    # Fit scaler on train
    scaler = StandardScaler()
    y_train_scaled = scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
    
    # Create lagged features
    X_train = np.column_stack([
        np.roll(y_train_scaled, i) for i in range(1, p+1)
    ])[p:]
    y_train_target = y_train_scaled[p:]
    
    # Train model
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train_target)
    
    # Evaluate on test
    results = {}
    for h in horizons:
        if split_idx + p + h >= n:
            continue
        
        # Forecast at horizon h
        X_test_h = scaler.transform(
            y_rolled.iloc[split_idx:split_idx+p].values.reshape(-1, 1)
        ).flatten()
        X_test_h = X_test_h[::-1].reshape(1, -1)  # Reverse for lag structure
        
        y_pred_scaled = model.predict(X_test_h)[0]
        y_pred = scaler.inverse_transform([[y_pred_scaled]])[0, 0]
        
        y_true = y_test[h-1]
        y_persist = y.iloc[split_idx-1]  # Persistence baseline
        
        # Errors
        err_model = (y_pred - y_true)**2
        err_persist = (y_persist - y_true)**2
        
        # Skill score
        skill = 1 - (err_model / err_persist) if err_persist > 0 else 0
        
        results[h] = {
            'rmse': np.sqrt(err_model),
            'skill': skill
        }
    
    return results


def rolling_origin_causal_protocol(y, horizons=[1,6,12,24,48,72], 
                                     W_min=365*24, step=7*24, p=24):
    """
    Rolling-origin validation with CAUSAL preprocessing (leakage-free).
    
    Computes rolling mean using only data available up to each forecast origin.
    Simulates operational deployment.
    """
    results = {h: {'rmse': [], 'skill': []} for h in horizons}
    
    n = len(y)
    origins = range(W_min, n - max(horizons), step)
    
    for origin in origins:
        # Training data: strictly past
        y_train = y.iloc[:origin]
        
        # CAUSAL: compute rolling mean only on training data
        y_rolled_train = y_train.rolling(window=24, min_periods=1).mean()
        
        # Fit scaler on train
        scaler = StandardScaler()
        y_train_scaled = scaler.fit_transform(
            y_rolled_train.values.reshape(-1, 1)
        ).flatten()
        
        # Lagged features
        X_train = np.column_stack([
            np.roll(y_train_scaled, i) for i in range(1, p+1)
        ])[p:]
        y_train_target = y_train_scaled[p:]
        
        # Train model
        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train_target)
        
        # Forecast at each horizon
        for h in horizons:
            if origin + h >= n:
                continue
            
            # Use causal rolling mean up to origin
            X_test_h = scaler.transform(
                y_rolled_train.iloc[-p:].values.reshape(-1, 1)
            ).flatten()
            X_test_h = X_test_h[::-1].reshape(1, -1)
            
            y_pred_scaled = model.predict(X_test_h)[0]
            y_pred = scaler.inverse_transform([[y_pred_scaled]])[0, 0]
            
            y_true = y.iloc[origin + h - 1]
            y_persist = y.iloc[origin - 1]
            
            # Errors
            err_model = (y_pred - y_true)**2
            err_persist = (y_persist - y_true)**2
            
            # Skill score
            skill = 1 - (err_model / err_persist) if err_persist > 0 else 0
            
            results[h]['rmse'].append(np.sqrt(err_model))
            results[h]['skill'].append(skill)
    
    # Aggregate across origins
    summary = {}
    for h in horizons:
        if len(results[h]['rmse']) > 0:
            summary[h] = {
                'rmse': np.mean(results[h]['rmse']),
                'skill': np.mean(results[h]['skill'])
            }
    
    return summary


def compute_hstar(results, threshold=0.0):
    """Compute H* = max horizon with skill > threshold."""
    horizons = sorted(results.keys())
    for h in reversed(horizons):
        if results[h]['skill'] > threshold:
            return h
    return 0


def main():
    print("Generating synthetic PM10 data (n=17,520 hours)...")
    y = generate_synthetic_pm10()
    
    horizons = [1, 6, 12, 24, 48, 72]
    
    print("\nRunning static (leaky) protocol...")
    static_results = static_leaky_protocol(y, horizons=horizons)
    
    print("Running rolling-origin (causal) protocol...")
    rolling_results = rolling_origin_causal_protocol(y, horizons=horizons)
    
    # Compute H*
    hstar_static = compute_hstar(static_results)
    hstar_rolling = compute_hstar(rolling_results)
    
    print(f"\n{'='*60}")
    print(f"H* COMPARISON")
    print(f"{'='*60}")
    print(f"Static (leaky):           H* = {hstar_static}h")
    print(f"Rolling-origin (causal):  H* = {hstar_rolling}h")
    print(f"{'='*60}\n")
    
    # Tabulate results
    df_results = pd.DataFrame({
        'horizon_h': horizons,
        'static_skill': [static_results.get(h, {}).get('skill', np.nan) for h in horizons],
        'rolling_skill': [rolling_results.get(h, {}).get('skill', np.nan) for h in horizons],
        'static_rmse': [static_results.get(h, {}).get('rmse', np.nan) for h in horizons],
        'rolling_rmse': [rolling_results.get(h, {}).get('rmse', np.nan) for h in horizons],
    })
    df_results['inflation'] = (df_results['static_skill'] / df_results['rolling_skill'] - 1) * 100
    
    print(df_results.to_string(index=False))
    df_results.to_csv('hstar_results.csv', index=False)
    print("\n✓ Saved results to hstar_results.csv")
    
    # Generate Figure 4
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Panel (a): RMSE
    ax1.plot(horizons, df_results['static_rmse'], 'o-', label='Static (leaky)', color='C0')
    ax1.plot(horizons, df_results['rolling_rmse'], 's--', label='Rolling-origin (causal)', color='C1')
    ax1.set_xlabel('Forecast horizon (hours)')
    ax1.set_ylabel('RMSE (µg/m³)')
    ax1.set_title('(a) Forecast Error')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Panel (b): Skill score
    ax2.plot(horizons, df_results['static_skill'], 'o-', label='Static (leaky)', color='C0')
    ax2.plot(horizons, df_results['rolling_skill'], 's--', label='Rolling-origin (causal)', color='C1')
    ax2.axhline(0, color='k', linestyle=':', linewidth=1, label='H* threshold')
    ax2.set_xlabel('Forecast horizon (hours)')
    ax2.set_ylabel('Skill score vs. persistence')
    ax2.set_title('(b) Skill Score')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figure4_hstar_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved figure to figure4_hstar_comparison.png\n")


if __name__ == '__main__':
    main()
