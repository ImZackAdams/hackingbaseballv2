import os
import sys
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if "statsapi" not in sys.modules:
    sys.modules["statsapi"] = types.SimpleNamespace(schedule=lambda *a, **k: [])

if "stripe" not in sys.modules:
    fake_session = types.SimpleNamespace(id="cs_test_123")
    fake_checkout = types.SimpleNamespace(Session=types.SimpleNamespace(create=lambda *a, **k: fake_session))
    sys.modules["stripe"] = types.SimpleNamespace(api_key="", checkout=fake_checkout)

try:
    import pandas  # noqa: F401
except Exception:
    class _StubDataFrame:  # pragma: no cover - test stub
        pass

    stub_pandas = types.SimpleNamespace(DataFrame=_StubDataFrame)
    setattr(stub_pandas, "__HB_STUB__", True)
    sys.modules["pandas"] = stub_pandas
