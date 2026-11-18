"""Compatibility entry point; shared extraction is in features.py."""
from .features import extract_windows
from .models import CANTransformer
WINDOW_SIZE = 64
STRUCTURAL_FEATURE_DIM = 32

def extract_structural_windows(df, window_size=64, flatten=False):
    x, y = extract_windows(df, window_size, representation="structural")
    return (x.reshape(len(x), window_size * 32) if flatten else x), y
