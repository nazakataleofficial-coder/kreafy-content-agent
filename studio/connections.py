"""Read-only readiness report using existing Buffer secrets. Never publishes."""
from studio.core import ACCOUNTS
from studio.delivery import graphql, verify_channel


def inspect_connections(token, channel_ids, transport=graphql):
    if not token:
        raise ValueError('Existing BUFFER_ACCESS_TOKEN is missing; no credential was created')
    organizations = transport('query Account { account { organizations { id } } }', {}, token).get('account', {}).get('organizations', [])
    if not organizations or len(organizations) > 5:
        raise ValueError('Cannot safely identify the existing Buffer organization')
    report = {}
    for platform in ('linkedin', 'instagram', 'twitter'):
        channel_id = channel_ids.get(platform)
        if not channel_id:
            report[platform] = {'ready': False, 'reason': 'Existing channel ID secret is missing'}
            continue
        errors = []
        for organization in organizations:
            try:
                verify_channel(platform, channel_id, organization['id'], token, transport)
                report[platform] = {'ready': True, 'account_url': ACCOUNTS[platform],
                                    'note': 'Read-only identity/connection check only; no post was sent'}
                break
            except ValueError as exc:
                errors.append(str(exc))
        else:
            report[platform] = {'ready': False, 'reason': '; '.join(sorted(set(errors)))}
    report['facebook'] = {'ready': False, 'reason': 'Professional profile has no supported Buffer publishing route'}
    return report
