from django.db import migrations, models


def copy_fk_to_m2m(apps, schema_editor):
    """Copy existing team_member_involved FK values to the new M2M field."""
    ValuationReportManagement = apps.get_model("registration", "ValuationReportManagement")
    for report in ValuationReportManagement.objects.all():
        fk_id = report.team_member_involved_id
        if fk_id is not None:
            report.team_members_involved.add(fk_id)


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0016_purchaseorder'),
        ('registration', '0019_poatracker_entity_fk'),
    ]

    operations = [
        # Step 1: Add the M2M field (creates the junction table)
        migrations.AddField(
            model_name='valuationreportmanagement',
            name='team_members_involved',
            field=models.ManyToManyField(
                blank=True,
                help_text='Select multiple team members from User Master',
                to='masters.usermaster',
                verbose_name='Team Members Involved',
            ),
        ),
        # Step 2: Copy existing FK values to the new M2M field
        migrations.RunPython(
            copy_fk_to_m2m,
            migrations.RunPython.noop,
        ),
        # Step 3: Remove the old FK field
        migrations.RemoveField(
            model_name='valuationreportmanagement',
            name='team_member_involved',
        ),
    ]
