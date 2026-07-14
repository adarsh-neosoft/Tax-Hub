# Generated manually — merges model rename PowerOfAttorneyTracker → PoaTracker,
# db_table change, verbose_name updates, and permission updates

from django.db import migrations


def update_poa_permissions(apps, schema_editor):
    """
    Update auth_permission codenames and names to reflect the renamed model.
    The RenameModel migration above updates the ContentType entry, but
    the Permission records themselves still have old codenames/names.
    """
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    try:
        ct = ContentType.objects.get(app_label='registration', model='poatracker')
    except ContentType.DoesNotExist:
        return  # Migration not fully applied yet in test contexts

    perms = Permission.objects.filter(content_type=ct)
    for perm in perms:
        # Update codename: add_powerofattorneytracker → add_poatracker
        if '_powerofattorneytracker' in perm.codename:
            perm.codename = perm.codename.replace(
                '_powerofattorneytracker', '_poatracker'
            )
        # Update name: "Can add Power Of Attorney Tracker" → "Can add POA Tracker"
        if 'Power Of Attorney Tracker' in perm.name:
            perm.name = perm.name.replace(
                'Power Of Attorney Tracker', 'POA Tracker'
            )
        # Handle plural in name: "Power Of Attorney Trackers" → "POA Tracker"
        if 'Power Of Attorney Trackers' in perm.name:
            perm.name = perm.name.replace(
                'Power Of Attorney Trackers', 'POA Tracker'
            )
        perm.save()


def reverse_poa_permissions(apps, schema_editor):
    """Reverse the permission updates."""
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    try:
        ct = ContentType.objects.get(app_label='registration', model='poatracker')
    except ContentType.DoesNotExist:
        return

    perms = Permission.objects.filter(content_type=ct)
    for perm in perms:
        if '_poatracker' in perm.codename:
            perm.codename = perm.codename.replace(
                '_poatracker', '_powerofattorneytracker'
            )
        if 'POA Tracker' in perm.name:
            perm.name = perm.name.replace('POA Tracker', 'Power Of Attorney Tracker')
        perm.save()


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0006_opinionmanagement'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dsctracker',
            options={'verbose_name': 'DSC Tracker', 'verbose_name_plural': 'DSC Tracker'},
        ),
        migrations.AlterModelOptions(
            name='powerofattorneytracker',
            options={'verbose_name': 'POA Tracker', 'verbose_name_plural': 'POA Tracker'},
        ),
        migrations.RenameModel(
            old_name='PowerOfAttorneyTracker',
            new_name='PoaTracker',
        ),
        migrations.AlterModelTable(
            name='poatracker',
            table='poa_tracker',
        ),
        migrations.RunPython(
            update_poa_permissions,
            reverse_poa_permissions,
        ),
    ]
