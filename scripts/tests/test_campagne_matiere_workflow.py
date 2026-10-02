"""Ordre des préconditions sur un runner sans inventaire conservé."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CampaignWorkflowTests(unittest.TestCase):
    def test_inventory_is_built_before_verification(self):
        workflow = (ROOT / '.github/workflows/campagne-matiere.yml').read_text(encoding='utf-8')
        commands = [
            'python telecharger_toutes_sources.py',
            'python ne_garder_que_l_exploitable.py --appliquer',
            'python reconstituer_provenance.py',
            'python verifier_sources.py',
            'python run_all.py --sans-verification',
        ]
        positions = [workflow.index(command) for command in commands]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('../DONNEES_MATIERE_ORI-C/PROVENANCE.json', workflow)


if __name__ == '__main__':
    unittest.main()
