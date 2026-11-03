"""Security regressions for the privileged per-object grant manifest."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('grants', ROOT / 'scripts/apply-aquarium-object-grants.py')
grants = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grants)


class GrantBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {'database': 'ReferenceProjectsDb', 'schema': 'Aquarium', 'runtimeRole': 'AquariumRuntime', 'developerRole': 'AquariumDeveloper', 'excludedObjects': ['__EFMigrationsHistory'], 'objects': []}

    def entry(self, **changes):
        result = {'name': 'Probe', 'type': 'TABLE', 'runtime': ['SELECT', 'INSERT'], 'developer': ['SELECT']}
        result.update(changes)
        return result

    def reject(self, entry):
        self.manifest['objects'] = [entry]
        with self.assertRaises(ValueError):
            grants.statements(self.manifest)

    def test_empty_stage1_manifest_has_no_grants(self):
        self.assertEqual([], grants.statements(self.manifest))

    def test_object_scope_and_separate_developer_read(self):
        self.manifest['objects'] = [self.entry()]
        statements = [item[2] for item in grants.statements(self.manifest)]
        self.assertEqual(['GRANT SELECT, INSERT ON OBJECT::[Aquarium].[Probe] TO [AquariumRuntime];', 'GRANT SELECT ON OBJECT::[Aquarium].[Probe] TO [AquariumDeveloper];'], statements)

    def test_other_schema_rejected(self):
        self.manifest['schema'] = 'BlastPlanning'
        with self.assertRaises(ValueError):
            grants.statements(self.manifest)

    def test_injected_identifier_rejected(self):
        self.reject(self.entry(name='Probe]; ALTER ROLE db_owner ADD MEMBER bad;--'))

    def test_qualified_identifier_rejected(self):
        self.reject(self.entry(name='dbo.OtherProduct'))

    def test_history_rejected(self):
        self.reject(self.entry(name='__EFMigrationsHistory'))

    def test_extra_history_exclusion_case_insensitive(self):
        self.manifest['excludedObjects'].append('MigrationHistory')
        self.reject(self.entry(name='migrationhistory'))

    def test_grant_authority_rejected(self):
        self.reject(self.entry(runtime=['CONTROL']))

    def test_developer_write_rejected(self):
        self.reject(self.entry(developer=['UPDATE']))

    def test_wildcard_rejected(self):
        self.reject(self.entry(name='*'))

    def test_procedure_execute_only(self):
        self.reject(self.entry(type='PROCEDURE', runtime=['SELECT'], developer=[]))

    def test_duplicate_case_insensitive_object_rejected(self):
        self.manifest['objects'] = [self.entry(), self.entry(name='probe')]
        with self.assertRaises(ValueError):
            grants.statements(self.manifest)


if __name__ == '__main__':
    unittest.main()
