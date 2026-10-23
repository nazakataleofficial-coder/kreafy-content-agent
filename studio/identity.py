"""Load only the checksum-bound, user-approved identity asset; no legacy fallback."""
import json
from PIL import Image, ImageOps
from studio.core import file_hash

EXPRESSIONS = frozenset('approving assertive authoritative bold casual confident curious determined friendly frustrated happy intense mysterious passionate professional proud serious shocked skeptical stern thoughtful warm'.split())
TOPIC_EXPRESSIONS = {
    'diagnose-views': 'frustrated', 'thumbnail-promise': 'curious',
    'show-deliverable': 'confident', 'facebook-opening': 'thoughtful',
    'originality': 'skeptical', 'website-next-step': 'professional',
    'automation-review': 'serious', 'one-test': 'determined',
    'qualified-enquiry': 'assertive', 'repurpose': 'friendly',
    'automation-scope': 'authoritative', 'proof-without-clients': 'approving',
}


def expression_for_topic(topic):
    expression = topic.get('expression', TOPIC_EXPRESSIONS.get(topic['id']))
    if expression not in EXPRESSIONS:
        raise ValueError('Topic needs an explicit valid expression; no random portrait fallback')
    return expression


def load_expression_bank(root):
    """Verify the entire selected bank before writing any campaign output."""
    approved_reference(root)
    bank = json.loads((root / 'assets/approved_identity/expression-bank.json').read_text())
    if set(bank['assets']) != EXPRESSIONS:
        raise ValueError('Expression bank must contain exactly the 22 named portraits')
    expected_refs = {'nazakat-ale-approved.png', 'left-approved.png', 'right-approved.png'}
    if set(bank['references']) != expected_refs:
        raise ValueError('All three approved identity references are required')
    for name, record in bank['references'].items():
        if record['path'] != f'assets/approved_identity/{name}' or not record['user_approved']:
            raise ValueError('Invalid approved identity reference')
        path = root / record['path']
        if not path.is_file() or file_hash(path) != record['sha256']:
            raise ValueError('Approved identity reference missing or changed')
    for name, record in bank['assets'].items():
        if record['path'] != f'assets/real_photos/{name}.png' or not record['assistant_reviewed']:
            raise ValueError('Invalid or unreviewed expression asset')
        path = root / record['path']
        if not path.is_file() or file_hash(path) != record['sha256']:
            raise ValueError('Expression asset missing or changed; no legacy fallback')
    return bank


def expression_reference(root, expression, bank=None):
    if expression not in EXPRESSIONS:
        raise ValueError('Unknown expression')
    bank = bank if bank is not None else load_expression_bank(root)
    record = bank['assets'][expression]
    photo = root / record['path']
    if not photo.is_file() or file_hash(photo) != record['sha256']:
        raise ValueError('Expression asset missing or changed; no legacy fallback')
    with Image.open(photo) as opened:
        source = ImageOps.exif_transpose(opened).convert('RGB')
        if list(source.size) != record['size']:
            raise ValueError('Expression asset dimensions changed')
        source.load()
    policy = {'expression': expression, 'asset_ai_generated': record['ai_generated'],
              'assistant_reviewed': record['assistant_reviewed'],
              'references': bank['references'],
              'bank_sha256': file_hash(root / 'assets/approved_identity/expression-bank.json')}
    return photo, source, policy


def approved_reference(root):
    policy = json.loads((root / 'assets/approved_identity/reference.json').read_text())
    photo = root / policy['asset']
    if not photo.is_file() or file_hash(photo) != policy['sha256']:
        raise ValueError('Approved identity asset missing or changed; legacy fallback is forbidden')
    with Image.open(photo) as opened:
        source = ImageOps.exif_transpose(opened).convert('RGB')
        if list(source.size) != policy['source_size']:
            raise ValueError('Approved reference dimensions changed')
        # The approved upload is a finished poster. Remove ONLY its old lower
        # headline/footer zone; retain the complete hair, face, beard and hand.
        box = policy['photo_box']
        if box != [0, 0, 1122, 1000]:
            raise ValueError('Photo extraction requires a reviewed crop')
        extracted = source.crop(box)
    return photo, extracted, policy
