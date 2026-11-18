"""Deploy a source-fitted head using confirmed-benign calibration of a new vehicle.

Vehicle identity is not an inference input. Calibration state is still specific
to the new vehicle; this interface does not assert statistical independence.
The encoder and W64 content-feature extraction must match the saved protocol.
"""
from pathlib import Path
import hashlib
import json
import joblib
import numpy as np
from . import invariant_pipeline as ip


class BenignCalibratedDetector:
    def __init__(self, method, head, projection=None):
        allowed = {'lr_targetq', 'diag_lr', 'white_lr', 'white_leace_lr', 'white_pca8_lr', 'white_inlp8_lr'}
        if method not in allowed:
            raise ValueError('Expected a source-fitted LR pipeline')
        self.method, self.head, self.projection = method, head, projection
        self.normalizer = None
        self.reference = None
        self.calibration = None

    @classmethod
    def from_fit(cls, folder, method='white_inlp8_lr'):
        """Load only source-fitted head/projection; discard every old normalizer/reference."""
        folder = Path(folder)
        metadata = json.loads((folder / 'fitted.json').read_text(encoding='utf-8'))
        path = folder / 'states.joblib'
        if hashlib.sha256(path.read_bytes()).hexdigest() != metadata['sha256']:
            raise ValueError('Fitted-state checksum mismatch')
        state = joblib.load(path)[method]
        return cls(method, state['head'], state['projection'])

    @staticmethod
    def _array(x):
        x = np.asarray(x, dtype=np.float64)
        if x.ndim != 2 or x.shape[1] != 64 or not len(x) or not np.isfinite(x).all():
            raise ValueError('Expected a nonempty finite N x 64 encoder embedding array')
        return x

    def _transform(self, x):
        x = self._array(x)
        if self.normalizer is not None:
            x = ip.normalize(x, self.normalizer)
        return ip.project(x, self.projection) if self.projection is not None else x

    def calibrate(self, normalization_z, threshold_z, normalization_ids, threshold_ids, alpha=.01):
        """Caller supplies confirmed-benign, nonoverlapping W64 windows only.

        IDs must identify windows globally (e.g., capture SHA256 + window index).
        The entire capture must be withheld from any subsequent evaluation.
        Exactly 1000 + 1000 windows matches the frozen research protocol.
        """
        a, b = self._array(normalization_z), self._array(threshold_z)
        if len(a) != 1000 or len(b) != 1000:
            raise ValueError('Frozen protocol requires 1000 normalization and 1000 threshold windows')
        left, right = list(normalization_ids), list(threshold_ids)
        if len(left) != len(a) or len(right) != len(b) or len(set(left)) != len(left) or len(set(right)) != len(right):
            raise ValueError('Calibration window IDs must be unique and aligned')
        if set(left) & set(right):
            raise ValueError('Normalization and threshold windows overlap')
        if alpha not in (.01, .001):
            raise ValueError('Frozen protocol supports alpha 0.01 or 0.001')
        mode = 'diag' if self.method == 'diag_lr' else 'white' if self.method.startswith('white') else None
        self.normalizer = ip.benign_normalizer(a, mode) if mode else None
        self.reference = ip.task_score(self._transform(b), self.head)
        self.threshold = ip.benign_threshold(self.reference, alpha)
        self.alpha = alpha
        self.calibration = dict(normalization_ids=left, threshold_ids=right, alpha=alpha,
                                normalization_sha256=hashlib.sha256(a.tobytes()).hexdigest(),
                                threshold_sha256=hashlib.sha256(b.tobytes()).hexdigest())
        return self

    def predict(self, embeddings):
        if self.reference is None:
            raise RuntimeError('Calibrate on a separate confirmed-benign capture first')
        z = self._transform(embeddings)
        score = ip.task_score(z, self.head)
        risk = ip.calibrated_risk(score, self.reference)
        return dict(score=score, risk=risk, attack=score >= self.threshold, embedding=z)

    def save(self, path):
        if self.reference is None:
            raise RuntimeError('Cannot save an uncalibrated deployment bundle')
        joblib.dump(self, path)
