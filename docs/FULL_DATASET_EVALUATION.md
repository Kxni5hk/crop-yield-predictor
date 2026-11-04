# CropCast AI — Full dataset Model A/B comparison

## Dataset

Original CSV had **1,000,000 records** and 10 columns. After excluding 231 negative-yield rows, 999,769 records remained. The same random_state=42 80/20 split was used for both models: 799,815 training and 199,954 held-out test records. Missing values: zero; duplicate rows: zero.

## Experiment parameters

RandomForestRegressor with 100 trees, maximum depth 20, min_samples_leaf 2, maximum bootstrap fraction 0.25 per tree, and n_jobs=4. This **differs from the earlier 50k-row experiment** using the default bootstrap size per tree, so differences between experiments cannot be attributed solely to data volume.

| Model | Input features | RMSE (t/ha) ↓ | MAE (t/ha) ↓ | R² ↑ |
|---|---:|---:|---:|---:|
| A · includes Days_to_Harvest | 9 | 0.5046694515 | 0.4025470269 | 0.9113472304 |
| B · omits Days_to_Harvest | 8 | 0.5053479897 | 0.4031628040 | 0.9111086793 |

All results are from the separate full-dataset research experiment, **not the original currently deployed Model B release**. The deployment uses an older eight-input Model B trained with the original 50,000-row experiment.

### Days_to_Harvest descriptive analysis

| Crop | Records | P10 days | Median days | P90 days |
|---|---:|---:|---:|---:|
| Barley | 166727 | 69 | 104 | 140 |
| Cotton | 166548 | 69 | 105 | 141 |
| Maize | 166785 | 69 | 105 | 141 |
| Rice | 166754 | 69 | 104 | 141 |
| Soybean | 166315 | 68 | 105 | 140 |
| Wheat | 166640 | 69 | 105 | 140 |

The days table reports dataset distributions and is **not** a recommended farming schedule.

The full-data Model A research file was separately trained with scikit-learn 1.8.0. Its SHA-256 is `99f54e989ee7503928fd0666385a9a9c214e03dc34cecd58545be7ee43bd7535`; file size 223,200,267 bytes. It is **not deployed on Render**, whose current production environment uses scikit-learn 1.6.1 and approximately 512 MiB RAM. Compatibility and memory use require independent checks before any deployment.

No farm/year generalization test was performed; agricultural provenance, future-season accuracy and real-field suitability are not established. Crop-yield predictions remain educational prototype estimates.
