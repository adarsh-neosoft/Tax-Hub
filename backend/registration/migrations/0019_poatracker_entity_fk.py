from django.db import migrations, models
import django.db.models.deletion


def map_entity_names_to_legal_entities(apps, schema_editor):
    """Try to match existing entity_name strings to LegalEntity records by entity_name."""
    PoaTracker = apps.get_model("registration", "PoaTracker")
    LegalEntity = apps.get_model("masters", "LegalEntity")
    
    for poa in PoaTracker.objects.all():
        old_name = poa.entity_name
        if not old_name:
            continue
        # Try to find a matching LegalEntity by entity_name
        match = LegalEntity.objects.filter(entity_name__iexact=old_name).first()
        if match:
            poa.entity_ref_id = match.id
        else:
            # Try partial match
            match = LegalEntity.objects.filter(entity_name__icontains=old_name).first()
            if match:
                poa.entity_ref_id = match.id
        poa.save()


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0016_purchaseorder'),
        ('registration', '0018_itrstatus_updated_fields'),
    ]

    operations = [
        # Step 1: Add new FK field (temporary name: entity_ref)
        migrations.AddField(
            model_name='poatracker',
            name='entity_ref',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='masters.legalentity',
                verbose_name='Name of Entity (temp)',
            ),
        ),
        # Step 2: Copy existing data from entity_name (CharField) to entity_ref (FK)
        migrations.RunPython(
            map_entity_names_to_legal_entities,
            migrations.RunPython.noop,
        ),
        # Step 3: Remove old entity_name CharField
        migrations.RemoveField(
            model_name='poatracker',
            name='entity_name',
        ),
        # Step 4: Rename entity_ref to entity_name
        migrations.RenameField(
            model_name='poatracker',
            old_name='entity_ref',
            new_name='entity_name',
        ),
        # Step 5: Update the FK field with proper verbose_name and help_text
        migrations.AlterField(
            model_name='poatracker',
            name='entity_name',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='masters.legalentity',
                verbose_name='Name of Entity',
                help_text='Select entity from Legal Entity Master',
            ),
        ),
    ]
