from threading import Lock

class FeatureFlags:
    def __init__(self):
        self._lock = Lock()

        self._flags = {
            "calibracao": {
                "global": False,
                "postos": {}
            },
            "camera": {
                "global": True,
                "postos": {}
            }
        }

    def set_global(self, feature: str, enabled: bool):
        with self._lock:
            self._flags.setdefault(feature, {"global": False, "postos": {}})
            self._flags[feature]["global"] = enabled

    def set_posto(self, feature: str, posto: int, enabled: bool):
        with self._lock:
            self._flags.setdefault(feature, {"global": False, "postos": {}})
            self._flags[feature]["postos"][posto] = enabled

    def is_enabled(self, feature: str, posto: int | None = None) -> bool:
        with self._lock:
            data = self._flags.get(feature)
            if not data:
                return False

            if posto is not None and posto in data["postos"]:
                return data["postos"][posto]

            return data["global"]

flags = FeatureFlags()