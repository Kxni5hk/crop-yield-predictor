"""Tests for bounded CSV predictions; no network or pickle loading."""
import unittest
from io import StringIO
import pandas as pd
from batch_tools import MAX_CSV_ROWS, csv_template, read_validated_csv, predict_csv_batch

class MockModel:
    def predict(self, rows):
        return (3.0 + rows["Rainfall_mm"].to_numpy(dtype=float) * .005
                + rows["Irrigation_Used"].to_numpy(dtype=float) * .2)

class BatchPredictionTests(unittest.TestCase):
    def test_template_yields_real_model_predictions(self):
        outputs, errors = predict_csv_batch(MockModel(), csv_template())
        self.assertEqual(len(outputs), 2)
        self.assertTrue(errors.empty)
        self.assertEqual(outputs["CSV line"].tolist(), [2, 3])
        self.assertAlmostEqual(outputs.loc[0, "Predicted yield (t/ha)"], 5.95)
        self.assertAlmostEqual(outputs.loc[0, "Predicted yield (kg/ha)"], 5950.)

    def test_invalid_rows_reported(self):
        frame = pd.read_csv(StringIO(csv_template().decode()))
        frame.loc[1, "Crop"] = "UnknownCrop"
        outputs, errors = predict_csv_batch(MockModel(), frame.to_csv(index=False).encode())
        self.assertEqual(len(outputs), 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors.iloc[0]["CSV line"], 3)

    def test_rejects_oversized_or_invalid_files(self):
        with self.assertRaises(ValueError): read_validated_csv(b"x" * (128*1024+1))
        with self.assertRaises(ValueError): read_validated_csv(b"")
        frame = pd.read_csv(StringIO(csv_template().decode()))
        too_many = pd.concat([frame] * (MAX_CSV_ROWS // 2 + 1), ignore_index=True)
        with self.assertRaises(ValueError):
            read_validated_csv(too_many.to_csv(index=False).encode())

    def test_no_and_false_booleans(self):
        frame = pd.read_csv(StringIO(csv_template().decode()))
        frame.loc[0, "Fertilizer_Used"] = "No"
        frame.loc[0, "Irrigation_Used"] = "False"
        accepted, rows, errors = read_validated_csv(frame.to_csv(index=False).encode())
        self.assertTrue(errors.empty)
        self.assertEqual(bool(accepted.loc[0, "Fertilizer_Used"]), False)
        self.assertEqual(bool(accepted.loc[0, "Irrigation_Used"]), False)

if __name__ == "__main__":
    unittest.main()
