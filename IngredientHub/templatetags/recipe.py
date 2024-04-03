from django import template
# from models import Recipe, Ingredient, Category, Subcategory, RecipeIngredient



register = template.Library()


@register.filter(name='chunks')
def chunks(value, chunk_length):
    for i in range(0, len(value), chunk_length):
        yield value[i:i+ chunk_length]

