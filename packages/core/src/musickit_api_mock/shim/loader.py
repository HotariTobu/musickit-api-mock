"""Load the bundled shim JavaScript text via importlib.resources."""

from importlib.resources import files


def _load_shim_script() -> str:
    base = files("musickit_api_mock.shim")
    parts = [
        (base / "eme.js").read_text(encoding="utf-8"),
        (base / "oauth.js").read_text(encoding="utf-8"),
        (base / "network.js").read_text(encoding="utf-8"),
    ]
    return "\n;\n".join(parts)
