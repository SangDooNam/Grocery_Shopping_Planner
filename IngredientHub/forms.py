from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import (Recipe, GroceryProduct, RecipeIngredient, Subcategory, Category, BreakfastLunchDinner)


class RecipeForm(forms.ModelForm):
    
    class Meta:
        model = Recipe
        exclude = ['user', 'groceryproducts', 'duration']
    
    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)


class GroceryProductForm(forms.ModelForm):
    
    class Meta:
        model = GroceryProduct
        fields = ['name', 'category_id', 'sub_category_id', 'description', 'image_url' ]


class CategoryForm(forms.ModelForm):
    
    class Meta:
        model = Category
        fields = ['name']


class SubcategoryForm(forms.ModelForm):
    
    class Meta:
        model = Subcategory
        fields = ['name', 'parent_category_id']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter subcategory name'}),
            
        }
    def __init__(self, *args, **kwargs) -> None:
        super(SubcategoryForm, self).__init__(*args, **kwargs)
        self.fields['parent_category_id'].choices = [('', 'Select a category')] + list(self.fields['parent_category_id'].choices)[1:]
        
class RecipeIngredientForm(forms.ModelForm):
    
    class Meta:
        model = RecipeIngredient
        fields = ['quantity','unit']

class BreakfastLunchDinnerForm(forms.ModelForm):
    
    class Meta:
        model = BreakfastLunchDinner
        exclude = ['user', 'planned_date']
    
    