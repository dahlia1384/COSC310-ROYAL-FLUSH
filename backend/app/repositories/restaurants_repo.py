from pathlib import Path
import json, os
from typing import List, Dict, Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "restaurants.json"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_all(restaurants: List[Dict[str, Any]]) -> None:
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)