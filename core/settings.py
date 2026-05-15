import json
import os
from pathlib import Path

DEFAULT_PRESETS = [
    {"label": "5 min",  "seconds": 300},
    {"label": "15 min", "seconds": 900},
    {"label": "30 min", "seconds": 1800},
]


class PresetsManager:
    def __init__(self):
        appdata = os.environ.get("APPDATA")
        if appdata:
            self._path = Path(appdata) / "Timer" / "presets.json"
        else:
            self._path = Path(__file__).parent.parent / "data" / "presets.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        if not self._path.exists():
            self.save(list(DEFAULT_PRESETS))
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, IOError):
            pass
        return list(DEFAULT_PRESETS)

    def save(self, presets):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(presets, f, indent=2, ensure_ascii=False)

    def add(self, label, seconds):
        presets = self.load()
        presets.append({"label": label, "seconds": seconds})
        self.save(presets)
        return presets

    def update(self, index, label, seconds):
        presets = self.load()
        if 0 <= index < len(presets):
            presets[index] = {"label": label, "seconds": seconds}
            self.save(presets)
        return presets

    def delete(self, index):
        presets = self.load()
        if 0 <= index < len(presets):
            presets.pop(index)
            self.save(presets)
        return presets
