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
    if args.command == 'import-drive':
        from studio.drive import import_images
        imported = import_images(args.folder, args.out)
        print(f'{len(imported)} images imported read-only. No automatic use or sharing.')
        return
    manifest = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    post = manifest['platforms'][args.platform]
    count = validate_post(post, args.platform)
    if args.command == 'validate':
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
