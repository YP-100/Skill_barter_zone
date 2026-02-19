from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Barter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Completed', 'Completed')], default='Pending', max_length=10)),
                ('date_requested', models.DateTimeField(auto_now_add=True)),
                ('date_responded', models.DateTimeField(blank=True, null=True)),
                ('admin', models.ForeignKey(blank=True, help_text='Admin user who manages this barter (optional).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='barters_managed', to=settings.AUTH_USER_MODEL)),
                ('skill_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='barters_from', to='skillzone.skill')),
                ('skill_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='barters_to', to='skillzone.skill')),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='barters_sent', to=settings.AUTH_USER_MODEL)),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='barters_received', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('rating', models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('barter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='skillzone.barter')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
