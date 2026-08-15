import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PRED = HERE / 'PREDICTIONS_PROSPECTIVES'
REG = PRED / 'ENREGISTREMENTS_PUBLICS'


def test_tous_les_paquets_osf_conservent_empreinte_scientifique():
    index = json.loads((REG / 'INDEX.json').read_text(encoding='utf-8'))
    expected_ids = {path.stem for path in PRED.glob('PRED-*.json')}
    assert {row['id'] for row in index['registrations']} == expected_ids
    for row in index['registrations']:
        identifier = row['id']
        registration = json.loads((REG / f'{identifier}.registration.json').read_text(encoding='utf-8'))
        source = PRED / f'{identifier}.json'
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert digest == registration['source_sha256']
        assert registration['status'] in {'package_ready_external_account_required', 'publicly_registered'}
        if registration['status'] == 'publicly_registered':
            assert registration.get('public_url')
            assert registration.get('registered_at')


def test_prediction_audit_exige_enregistrement_public():
    audit = json.loads((HERE / 'resultats/PREDICTIONS_HORS_ECHANTILLON_AUDIT.json').read_text(encoding='utf-8'))
    for row in audit['predictions']:
        if row['registration_status'] != 'publicly_registered':
            assert row['public_preregistration_present'] is False
