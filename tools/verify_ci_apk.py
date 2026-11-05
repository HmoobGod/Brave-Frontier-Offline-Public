"""Offline verification of downloaded CI APK + identity ZIPs; never installs APKs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

PACKAGE = 'org.bravefrontier.offline'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def payload(path, suffix, digest):
    require(re.fullmatch(r'[0-9a-f]{64}', digest) is not None, 'Invalid trusted artifact digest')
    require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'Artifact ZIP digest mismatch')
    with zipfile.ZipFile(path) as archive:
        matches = [i for i in archive.infolist() if i.filename.endswith(suffix)]
        require(len(matches) == 1, 'Exactly one artifact payload required')
        item = matches[0]
        require(item.file_size <= 64 * 1024 * 1024, 'Artifact payload exceeds size limit')
        # Read a single member without extracting paths or executing archive files.
        return archive.read(item)


def verify_receipt(apk, report, head, checkout, run, certificate):
    for sha in (head, checkout):
        require(re.fullmatch(r'[0-9a-f]{40}', sha) is not None, 'Invalid expected commit')
    require(re.fullmatch(r'[0-9a-f]{64}', certificate) is not None, 'Invalid trusted certificate')
    expected = {
        'schema': 'bf-offline-v251-owner-apk-identity-v2',
        'source_head_sha': head, 'pull_request_head_sha': head,
        'github_event_name': 'pull_request', 'github_sha': checkout,
        'checked_out_commit_sha': checkout, 'build_run_number': run,
        'apk_filename': 'app-debug.apk', 'apk_sha256': hashlib.sha256(apk).hexdigest(),
        'apk_size_bytes': len(apk), 'package_id': PACKAGE,
        'version_code': 100000 + run, 'version_name': '174.00.0-demo',
        'signing_certificate_sha256': certificate, 'internet_permission': False,
    }
    require(type(run) is int and run > 0, 'Invalid run number')
    for key, value in expected.items():
        require(type(report.get(key)) is type(value) and report[key] == value,
                'Identity mismatch: ' + key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('apk-zip', 'identity-zip', 'apk-zip-sha256', 'identity-zip-sha256',
                'head', 'checkout', 'certificate', 'build-tools'):
        parser.add_argument('--' + arg, required=True)
    parser.add_argument('--run', type=int, required=True)
    args = parser.parse_args()
    apk = payload(Path(args.apk_zip), 'app-debug.apk', args.apk_zip_sha256)
    report = json.loads(payload(Path(args.identity_zip),
                               'BraveFrontier-v251-owner-apk-identity.json',
                               args.identity_zip_sha256))
    verify_receipt(apk, report, args.head, args.checkout, args.run, args.certificate)
    with tempfile.TemporaryDirectory(prefix='bf-apk-verify-') as folder:
        path = Path(folder) / 'candidate.apk'
        path.write_bytes(apk)
        tools = Path(args.build_tools)
        signature = subprocess.check_output([str(tools / 'apksigner'), 'verify',
                    '--verbose', '--print-certs', str(path)], text=True)
        certs = re.findall(r'(?im)^Signer #\d+ certificate SHA-256 digest:\s*([a-f0-9]{64})\s*$', signature)
        require(certs == [args.certificate], 'Actual signer mismatch')
        badging = subprocess.check_output([str(tools / 'aapt'), 'dump', 'badging', str(path)], text=True)
        match = re.search(r"(?m)^package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", badging)
        require(match is not None and match.groups() == (PACKAGE, str(100000 + args.run),
                                                        '174.00.0-demo'), 'Actual package/version mismatch')
        permissions = subprocess.check_output([str(tools / 'aapt'), 'dump', 'permissions', str(path)], text=True)
        require('android.permission.INTERNET' not in permissions, 'Actual APK requests Internet')
    print('PASS: artifact digests, PR identity, APK signature, certificate, package and offline permission')
    print('Owner installed APK, save compatibility and Android device acceptance: NOT TESTED')


if __name__ == '__main__':
    main()
