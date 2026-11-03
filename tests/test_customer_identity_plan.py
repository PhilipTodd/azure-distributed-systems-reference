"""Prevent customer identity bootstrap from drifting beyond accepted ADR-009."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('customer', ROOT / 'scripts/bootstrap-customer-identity.py')
customer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(customer)


class CustomerPlanTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads(customer.MANIFEST.read_text(encoding='utf-8'))

    def test_reviewed_plan_accepted(self):
        customer.validate(self.plan)

    def test_workforce_tenant_refused_before_token_request(self):
        with self.assertRaises(ValueError):
            customer.Graph(customer.delivery.TENANT)

    def test_wildcard_callback_refused(self):
        self.plan['spaRedirectUris'].append('https://*.parameterpilot.com')
        with self.assertRaises(ValueError): customer.validate(self.plan)

    def test_social_signin_refused(self):
        self.plan['customerSignIn'] = 'Google'
        with self.assertRaises(ValueError): customer.validate(self.plan)

    def test_downstream_write_refused(self):
        self.plan['trackingDownstreamScope'] = 'Aquarium.Write'
        with self.assertRaises(ValueError): customer.validate(self.plan)

    def test_advisor_registration_refused(self):
        self.plan['applications']['advisor'] = {'displayName': 'Unapproved Advisor'}
        with self.assertRaises(ValueError): customer.validate(self.plan)

    def test_unapproved_scope_refused(self):
        self.plan['applications']['aquarium']['scopes'].append('Aquarium.Admin')
        with self.assertRaises(ValueError): customer.validate(self.plan)

    def test_scope_ids_stable_and_service_distinct(self):
        tenant = '00000000-0000-0000-0000-000000000001'
        first = customer.scope_id(tenant, 'aquarium', 'Aquarium.Read')
        self.assertEqual(first, customer.scope_id(tenant, 'aquarium', 'Aquarium.Read'))
        self.assertNotEqual(first, customer.scope_id(tenant, 'tracking', 'Tracking.Read'))

    def test_readback_rejects_missing_protection(self):
        self.assertFalse(customer.contains({'isSignUpAllowed': True}, {'isSignUpAllowed': False}))


if __name__ == '__main__':
    unittest.main()
