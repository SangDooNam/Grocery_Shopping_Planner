from django.urls import path
from .views import (CreateRecipe, AddProduct, SelectCategory, 
                    SelectSub, Search, SelectOrCreate, SelectRecipe, 
                    RecipeUpdate, SubCatEdit, ProductEdit)

app_name = 'IngredientHub'

urlpatterns = [
    path('recipe/<int:year>/<str:month_name>/', CreateRecipe.as_view(), name='recipe'),
    path('add/<int:year>/<str:month_name>/', AddProduct.as_view(), name='add'),
    path('cat/<int:year>/<str:month_name>/', SelectCategory.as_view(), name='cat'),
    path('sub/<int:year>/<str:month_name>/', SelectSub.as_view(), name='sub'),
    path('search/<int:year>/<str:month_name>/', Search.as_view(), name='search'),
    path('select/<int:year>/<str:month_name>/', SelectRecipe.as_view(), name='select'),
    path('<int:year>/<str:month_name>/', SelectOrCreate.as_view(), name='select_or_create'),
    path('update/<int:rec_id>/', RecipeUpdate.as_view(), name='update_recipe'),
    path('sub_edit/<int:cat_id>', SubCatEdit.as_view(), name='sub_edit'),
    path('products_edit/<int:cat_id>', ProductEdit.as_view(), name='products_edit'),
    path('search_edit/', Search.as_view(), name='search_edit'),
]
