# Generated by Django 4.2.17 on 2025-04-17 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prajnayana_dashboard', '0008_article'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='knowledgehub',
            name='category',
        ),
        migrations.AlterField(
            model_name='knowledgehub',
            name='title',
            field=models.CharField(choices=[('Mindfulness Techniques', 'Mindfulness Techniques'), ('Emotional Resilience', 'Emotional Resilience'), ('Self-Awareness', 'Self Awareness'), ('Personal Growth', 'Personal Growth'), ('Community Stories', 'Community Stories')], max_length=255),
        ),
    ]
