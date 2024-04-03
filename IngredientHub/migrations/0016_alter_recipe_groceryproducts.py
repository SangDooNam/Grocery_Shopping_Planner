# Generated by Django 5.0.2 on 2024-03-11 00:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("IngredientHub", "0015_alter_recipe_groceryproducts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="groceryproducts",
            field=models.ManyToManyField(
                blank=True,
                related_name="recipes",
                through="IngredientHub.RecipeIngredient",
                to="IngredientHub.groceryproduct",
            ),
        ),
    ]
