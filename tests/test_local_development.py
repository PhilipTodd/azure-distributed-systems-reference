"""Local bootstrap must reject cloud/public targets and unpinned dependencies."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('local_setup', ROOT / 'scripts/local-development.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class LocalBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.config = {'services': {name: {'image': 'mcr.microsoft.com/test@sha256:' + 'a'*64, 'ports': [{'host_ip': '127.0.0.1'}]} for name in ['sql', 'cosmos']}}

    def test_rejects_public_bind(self):
        for address in ['0.0.0.0', '::', '192.168.0.1', None]:
            config=copy.deepcopy(self.config); config['services']['cosmos']['ports'][0]['host_ip']=address
            with self.assertRaises(ValueError): m.validate_config(config)

    def test_rejects_floating_image(self):
        self.config['services']['cosmos']['image']='example:latest'
        with self.assertRaises(ValueError): m.validate_config(self.config)

    def test_rejects_extra_service(self):
        self.config['services']['unexpected']={}
        with self.assertRaises(ValueError): m.validate_config(self.config)

    def test_rejects_host_network_or_privilege(self):
        for key,value in [('network_mode','host'),('privileged',True)]:
            config=copy.deepcopy(self.config);config['services']['sql'][key]=value
            with self.assertRaises(ValueError): m.validate_config(config)

    def test_rejects_secret_in_compose_environment(self):
        self.config['services']['sql']['environment']={'MSSQL_SA_PASSWORD':'not-a-real-password'}
        with self.assertRaises(ValueError): m.validate_config(self.config)

    def test_rejects_other_project_before_touching_machine(self):
        for name in ['blast-iq','pp-local-check-other','../../outside','rg-platform-dev']:
            with self.assertRaises(ValueError): m.environment(name)

    def test_pending_baseline_cannot_start_containers(self):
        with patch.object(m.Path,'read_text',return_value='{"status":"pending-owner-decision"}'), patch.object(m,'compose') as compose:
            with self.assertRaisesRegex(RuntimeError,'awaits owner approval'): m.up('pp-local',{})
            compose.assert_not_called()


if __name__=='__main__': unittest.main()
