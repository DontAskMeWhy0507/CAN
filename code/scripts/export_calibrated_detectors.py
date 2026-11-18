"""Recalibrate portable research bundles and verify against held-out predictions."""
from pathlib import Path
import sys
import json
import numpy as np

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src')]
from research_multisource.calibrated_detector import BenignCalibratedDetector
from can_research.io import json_write, sha256_file

OUT = CODE / 'results/benign_invariant_pipeline_2026-11-11'


def main():
    cal = json.loads((OUT / 'calibration_selection.json').read_text())
    summary = []
    for vehicle, name in enumerate(['Impala', 'Traverse', 'Silverado', 'Forester']):
        c = cal[str(vehicle)]
        folder = OUT / 'embeddings' / name
        with np.load(folder / (c['token'] + '.npz')) as data:
            indices = data['ix']
            normalization = np.searchsorted(indices, c['normalization'])
            threshold = np.searchsorted(indices, c['threshold'])
            arrays = {seed: (data[f'z{seed}'][normalization], data[f'z{seed}'][threshold]) for seed in (42, 43, 44)}
        for seed in (42, 43, 44):
            fit = OUT / 'fits' / name / f'seed_{seed}'
            for method in ['lr_targetq', 'diag_lr', 'white_lr', 'white_leace_lr', 'white_pca8_lr', 'white_inlp8_lr']:
                detector = BenignCalibratedDetector.from_fit(fit, method)
                assert detector.normalizer is None and detector.reference is None
                a, b = arrays[seed]
                detector.calibrate(a, b, [f'{c["token"]}:{i}' for i in c['normalization']],
                                   [f'{c["token"]}:{i}' for i in c['threshold']])
                prediction = next((fit / 'predictions' / method).glob('*.npz'))
                with np.load(folder / prediction.name) as data:
                    z = data[f'z{seed}'][:512]
                expected = np.load(prediction)
                actual = detector.predict(z)
                np.testing.assert_allclose(actual['score'], expected['score'][:len(z)], atol=1e-11, rtol=1e-11)
                np.testing.assert_array_equal(actual['risk'], expected['risk'][:len(z)])
                dest = OUT / 'deployable' / name / f'seed_{seed}'
                dest.mkdir(parents=True, exist_ok=True)
                artifact = dest / (method + '.joblib')
                detector.save(artifact)
                encoder = CODE / 'results/multisource_lovo_v2_2026-11-10/fits' / name / f'seed_{seed}' / 'structural/checkpoint.pt'
                summary.append(dict(vehicle=name, seed=seed, method=method,
                                    artifact=artifact.relative_to(OUT).as_posix(), sha256=sha256_file(artifact),
                                    encoder=str(encoder), encoder_sha256=sha256_file(encoder),
                                    checked_windows=len(z), max_score_error=float(np.max(np.abs(actual['score'] - expected['score'][:len(z)]))),
                                    calibration_capture=c['token']))
    json_write(OUT / 'deployment_export.json', dict(status='PASS', bundles=summary,
        input='N x 64 embedding from the matching frozen Structural encoder and W64 feature extractor',
        use='Recalibrate on a new confirmed-benign capture before use on a different vehicle.',
        claim='Research artifact; per-vehicle calibration is not statistical vehicle independence.'))
    print(f'PASS: {len(summary)} deployment bundles reproduce research predictions')


if __name__ == '__main__':
    main()
