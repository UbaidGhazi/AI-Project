"""
prolog_connector.py
Lazy-loads SWI-Prolog via PySWIP only when first used.
If SWI-Prolog is not installed the rest of the GUI still works;
queries return empty results and a warning is printed.
"""

import os

_PROLOG_AVAILABLE = None   # None = not yet checked


def _check_prolog():
    global _PROLOG_AVAILABLE
    if _PROLOG_AVAILABLE is not None:
        return _PROLOG_AVAILABLE
    try:
        from pyswip import Prolog  # noqa: F401
        _PROLOG_AVAILABLE = True
    except Exception as e:
        print(f"[WARN] SWI-Prolog not available: {e}")
        _PROLOG_AVAILABLE = False
    return _PROLOG_AVAILABLE


class PrologConnector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            obj = super().__new__(cls)
            obj.prolog = None
            obj._available = False
            cls._instance = obj
        return cls._instance

    def _ensure_loaded(self):
        if self.prolog is not None:
            return True
        if not _check_prolog():
            return False
        try:
            from pyswip import Prolog
            self.prolog = Prolog()
            self._load_files()
            self._available = True
        except Exception as e:
            print(f"[WARN] Prolog init failed: {e}")
            self._available = False
        return self._available

    def _load_files(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prolog_dir = os.path.join(base_dir, "prolog")

        for fname in ("knowledge_base.pl", "rules.pl", "inference.pl"):
            path = os.path.join(prolog_dir, fname).replace("\\", "/")
            self.prolog.consult(path)

    # ── Public API ──────────────────────────────────────────────────────────

    @property
    def available(self):
        return self._ensure_loaded()

    def assert_symptom(self, symptom):
        if not self._ensure_loaded():
            return
        try:
            list(self.prolog.query(f"assertz(symptom({symptom}))"))
        except Exception as e:
            print(f"[WARN] Prolog assertz symptom failed ({symptom}): {e}")
            raise e

    def retract_all_symptoms(self):
        if not self._ensure_loaded():
            return
        try:
            list(self.prolog.query("retractall(symptom(_))"))
        except Exception as e:
            print(f"[WARN] Prolog retractall symptoms failed: {e}")
            raise e


    def query(self, query_string):
        if not self._ensure_loaded():
            return []
        try:
            return list(self.prolog.query(query_string))
        except Exception as e:
            print(f"[WARN] Prolog query failed ({query_string}): {e}")
            return []
