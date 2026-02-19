# Generated manually for SkillBarterZone project

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20250509_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilemodel',
            name='login_name',
            field=models.CharField(max_length=150, blank=True),
        ),
        migrations.AddField(
            model_name='profilemodel',
            name='full_name',
            field=models.CharField(max_length=150, blank=True),
        ),
        migrations.AddField(
            model_name='profilemodel',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='profilemodel',
            name='gender',
            field=models.CharField(max_length=1, blank=True),
        ),
    ]
