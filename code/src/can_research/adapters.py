"""Strict adapters shared with the audited runner."""
from .io import canonical_csv, read_frames

def otids_chunk_to_canonical(chunk):
    return canonical_csv(chunk.astype(str), 'otids')

def parse_candump_chunk(*args, **kwargs):
    raise RuntimeError('Use io.read_frames with an explicit label policy and one extractor per file.')
