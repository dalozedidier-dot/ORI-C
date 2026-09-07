import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def module(relative):
    spec = importlib.util.spec_from_file_location('subject', ROOT / relative)
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    return subject


class AuthorityGuards(unittest.TestCase):
    def test_solar_gates_respond_to_changed_evidence(self):
        audit = module('scripts/auditer_invariant_hmr_solaire.py')
        history, intervention = audit.load(audit.H_SOURCE), audit.load(audit.M_SOURCE)
        for block in history.values():
            for row in block['detail']:
                row['passed'] = True
        intervention['matching']['same_future_forcing'] = False
        with patch.object(audit, 'load', side_effect=[history, intervention]):
            result = audit.build()
        self.assertTrue(result['filters']['H_given_rich_X']['equal_complexity_comparison_passes'])
        self.assertIsNone(result['filters']['H_given_rich_X']['passes'])
        self.assertFalse(result['filters']['m_to_R']['passes_model_level'])
        self.assertFalse(result['section_XIV_credit'])

    def test_opening_refused_even_with_valid_committed_hash(self):
        guard = module('02_branche_systeme_solaire/paleo_history_03_age_ensemble/verifier_avant_ouverture.py')
        with patch.object(guard, 'verify_committed_freeze', return_value='valid'), \
                patch('sys.argv', ['guard', 'never-open-this-file']), \
                patch.object(Path, 'open', side_effect=AssertionError('data access')):
            self.assertEqual(guard.main(), 2)

    def test_modified_freeze_is_rejected(self):
        guard = module('02_branche_systeme_solaire/paleo_history_03_age_ensemble/verifier_avant_ouverture.py')
        with patch.object(guard, 'committed_bytes', return_value=b'other content'):
            with self.assertRaises(RuntimeError):
                guard.verify_committed_freeze()
