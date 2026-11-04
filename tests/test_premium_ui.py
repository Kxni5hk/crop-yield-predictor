"""Contract tests for premium visual system; no browser or network required."""
import unittest
from premium_ui import (
    STYLES, brand_banner, hero_banner, metric_cards,
    workflow_cards, section_heading, result_card, footer,
)


class PremiumUITests(unittest.TestCase):
    def test_static_sections(self):
        for html in (brand_banner(), hero_banner(), metric_cards(), workflow_cards(), footer()):
            self.assertTrue(html.strip())
            self.assertNotIn("<script", html.lower())
        self.assertIn("MODEL B", hero_banner())
        self.assertIn("0.9031", metric_cards())
        self.assertIn("@media(max-width:750px)", STYLES)
        self.assertIn("prefers-reduced-motion", STYLES)

    def test_dynamic_content_is_escaped(self):
        heading = section_heading("<script>", "Title", "description & details")
        self.assertIn("&lt;script&gt;", heading)
        self.assertNotIn("<script>", heading)
        card = result_card("<img src=x>", "North<script>", 6.16)
        self.assertNotIn("<img", card)
        self.assertNotIn("North<script>", card)
        self.assertIn("6.16", card)
        self.assertIn("6,160", card)

    def test_layout_has_production_disclosure(self):
        self.assertIn("No independent farm validation", footer())
        self.assertIn("not field-validated", result_card("Wheat", "North", 6.16))

if __name__ == "__main__":
    unittest.main()
