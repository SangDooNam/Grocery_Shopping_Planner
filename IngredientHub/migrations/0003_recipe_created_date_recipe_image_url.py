# Generated by Django 5.0.2 on 2024-03-01 22:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("IngredientHub", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="created_date",
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name="recipe",
            name="image_url",
            field=models.ImageField(blank=True, null=True, upload_to="images"),
        ),
    ]
