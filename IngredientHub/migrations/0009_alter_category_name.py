# Generated by Django 5.0.2 on 2024-03-07 15:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("IngredientHub", "0008_alter_category_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(
                choices=[
                    ("Eggs and Milk", "Eggs and Milk"),
                    ("Fats and Oils", "Fats and Oils"),
                    ("Fruits", "Fruits"),
                    (
                        "Grains, Nuts, and Baking Products",
                        "Grains, Nuts, and Baking Products",
                    ),
                    ("Herbs and Spices", "Herbs and Spices"),
                    ("Meats", "Meats"),
                    ("Seafoods", "Seafoods"),
                    ("Rice, and Pulses", "Rice, and Pulses"),
                    ("Vegetables", "Vegetables"),
                    ("Processed Foods", "Processed Foods"),
                    ("Fermented Foods", "Fermented Foods"),
                    ("Others", "Others"),
                ],
                max_length=100,
            ),
        ),
    ]
