"""Regression guards for the documented CropCast first-screen issues."""
from pathlib import Path
import unittest
from premium_ui import STYLES, hero_banner, section_heading

ROOT = Path(__file__).resolve().parents[1]


class WebsiteUXRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "app.py").read_text(encoding="utf-8")

    def test_no_false_model_missing_banner(self):
        self.assertNotIn("Add a model-release URL in Streamlit Cloud Secrets", self.app)
        self.assertNotIn("Website design is ready.", self.app)
        self.assertIn("verified Model B", self.app)
        self.assertIn("Your prediction will appear here", self.app)

    def test_prediction_workspace_is_above_supporting_dashboards(self):
        self.assertLess(
            self.app.index("predict_tab, compare_tab, bulk_tab"),
            self.app.index("metric_cards(), unsafe_allow_html=True"),
        )
        self.assertLess(self.app.index("with predict_tab:"), self.app.index("with performance_tab:"))
        self.assertIn('st.markdown(workflow_cards(), unsafe_allow_html=True)', self.app)

    def test_reference_model_and_functionality_retained(self):
        self.assertIn("2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b", self.app)
        for feature in ("with predict_tab:", "with compare_tab:", "with bulk_tab:",
                        "with weather_tab:", "with history_tab:", "with performance_tab:"):
            self.assertIn(feature, self.app)

    def test_compact_accessible_visual_system(self):
        self.assertIn("task-first compact dashboard", STYLES)
        self.assertIn("prefers-reduced-motion", STYLES)
        self.assertIn("max-width:750px", STYLES)
        self.assertIn("crop yield intelligence", hero_banner().lower())
        self.assertIn("Build a yield scenario", section_heading("", "Build a yield scenario", ""))
        
if __name__ == "__main__":
    unittest.main()
