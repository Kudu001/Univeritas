from django.db import migrations


def seed_settings(apps, schema_editor):
    SystemSetting = apps.get_model('core', 'SystemSetting')
    defaults = [
        {
            'key': 'PLAGIARISM_FLAG_THRESHOLD',
            'value': '0.40',
            'description': 'Similarity score (0.0–1.0) above which a submission is automatically flagged.',
        },
        {
            'key': 'PLAGIARISM_SIMILARITY_SCOPE',
            'value': 'DEAN_APPROVED,PUBLISHED',
            'description': 'Submission statuses included in the plagiarism comparison archive.',
        },
    ]
    for setting in defaults:
        SystemSetting.objects.get_or_create(key=setting['key'], defaults=setting)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_settings, migrations.RunPython.noop),
    ]
