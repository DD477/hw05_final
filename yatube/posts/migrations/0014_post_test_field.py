# Generated by Django 2.2.16 on 2022-02-22 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20211127_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='test_field',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
