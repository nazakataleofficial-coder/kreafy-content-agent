"""Load only the checksum-bound, user-approved identity asset; no legacy fallback."""
import json
from PIL import Image, ImageOps
from studio.core import file_hash


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
