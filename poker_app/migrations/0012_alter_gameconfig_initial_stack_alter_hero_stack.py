# Generated by Django 5.0.3 on 2024-07-01 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poker_app', '0011_alter_gameconfig_initial_stack_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameconfig',
            name='initial_stack',
            field=models.IntegerField(default=300),
        ),
        migrations.AlterField(
            model_name='hero',
            name='stack',
            field=models.IntegerField(default=400),
        ),
    ]
