# Generated by Django 5.0.2 on 2024-03-12 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="photo",
            field=models.ImageField(
                default="static/img/default.jpg", upload_to="profile_photo"
            ),
        ),
    ]
