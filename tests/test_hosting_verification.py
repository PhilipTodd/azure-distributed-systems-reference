"""Safety regression: hosting preparation must never take the data-test path."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hosting', ROOT / 'scripts/run-hosting-verification.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


class HostingSafetyTests(unittest.TestCase):
    def test_prepare_uses_both_real_hosts_without_sql_or_cosmos(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / '.runtime'
            (runtime / 'publish').mkdir(parents=True)
            (root / 'Dockerfile').write_text('FROM test-only')
            grants = []

            def az(*args):
                if args[:2] == ('account', 'show'):
                    return {'id': h.p.SUB, 'tenantId': h.p.TENANT}
                if args[:3] == ('role', 'assignment', 'list'): return []
                if args[:3] == ('role', 'assignment', 'create'):
                    principal = args[args.index('--assignee-object-id') + 1]
                    grants.append(principal)
                    return {'id': h.p.REGISTRY + '/providers/Microsoft.Authorization/roleAssignments/' + args[args.index('--name') + 1], 'condition': args[args.index('--condition') + 1]}
                if args[:3] == ('webapp', 'config', 'appsettings'): return []
                return {}

            def rest(method, path, body=None):
                if '/config/logs?' in path:
                    return {'properties': {'httpLogs': {'fileSystem': {'enabled': False}}}}
                service = 'tracking' if 'tracking' in path else 'aquarium'
                return {'identity': {'principalId': h.p.IDENTITIES[service]}, 'properties': {'enabled': False, 'publicNetworkAccess': 'Disabled'}, 'kind': 'app,linux,container'}

            with patch.multiple(h.p, PROBE=root, RUNTIME=runtime, JOURNAL=runtime / 'journal.json'), patch.object(h.p, 'az', side_effect=az), patch.object(h.p, 'rest', side_effect=rest), patch.object(h.p, 'sql_connect', side_effect=AssertionError('Hosting must not connect to SQL')) as sql:
                h.p.prepare('hosting')
                self.assertEqual(set(grants), {*h.p.IDENTITIES.values(), '7233cead-7a49-4ab1-80f9-6066a03d193f'})
                self.assertNotIn('sqlSecurityBefore', h.p.load())
                sql.assert_not_called()

    def test_network_timeout_is_a_retryable_startup_result(self):
        with patch.object(h.urllib.request, 'urlopen', side_effect=TimeoutError):
            self.assertEqual(h.request('https://example.invalid'), (598, None))

    def test_initial_metrics_have_at_least_two_minutes_of_history(self):
        from datetime import datetime, timezone
        from urllib.parse import parse_qs, urlparse
        now = datetime.now(timezone.utc)
        with patch.object(h, 'arm', return_value={'value': []}) as arm:
            h.metrics(now.strftime('%Y-%m-%dT%H:%M:%SZ'))
            timespan = parse_qs(urlparse(arm.call_args.args[1]).query)['timespan'][0]
            start, end = [datetime.fromisoformat(value.replace('Z', '+00:00')) for value in timespan.split('/')]
            self.assertGreaterEqual((end-start).total_seconds(), 120)


if __name__ == '__main__': unittest.main()
