# Generated by Django 5.0.2 on 2024-03-21 00:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("IngredientHub", "0022_alter_recipeingredient_recipe"),
    ]

    operations = [
        migrations.AlterField(
            model_name="breakfastlunchdinner",
            name="planned_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
