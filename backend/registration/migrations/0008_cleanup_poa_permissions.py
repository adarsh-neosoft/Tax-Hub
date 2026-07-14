# Removes duplicate permissions created by post_migrate after the model rename.
# Only acts if stale old-codename permissions still exist — otherwise does nothing,
# guarding against the case where 0007's data migration already handled the rename.

from django.db import migrations


def fix_duplicate_poa_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    try:
        ct = ContentType.objects.get(app_label='registration', model='poatracker')
    except ContentType.DoesNotExist:
        return

    # Check if old-codename permissions still exist (they have group/user assignments)
    stale_old = Permission.objects.filter(
        content_type=ct,
        codename__endswith='_powerofattorneytracker',
    )

    if not stale_old.exists():
        # Already cleaned up by 0007's data migration — nothing to do
        return

    # Delete the NEW duplicate permissions (auto-created by post_migrate)
    # These have NO group/user assignments, unlike the originals.
    Permission.objects.filter(
        content_type=ct,
        codename__endswith='_poatracker',
    ).delete()

    # Rename the old permissions' codenames to match the renamed model
    for perm in stale_old:
        perm.codename = perm.codename.replace(
            '_powerofattorneytracker', '_poatracker'
        )
        if 'Power Of Attorney' in perm.name:
            perm.name = perm.name.replace(
                'Power Of Attorney Tracker', 'POA Tracker'
            )
        perm.save()


def reverse_fix(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0007_rename_and_options'),
    ]

    operations = [
        migrations.RunPython(
            fix_duplicate_poa_permissions,
            reverse_fix,
        ),
    ]
