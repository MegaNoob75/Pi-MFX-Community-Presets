import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "catalog_guard", ROOT / ".github/scripts/catalog_guard.py"
)
catalog_guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog_guard)


class PiMfxJsonCompatibilityTest(unittest.TestCase):
    def test_matches_pimfx_number_formatting(self):
        value = {
            "tempo": 120.731,
            "gain": -6.153846263885498,
            "integralFloat": 1.0,
            "enabled": True,
        }
        self.assertEqual(
            catalog_guard.pimfx_compact_json(value),
            '{"tempo":120.73099999999999,"gain":-6.153846263885498,"integralFloat":1,"enabled":true}',
        )

    def test_preset_1_hashes_match_catalog(self):
        manifest = catalog_guard.load_json(ROOT / "presets/preset-1/manifest.json")
        catalog = catalog_guard.load_json(ROOT / "catalog/index.json")
        entry = next(item for item in catalog["presets"] if item["id"] == "preset-1")
        self.assertEqual(catalog_guard.compact_sha256(manifest), entry["manifestSha256"])
        self.assertEqual(catalog_guard.content_fingerprint(manifest), entry["contentSha256"])


if __name__ == "__main__":
    unittest.main()
