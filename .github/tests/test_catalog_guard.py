import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("catalog_guard", ROOT / ".github/scripts/catalog_guard.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)

def fixture():
    return {
        "format": "pimfx-community-preset", "formatVersion": 3,
        "id": "routing-test", "name": "Routing Test", "author": "Test",
        "description": "", "tags": [], "license": "MIT", "checksums": {},
        "compatibility": {"minimumPiMfxVersion": "0.6.0"},
        "preset": {
            "name": "Routing Test", "tempo": 120, "inputGainDb": 0, "outputGainDb": 0,
            "chain": [
                {"id": "amp", "uri": "urn:test:amp", "name": "Amp", "enabled": True, "state": {}},
                {"id": "mix", "kind": "mixer", "name": "Mixer", "enabled": True, "state": {}}
            ],
            "snapshots": [], "parameterBindings": [], "routingFormat": 1,
            "routing": {"version": 1, "positions": {}, "edges": [
                {"from": "input", "to": "amp"}, {"from": "amp", "to": "mix"},
                {"from": "input", "to": "mix"}, {"from": "mix", "to": "output"}
            ]}
        },
        "dependencies": {"effects": [{"uri": "urn:test:amp"}], "tone3000": [], "irs": [], "localAssets": []}
    }

class RoutingPackageTest(unittest.TestCase):
    def test_branch_merge_and_mixer_validate(self):
        guard.validate_manifest(fixture())

    def test_invalid_connections_rejected(self):
        for edge in [{"from": "mix", "to": "amp"}, {"from": "unknown", "to": "mix"},
                     {"from": "input", "to": "amp"}, {"from": "output", "to": "mix"}]:
            with self.subTest(edge=edge):
                data = fixture()
                data["preset"]["routing"]["edges"].append(edge)
                with self.assertRaises(guard.GuardError):
                    guard.validate_manifest(data)

    def test_bad_positions_and_levels_rejected(self):
        for change in [
            lambda r: r["positions"].update({"unknown": {"x": 0, "y": 0}}),
            lambda r: r["positions"].update({"amp": {"x": -1, "y": 0}}),
            lambda r: r["edges"][0].update({"levelDb": 13}),
            lambda r: r["edges"][0].update({"mute": "yes"}),
        ]:
            data = fixture()
            change(data["preset"]["routing"])
            with self.assertRaises(guard.GuardError):
                guard.validate_manifest(data)

    def test_snapshots_only_reference_existing_connections(self):
        data = fixture()
        data["preset"]["snapshots"] = [{"routingMix": [{"from": "amp", "to": "mix", "levelDb": -6}]}]
        guard.validate_manifest(data)
        data["preset"]["snapshots"][0]["routingMix"][0]["to"] = "output"
        with self.assertRaises(guard.GuardError):
            guard.validate_manifest(data)

    def test_duplicate_snapshot_mix_rejected(self):
        data = fixture()
        edge = {"from": "amp", "to": "mix", "levelDb": -6}
        data["preset"]["snapshots"] = [{"routingMix": [edge, copy.deepcopy(edge)]}]
        with self.assertRaises(guard.GuardError):
            guard.validate_manifest(data)

    def test_dependencies_match_plugins(self):
        data = fixture()
        data["dependencies"]["effects"] = []
        with self.assertRaises(guard.GuardError):
            guard.validate_manifest(data)

    def test_layout_does_not_change_sound_identity(self):
        data = fixture()
        other = copy.deepcopy(data)
        other["preset"]["routing"]["positions"] = {"amp": {"x": 40, "y": 80}}
        self.assertEqual(guard.content_fingerprint(data), guard.content_fingerprint(other))
        other["preset"]["routing"]["edges"][0]["levelDb"] = -6
        self.assertNotEqual(guard.content_fingerprint(data), guard.content_fingerprint(other))

    def test_old_format_rejected(self):
        data = fixture()
        data["formatVersion"] = 2
        with self.assertRaises(guard.GuardError):
            guard.validate_manifest(data)

    def test_matches_pimfx_number_formatting(self):
        value = {"tempo": 120.731, "gain": -6.153846263885498, "integralFloat": 1.0, "enabled": True}
        self.assertEqual(guard.pimfx_compact_json(value),
                         '{"tempo":120.73099999999999,"gain":-6.153846263885498,"integralFloat":1,"enabled":true}')

if __name__ == "__main__":
    unittest.main()
