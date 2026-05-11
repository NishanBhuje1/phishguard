import json
import numpy as np
import joblib
import pandas as pd
from pathlib import Path

_ML_DIR = Path(__file__).parent.parent / "ml"
MODEL_PATH = _ML_DIR / "model.pkl"
FEATURES_PATH = _ML_DIR / "feature_columns.json"

model = joblib.load(MODEL_PATH)

with open(FEATURES_PATH) as f:
    feature_columns = json.load(f)

# UCI columns we populate from URL-extracted features.
# All other columns default to 0 (the neutral/unknown middle value).
# Asymmetric rule for prefix_suffix: only set to -1 when we have positive
# evidence of a brand typo — otherwise leave it at 0 (we cannot confirm a dash).
_UCI_MAP = {
    "having_ip_address",
    "url_length",
    "shortining_service",
    "having_at_symbol",
    "double_slash_redirecting",
    "having_sub_domain",
    "domain_registration_length",
    "google_index",
    "sslfinal_state",   # derived from uses_https (33% of model importance)
    # prefix_suffix added conditionally below
}


def _encode(features: dict) -> dict:
    """Convert extracted feature values to UCI -1/0/1 encoding."""
    enc = {}

    # having_ip_address: -1 if IP, 1 if domain
    enc["having_ip_address"] = -1 if features["has_ip_address"] else 1

    # url_length thresholds: ≤54→1, 54-75→0, >75→-1
    length = features["url_length"]
    enc["url_length"] = 1 if length <= 54 else (0 if length <= 75 else -1)

    # shortining_service: -1 if shortener, 1 if not
    enc["shortining_service"] = -1 if features["is_url_shortener"] else 1

    # having_at_symbol: proxy for special_char_count (>8 → phishing)
    enc["having_at_symbol"] = -1 if features["special_char_count"] > 8 else 1

    # double_slash_redirecting: proxy for path_depth (>3 → suspicious)
    enc["double_slash_redirecting"] = -1 if features["path_depth"] > 3 else 1

    # prefix_suffix: only assert -1 when we have confirmed a brand typo.
    # When no typo is found we can't confirm there's no dash in the domain,
    # so we leave the column at 0 (neutral) rather than asserting 1 (clean).
    if features["has_brand_typo"]:
        enc["prefix_suffix"] = -1

    # having_sub_domain: 1=none, 0=one, -1=many
    subs = features["subdomain_count"]
    enc["having_sub_domain"] = 1 if subs == 0 else (0 if subs == 1 else -1)

    # domain_registration_length: proxy for suspicious_tld
    enc["domain_registration_length"] = -1 if features["suspicious_tld"] else 1

    # google_index: proxy for phishtank_match
    enc["google_index"] = -1 if features["phishtank_match"] else 1

    # sslfinal_state: 1 = HTTPS, -1 = HTTP (top feature, 33% model importance)
    enc["sslfinal_state"] = 1 if features.get("uses_https", False) else -1

    return enc


def classify_url(features: dict) -> dict:
    enc = _encode(features)

    # Build full vector: mapped columns use extracted values,
    # all other columns default to 0 (neutral/unknown)
    vector = np.array(
        [enc.get(col, 0) for col in feature_columns], dtype=float
    ).reshape(1, -1)

    df_row = pd.DataFrame(vector, columns=feature_columns)

    # predict_proba[:, 1] = probability of class 1 (phishing)
    confidence = float(model.predict_proba(df_row)[0][1])

    if confidence >= 0.75:
        verdict = "phishing"
    elif confidence >= 0.45:
        verdict = "suspicious"
    else:
        verdict = "safe"

    return {"verdict": verdict, "confidence": round(confidence, 4)}
