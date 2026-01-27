from threading import Lock

class FeatureFlags:
    def __init__(self):
        self._lock = Lock()
        self._flags = {
            "camera": True,
            "calibracao": False
        }

    def set(self, nome: str, valor: bool):
        with self._lock:
            self._flags[nome] = valor

    def get(self, nome: str) -> bool:
        with self._lock:
            return self._flags.get(nome, False)


flags = FeatureFlags()