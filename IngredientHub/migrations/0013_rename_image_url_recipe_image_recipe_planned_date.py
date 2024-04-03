# Generated by Django 5.0.2 on 2024-03-09 14:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("IngredientHub", "0012_rename_ingredients_recipe_groceryproducts_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="recipe",
            old_name="image_url",
            new_name="image",
        ),
        migrations.AddField(
            model_name="recipe",
            name="planned_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
