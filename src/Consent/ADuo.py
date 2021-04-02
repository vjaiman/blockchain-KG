duo_prim = {
    "NRES": {"NRES", "GRU-CC", "POA", "HMB", "DS-XX"},
    "GRU-CC": {"GRU-CC", "POA", "HMB", "DS-XX"},
    "HMB": {"HMB", "DS-XX"},
    "POA": {"POA"},
    "DS-XX": {"DS-XX"},
}

duo_sec = {
    "GSO",
    "RUO",
    "RS-XX",
    "NMDS",
    "GS-XX",
    "NPU",
    "PUB",
    "COL-XX",
    "IRB",
    "TS-XX",
    "COST",
    "DSM",
}

adam_main_mapped_to_duo = {
    "NRES": "NRES",
    "GRU": "RUO",
    "NMDS": "NMDS",
    "RS-XX": "RS-XX",
    "HMB": "HMB",
    "PO": "POA",
    "ANS": "ANS",
    "GEN": "HMB",
    "GSO": "GSO",
    "DD": "HMB",
    "FB": "HMB",
    "DS-XX": "DS-XX",
    "AGE": "HMB",
    "COP": "GRU-CC",
    "GRU": "GRU-CC",
    "CC": "GRU-CC",
    "PU": "NOT-NPU",
    "NP": "HMB",
    "DSO": "GRU-CC",
    "DS": "GRU-CC",
}

#if I find these, i need the matching duo consent! No matter the main category
adam_sec_mapped_to_duo = {
    "GS-XX": "GS-CC",
    "NPU": "NPU",
    "PU": "NOT-NPU",
    "PUB": "PUB",
    "COL-XX": "COL-XX",
    "IRB": "IRB",
    "TS-XX": "TS-XX",
    "FEE": "COST",
    "DSM": "DSM"
}
