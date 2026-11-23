import os
from pathlib import Path

DEFAULT_DB_PATH = Path(os.getenv("IT_OPS_DB_PATH", "data/it_ops_hub.db"))
DEFAULT_DOMAIN_DN = os.getenv("AD_DOMAIN_BASE_DN", "DC=corp,DC=local")
DEFAULT_NETWORK_TARGETS = Path(os.getenv("NETWORK_TARGETS_CONFIG", "network_targets.json"))
DEFAULT_KB_DIR = Path("kb-articles")
