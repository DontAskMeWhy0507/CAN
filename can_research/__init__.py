"""Reusable utilities for the CAN distribution-shift research notebooks."""

try:
    from .data import (
        CTT_SCENARIOS,
        CTT_VEHICLES,
        CANONICAL_COLUMNS,
        audit_workspace,
        canonicalize_cici_hex,
        canonicalize_ctt,
        parse_candump_log,
        read_canonical_file,
    )
except ImportError:
    pass

try:
    from .preprocess import (
        FEATURE_COLUMNS,
        FRAME_FEATURE_COLUMNS,
        compute_ctt_metrics,
        compute_shift_effects,
        extract_windows_from_df,
        load_balanced_train_windows,
    )
    create_windows = extract_windows_from_df
except ImportError:
    pass


try:
    from .features import (
        build_raw_features,
        build_structural_features,
        extract_windows,
        sample_ctt_train_windows,
    )
except ImportError:
    pass

try:
    from .metrics import (
        StreamingBinaryEvaluator,
        choose_threshold_on_validation,
        compute_binary_metrics,
    )
except ImportError:
    pass

__all__ = [
    "CANONICAL_COLUMNS",
    "CTT_SCENARIOS",
    "CTT_VEHICLES",
    "StreamingBinaryEvaluator",
    "audit_workspace",
    "build_raw_features",
    "build_structural_features",
    "canonicalize_cici_hex",
    "canonicalize_ctt",
    "choose_threshold_on_validation",
    "compute_binary_metrics",
    "extract_windows",
    "parse_candump_log",
    "read_canonical_file",
    "sample_ctt_train_windows",
]
