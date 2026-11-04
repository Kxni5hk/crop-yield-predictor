# CropCast AI — one-million-row A/B evaluation (4 Nov 2026)

The full `crop_yield.csv` in the owner's connected Drive project folder contains **1,000,000 observations** and 10 columns. The original Colab notebook loaded **336,776 rows**, then sampled 50,000 for its first comparison. This experiment reads the entire available CSV, without the 50,000-row sampling step.

## Dataset quality and split
- Original rows: **1,000,000**
- Negative yield rows removed: **231**
- Missing values: **0** across the original CSV
- Duplicate complete rows: **0**
- Valid rows: **999,769**
- Training rows: **799,815**
- Held-out test rows: **199,954**
- Same 80/20 split for A and B; random_state=42

## Training configuration
Both: RandomForestRegressor, 100 estimators, max_depth=20, min_samples_leaf=2, random_state=42, **max_samples=0.25**, n_jobs=4. Numerical fields use median imputation; categorical/boolean use most-frequent imputation and OneHotEncoder. Training was run with Python and scikit-learn 1.8.0.

**Methodology limitation:** The original 50k notebook used default `max_samples=None`. This larger experiment uses a 25% bootstrap draw per tree to bound compute. Changes in metric values therefore cannot be attributed entirely to dataset size.

## Results: same 199,954-row holdout

| Model | Features | RMSE (t/ha) ↓ | MAE (t/ha) ↓ | R² ↑ |
|---|---:|---:|---:|---:|
| A — with Days_to_Harvest | 9 | 0.504669 | 0.402547 | **0.911347** |
| B — without Days_to_Harvest | 8 | 0.505348 | 0.403163 | 0.911109 |

Model A has a **small** numerical edge: ΔR² = 0.000239, ΔRMSE = 0.000679 t/ha, ΔMAE = 0.000616 t/ha.

## Comparison with original limited experiment

Original 50k-row sample (40k training; 10k test): Model A R²=0.9039 RMSE=0.5211; Model B R²=0.9031 RMSE=0.5233. Those original scores come from **different experimental conditions** and are not controlled head-to-head evidence that dataset size alone caused improvement.

## Deployment choice

The public website currently serves the **earlier 50k-trained Model B**, whose exact artifact hash is checked before joblib loading. These full-data scores are from new **experimental models**, not that deployed artifact.

Model A requires `Days_to_Harvest`, which may be unknown at the time of early yield planning. It can be useful for retrospective or planned-harvest-day scenarios, but it should not be presented as an input known in advance without caveat. Model B avoids that requirement. Neither candidate is externally validated for future seasons or independent farms; the CSV has no farm/year identifiers for that test. Dataset provenance and real-world representativeness are unverified. A model trained on ~800k rows may also exceed the existing 512MiB Render Free memory limit: don't hot-swap it into production without a resource profile, model file integrity check and live stability verification.

Experiment artifacts: full comparison CSV, crop-wise results, executable script, and a standalone Colab notebook; the original training notebook was not overwritten.
