import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from studio.core import PLATFORMS, approve, atomic_json, validate_post


def main():
    parser = argparse.ArgumentParser(description='Kreafy no-API-cost draft studio; publishing is off by default')
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare')
    prepare.add_argument('--start', default=datetime.now(ZoneInfo('Asia/Karachi')).date().isoformat())
    prepare.add_argument('--out', default='studio-output')
    commands.add_parser('inspect-buffer')
    status = commands.add_parser('status')
    status.add_argument('--journal', default='studio-private/delivery.sqlite3')
    record = commands.add_parser('record-publication')
    record.add_argument('manifest')
    record.add_argument('--platform', choices=PLATFORMS, required=True)
    record.add_argument('--url', required=True)
    record.add_argument('--observed-at', required=True)
    record.add_argument('--published-at')
    record.add_argument('--account-verified', action='store_true')
    record.add_argument('--journal', default='studio-private/delivery.sqlite3')
    drive = commands.add_parser('import-drive')
    drive.add_argument('--folder', required=True)
    drive.add_argument('--out', default='studio-private/drive')
    for command in ('validate', 'approve', 'queue'):
        sub = commands.add_parser(command)
        sub.add_argument('manifest')
        sub.add_argument('--platform', choices=PLATFORMS, required=True)
        if command == 'queue':
            sub.add_argument('--journal', default='studio-private/delivery.sqlite3')
    args = parser.parse_args()
    if args.command == 'prepare':
        from studio.prepare import prepare
        paths = prepare(Path(__file__).resolve().parents[1], args.out, args.start)
        print(f'{len(paths)} topics / {len(paths)*4} drafts prepared. Nothing queued or published.')
        return
    if args.command == 'inspect-buffer':
        from studio.connections import inspect_connections
        report = inspect_connections(os.environ.get('BUFFER_ACCESS_TOKEN', ''),
            {p: os.environ.get(f'BUFFER_{p.upper()}_ID', '') for p in ('linkedin', 'instagram', 'twitter')})
        print(json.dumps(report, indent=2))
        if not all(report[p]['ready'] for p in ('linkedin', 'instagram', 'twitter')):
            raise SystemExit(1)
        return
    if args.command == 'import-drive':
        from studio.drive import import_images
        imported = import_images(args.folder, args.out)
        print(f'{len(imported)} images imported read-only. No automatic use or sharing.')
        return
    if args.command == 'status':
        from studio.publications import publication_status
        print(json.dumps(publication_status(journal=args.journal), ensure_ascii=False, indent=2))
        return
    manifest = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    post = manifest['platforms'][args.platform]
    count = validate_post(post, args.platform)
    if args.command == 'record-publication':
        from studio.publications import record_publication
        receipt = record_publication(post, args.platform, args.journal, args.url,
                                     args.observed_at, args.published_at, args.account_verified)
        print(json.dumps(receipt, indent=2))
    elif args.command == 'validate':
        print(f'{args.platform}: valid local image and caption ({count} conservative characters). Account and live sources need verification before delivery.')
    elif args.command == 'approve':
        approve(post)
        atomic_json(args.manifest, manifest)
        print(f'Exact {args.platform} preview approved locally. Nothing sent.')
    elif args.command == 'queue':
        from studio.delivery import queue_post
        receipt = queue_post(post, args.platform, args.journal,
                             os.environ.get(f'BUFFER_{args.platform.upper()}_ID', ''),
                             os.environ.get('BUFFER_ORGANIZATION_ID', ''),
                             os.environ.get('BUFFER_ACCESS_TOKEN', ''))
        print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
