# Generated by Django 5.0.2 on 2024-03-12 14:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_alter_profile_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="photo",
            field=models.ImageField(
                default="img/default.jpg", upload_to="profile_photo"
            ),
        ),
    ]
