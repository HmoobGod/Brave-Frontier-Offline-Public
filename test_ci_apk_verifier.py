"""Synthetic artifact/provenance adversarial tests; no claimed signed APK acceptance."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('verifier', Path(__file__).parent / 'tools/verify_ci_apk.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class VerificationTests(unittest.TestCase):
    def test_zip_digest_and_ambiguity(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.zip'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('../app-debug.apk', b'synthetic')
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(v.payload(path, 'app-debug.apk', digest), b'synthetic')
            self.assertFalse((Path(folder).parent / 'app-debug.apk').exists())
            with self.assertRaises(ValueError): v.payload(path, 'app-debug.apk', '0'*64)
            with zipfile.ZipFile(path, 'a') as z: z.writestr('other/app-debug.apk', b'other')
            with self.assertRaises(ValueError):
                v.payload(path, 'app-debug.apk', hashlib.sha256(path.read_bytes()).hexdigest())

    def test_identity_negative_controls(self):
        apk = b'synthetic, not a real APK'
        head, checkout, cert, run = 'a'*40, 'b'*40, 'c'*64, 1687
        report = dict(schema='bf-offline-v251-owner-apk-identity-v2', source_head_sha=head,
            pull_request_head_sha=head, github_event_name='pull_request', github_sha=checkout,
            checked_out_commit_sha=checkout, build_run_number=run, apk_filename='app-debug.apk',
            apk_sha256=hashlib.sha256(apk).hexdigest(), apk_size_bytes=len(apk),
            package_id=v.PACKAGE, version_code=100000+run, version_name='174.00.0-demo',
            signing_certificate_sha256=cert, internet_permission=False)
        v.verify_receipt(apk, report, head, checkout, run, cert)
        for key in report:
            with self.subTest(key=key):
                changed = copy.deepcopy(report); changed[key] = None
                with self.assertRaises(ValueError): v.verify_receipt(apk, changed, head, checkout, run, cert)
        with self.assertRaises(ValueError): v.verify_receipt(apk+b'tamper', report, head, checkout, run, cert)
        with self.assertRaises(ValueError): v.verify_receipt(apk, report, 'd'*40, checkout, run, cert)
        with self.assertRaises(ValueError): v.verify_receipt(apk, report, head, checkout, run, 'e'*64)

if __name__ == '__main__': unittest.main()
