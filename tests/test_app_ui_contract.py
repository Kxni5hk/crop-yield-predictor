"""Regression guards for CropCast's route-based professional workspace."""
from pathlib import Path
import unittest

from premium_ui import STYLES, hero_banner, section_heading
from model_research import evaluation_table, harvest_duration_table, model_a_status

ROOT = Path(__file__).resolve().parents[1]


class WebsiteUXRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "app.py").read_text(encoding="utf-8")
        cls.nav = (ROOT / "workspace_nav.py").read_text(encoding="utf-8")

    def test_no_false_model_missing_banner(self):
        self.assertNotIn("Add a model-release URL in Streamlit Cloud Secrets", self.app)
        self.assertNotIn("Website design is ready.", self.app)
        self.assertIn("verified Model B", self.app)
        self.assertIn("Your prediction will appear here", self.app)

    def test_route_based_navigation_and_model_a(self):
        self.assertIn("page = navigation()", self.app)
        self.assertNotIn("st.tabs(", self.app)
        for name in ("Overview", "Yield Predictor", "Crop Scenarios", "Model A Research",
                     "Batch Studio", "Weather Context", "Session History", "Research & About"):
            self.assertIn('if page == "' + name + '":', self.app)
            self.assertIn('"' + name + '"', self.nav)
        self.assertIn('home_launchers()', self.app)
        self.assertIn('st.radio(', self.nav)

    def test_live_model_features_preserved(self):
        self.assertIn("2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b", self.app)
        for marker in ("predict_csv_batch(", "fetch_city_weather(", "compare_supported_crops(",
                       "compare_one_feature_at_a_time(", "st.form_submit_button("):
            self.assertIn(marker, self.app)
        self.assertIn("model_a_status()", self.app)

    def test_model_a_evidence_is_honest(self):
        table = evaluation_table().set_index("Model")
        a = table.loc["A · Harvest-duration research"]
        b = table.loc["B · Early-stage scenarios"]
        self.assertGreater(a["R²"], b["R²"])
        self.assertLess(a["RMSE (t/ha)"], b["RMSE (t/ha)"])
        self.assertEqual(len(harvest_duration_table()), 6)
        self.assertIn("not deployed", model_a_status())
        self.assertIn("old", model_a_status().lower())

    def test_visual_system_is_accessible(self):
        self.assertIn("task-first compact dashboard", STYLES)
        self.assertIn("prefers-reduced-motion", STYLES)
        self.assertIn("max-width:750px", STYLES)
        self.assertIn("crop yield intelligence", hero_banner().lower())
        self.assertIn("Build a yield scenario", section_heading("", "Build a yield scenario", ""))


if __name__ == "__main__":
    unittest.main()
