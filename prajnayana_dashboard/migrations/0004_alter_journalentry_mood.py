# Generated by Django 4.2.17 on 2025-02-05 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prajnayana_dashboard', '0003_journalentry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalentry',
            name='mood',
            field=models.CharField(choices=[('Happy', 'Happy'), ('Sad', 'Sad'), ('Neutral', 'Neutral'), ('Excited', 'Excited'), ('Stressed', 'Stressed')], default='neutral', max_length=10),
        ),
    ]
