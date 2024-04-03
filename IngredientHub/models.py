from django.db import models
from main.models import Profile

# Create your models here.

class ValidatedModel(models.Model):
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        
        abstract = True


class Category(ValidatedModel):
    INGREDIENTS_CATEGORIES_CHOICES = [
        ('Eggs and Milk', 'Eggs and Milk'),
        ('Fats and Oils', 'Fats and Oils'),
        ('Fruits', 'Fruits'),
        ('Grains, Nuts, and Baking Products', 'Grains, Nuts, and Baking Products'),
        ('Herbs and Spices', 'Herbs and Spices'),
        ('Meats', 'Meats'),
        ('Seafoods', 'Seafoods'),
        ('Rice, and Pulses', 'Rice, and Pulses'),
        ('Vegetables', 'Vegetables'),
        ('Processed Foods', 'Processed Foods'),
        ('Fermented Foods', 'Fermented Foods'),
        ('Others', 'Others'),
        ]
    name = models.CharField(max_length=100, choices=INGREDIENTS_CATEGORIES_CHOICES)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name',], name='category'),
        ]
    
    def __str__(self):
        return self.name


class Subcategory(ValidatedModel):
    name = models.CharField(max_length=100)
    parent_category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sub_categories')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name',], name='sub_category')
        ]
    def __str__(self):
        return self.name


class GroceryProduct(ValidatedModel):
    name = models.CharField(max_length=100)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ing_categories')
    sub_category_id = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, blank=True, related_name='ing_sub_categories')
    description = models.TextField(null=True, blank=True)
    image_url = models.ImageField(upload_to="images", null=True, blank=True)
    
    def __str__(self):
        return self.name


class Recipe(ValidatedModel):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    groceryproducts = models.ManyToManyField(GroceryProduct, blank=True, through='RecipeIngredient', related_name='recipes')
    duration = models.DurationField(null=True, blank=True)
    image = models.ImageField(upload_to="images", null=True, blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateField(auto_now=True)
    
    def __str__(self):
        return self.title


class RecipeIngredient(ValidatedModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='through_rec')
    ingredient = models.ForeignKey(GroceryProduct, on_delete=models.CASCADE, related_name='through_ing')
    quantity = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.recipe.title



class BreakfastLunchDinner(ValidatedModel):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    breakfast = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True, related_name='breakfast')
    lunch = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True, related_name='lunch')
    dinner = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True, related_name='dinner')
    planned_date = models.DateField(unique=True)
    
    def __str__(self):
        return str(self.planned_date)