from django.db.models.base import Model as Model
from django.db.models.query import QuerySet, Q
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.http import JsonResponse, Http404


from .forms import (RecipeForm, Subcategory, BreakfastLunchDinnerForm)
from .models import (Subcategory, Category, GroceryProduct, Recipe, BreakfastLunchDinner, RecipeIngredient)
from typing import Any
from datetime import datetime, timedelta

# Create your views here.

class SelectOrCreate(TemplateView):
    template_name='IngredientHub/select_or_create.html'
    year = None
    month_name = None
    day = None
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:
        self.year = kwargs.get('year')
        self.month_name = kwargs.get('month_name')
        self.day = self.request.GET.get('day')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['year'] = self.year
        context['month_name'] = self.month_name
        context['day'] = self.day
        
        return context


class SelectRecipe(UpdateView):
    template_name= 'IngredientHub/select_recipe.html'
    form_class = BreakfastLunchDinnerForm
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:
        
        self.year = kwargs.get('year')
        self.month_name = kwargs.get('month_name')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.day = self.request.GET.get('day')
        if self.day and self.year and self.month_name:
            try:
                planned_date = datetime.strptime(f'{self.year}-{self.month_name}-{self.day}', "%Y-%B-%d").date()
                self.request.session['planned_date'] = str(planned_date)
            except ValueError:
                pass
        
        if self.request.user.is_authenticated:
            try:
                self.selected_recipes = get_object_or_404(BreakfastLunchDinner, planned_date=planned_date)
            except Http404:
                self.selected_recipes = None
        else:
            self.selected_recipes = None
        
        context['year'] = self.year
        context['month_name'] = self.month_name
        context['day'] = self.day
        context['selected_recipes'] = self.selected_recipes
        context['planned_date'] = planned_date
        
        return context
    
    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        
        initial['breakfast'] = None
        initial['lunch'] = None
        initial['dinner'] = None
        return initial
    
    
    def get_object(self, queryset=None):
        """Get the object to be updated."""
        planned_date = self.request.session.get('planned_date')
        if planned_date:
            planned_date = datetime.strptime(planned_date, "%Y-%m-%d").date()
            return BreakfastLunchDinner.objects.filter(user=self.request.user, planned_date=planned_date).first()
        return None
        
    def form_valid(self, form):
        """Handle valid form submission."""
        if self.request.user.is_authenticated:
            planned_date_str = self.request.session.get('planned_date')
            if planned_date_str:
                planned_date = datetime.strptime(planned_date_str, "%Y-%m-%d").date()
                bld_obj = self.get_object()
                if bld_obj:
                    # Existing object, update it
                    print(form.changed_data)
                    if 'breakfast' in form.cleaned_data:
                        bld_obj.breakfast = form.cleaned_data.get('breakfast')
                    if 'lunch' in form.cleaned_data:
                        bld_obj.lunch = form.cleaned_data.get('lunch')
                    if 'dinner' in form.cleaned_data:
                        bld_obj.dinner = form.cleaned_data.get('dinner')

                    bld_obj.planned_date = planned_date  # Explicitly set the planned_date
                    bld_obj.user = self.request.user  # Explicitly set the user
                    bld_obj.save()
                else:
                    # Create a new object
                    planned_date = self.request.session.get('planned_date')
                    if planned_date:
                        planned_date = datetime.strptime(planned_date, "%Y-%m-%d").date()
                        BreakfastLunchDinner.objects.create(
                            user=self.request.user,
                            planned_date=planned_date,
                            breakfast=form.cleaned_data.get('breakfast'),
                            lunch=form.cleaned_data.get('lunch'),
                            dinner=form.cleaned_data.get('dinner'),
                        )
            return HttpResponse(f"added sucessfully")
        return super().form_invalid(form)

class CreateRecipe(CreateView):
    template_name = 'IngredientHub/create_recipe.html'
    form_class = RecipeForm
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:
        response = super().dispatch(request, *args, **kwargs)
        
        self.year = kwargs.get('year')
        self.month_name = kwargs.get('month_name')
        self.day = self.request.GET.get('day')
        
        return response

    def get(self, request, *args, **kwargs):
        self.year = kwargs.get('year')
        self.month_name = kwargs.get('month_name')
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.day = self.request.GET.get('day')
        selected_meal_module = self.request.GET.get('Create_recipe')
        self.request.session['selected_meal_module'] = selected_meal_module
        

        context['categories'] = Category.objects.all().order_by('name')
        context['year'] = self.year
        context['month_name'] = self.month_name
        context['day'] = self.day
        context['selected_meal_module'] = selected_meal_module
        
        planned_date = datetime.strptime(f"{self.year}-{self.month_name}-{self.day}", "%Y-%B-%d").date()
        
        self.request.session['planned_date'] = str(planned_date)
        
        return context
    
    def get_success_url(self):
        return reverse('IngredientHub:select_or_create', kwargs={'year':self.year, 'month_name':self.month_name}) + f"{self.day}"


    def form_valid(self, form, *args, **kwargs):
        product_ids = self.request.session['selected_products_ids']
        
        if self.request.user.is_authenticated and product_ids is not None:
            planned_date = self.request.session['planned_date']
            planned_date = datetime.strptime(planned_date, "%Y-%m-%d").date()
            recipe = form.save(commit=False)
            form.instance.user = self.request.user
            recipe.save()
            
            recipe.groceryproducts.set(product_ids)
            
            if self.request.session['selected_meal_module'] == 'breakfast':
                bld_default ={
                    'breakfast': recipe,
                }
            elif self.request.session['selected_meal_module'] == 'lunch':
                bld_default ={
                    'lunch': recipe,
                }
            elif self.request.session['selected_meal_module'] == 'dinner':
                bld_default ={
                    'dinner': recipe,
                }
                
            breakfast_lunch_dinner, created = BreakfastLunchDinner.objects.update_or_create(user=self.request.user, planned_date=planned_date, defaults=bld_default)
            
            for id in product_ids:
                product = GroceryProduct.objects.get(id=id)
                recipeingredient, created = RecipeIngredient.objects.update_or_create(recipe=recipe, ingredient=product)
                recipeingredient.save()
            
            breakfast_lunch_dinner.save()
            form.save_m2m()
            del self.request.session['selected_products_ids']
            return HttpResponse(f"{self.request.session['selected_meal_module'].capitalize()} added sucessfully")
        else:
            return HttpResponse(f"{self.request.session['selected_meal_module'].capitalize()} failed to be added")


class AddProduct(TemplateView):
    
    
    template_name= 'partials/added_products_list.html'
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:
        if request.method == 'DELETE':
            return self.handle_delete(request, *args, **kwargs)
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        year = kwargs.get('year')
        month_name = kwargs.get('month_name')
        day = request.GET.get('day')
        cat_id = request.GET.get('cat_id')
        sub_id = request.GET.get('sub_id')
        ing_id = request.GET.get('ing_id')
        selected_meal_module = self.request.session.get('selected_meal_module')
        selected_products_ids = self.request.session.get('selected_products_ids', list())
        
        if ing_id:
            if ing_id not in selected_products_ids:
                selected_products_ids.append(ing_id)
            self.request.session['selected_products_ids'] = selected_products_ids
            container = GroceryProduct.objects.filter(id__in=selected_products_ids)
        
        context = {
            'year' : year,
            'month_name' : month_name,
            'day' : day,
            'cat_id' : cat_id,
            'sub_id' : sub_id,
            'ing_id' : ing_id,
            'container' : container,
            'selected_meal_module' : selected_meal_module,
        }

        return render(request, 'partials/added_products_list.html', context)
    
    def handle_delete(self, request, *args, **kwargs):
        
        del_id = self.request.GET.get('del_id')
        selected_product_ids = set(self.request.session.get('selected_products_ids', []))
        
        if del_id and del_id in selected_product_ids:
            try:
                selected_product_ids.remove(del_id)
                self.request.session['selected_products_ids'] = list(selected_product_ids)    

                return JsonResponse({'status': 'sucess'})
            except:
                return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
        return JsonResponse({'status': 'error', 'message': 'No item specified'}, status=400)



class SelectCategory(TemplateView):
    
    template_name = 'partials/select_cat.html'
    
    def get(self, request, *args, **kwargs):
        year = kwargs.get('year')
        month_name = kwargs.get('month_name')
        day =  self.request.GET.get('day')
        cat_id = self.request.GET.get('cat_id')
        sub_id = self.request.GET.get('sub_id')
        selected_meal_module = self.request.session['selected_meal_module']
        subcategories = Subcategory.objects.filter(parent_category_id=cat_id).order_by('name')
        
        context = {
            'year' : year,
            'month_name' : month_name,
            'day' : day,
            'cat_id' : cat_id,
            'sub_id' : sub_id,
            'subcategories' : subcategories,
            'selected_meal_module' : selected_meal_module,
        }
        
        return render(request, 'partials/select_cat.html', context)


class SelectSub(TemplateView):
    
    template_name = 'partials/select_sub.html'
    
    def get(self, request, *args, **kwargs):
        
        year = kwargs.get('year')
        month_name = kwargs.get('month_name')
        day = self.request.GET.get('day')
        cat_id = self.request.GET.get('cat_id')
        sub_id = self.request.GET.get('sub_id')
        ing_id = self.request.GET.get('ing_id')
        selected_meal_module = self.request.session['selected_meal_module']
        products = GroceryProduct.objects.filter(category_id=cat_id, sub_category_id=sub_id).order_by('name')
        
        context = {
            'year': year,
            'month_name': month_name,
            'day': day,
            'cat_id': cat_id,
            'sub_id': sub_id,
            'ing_id': ing_id,
            'groceryproduct': products,
            'selected_meal_module' : selected_meal_module,
        }
        
        return render(request, 'partials/select_sub.html', context)


class Search(TemplateView):
    
    template_name = 'partials/search_display.html'
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:
        if kwargs.get('year') and kwargs.get('month_name'):
            return self.post(request, *args, **kwargs)
        
        else:
            return self.post_edit(request,*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        
        year = kwargs.get('year')
        month_name = kwargs.get('month_name')
        day = self.request.GET.get('day')
        search_term = self.request.POST.get('productname')
        results = GroceryProduct.objects.filter(name__icontains=search_term)
        
        context = {
            'year' : year,
            'month_name': month_name,
            'day' : day,
            'search_term': search_term,
            'results': results
        }
        
        return render(request, 'partials/search_display.html', context )
    
    def post_edit(self, request, *args, **kwargs):
        rec_id = self.request.session['rec_id']
        
        search_term = self.request.POST.get('productname')
        results = GroceryProduct.objects.filter(name__icontains=search_term)
        context = {
            'rec_id' : rec_id,
            'search_term': search_term,
            'results': results,
        }
        return render(request, 'partials/search_display_at_edit.html', context )


class RecipeUpdate(UpdateView):
    
    template_name = "IngredientHub/update_recipe.html"
    form_class = RecipeForm
    context_object_name = "recipe"
    success_url = reverse_lazy('main:profile')
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:

        self.del_id = self.request.GET.get('del_id')
        if request.method == 'DELETE':
            return self.delete(*args, **kwargs)
        
        elif request.method == 'PUT' and request.headers['Hx-Request'] == 'true':
            return self.hx_put(*args, **kwargs)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request: HttpRequest, *args: str, **kwargs: reverse_lazy) -> HttpResponse:
        self.id = kwargs.get('rec_id')
        self.request.session['rec_id'] = self.id
                
        return super().get(request, *args, **kwargs)
    
    def get_object(self, queryset: QuerySet[Any] | None = ..., *args, **kwargs) -> Model:
        self.id = self.request.session['rec_id']
        self.object = Recipe.objects.get(id=self.id)
        return self.object
    
    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        ingredients = RecipeIngredient.objects.filter(recipe=self.object)
        ingredients = [recipe.ingredient for recipe in ingredients]
        
        categories = Category.objects.all().order_by('name')
        
        context['categories'] = categories
        context['rec_id'] = self.id
        context['ingredients'] = ingredients
        
        return context
        
    def delete(self, rec_id): 
        
        try:
            recipe_ingredient = RecipeIngredient.objects.get(recipe_id=rec_id, ingredient_id=self.del_id)
            recipe_ingredient.delete()
            return HttpResponse('deleted')
        except GroceryProduct.DoesNotExist:
            raise JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
    
    def hx_put(self, *args, **kwargs):
        
        try:
            product_id = self.request.GET.get('product_id')
            obj = self.get_object(*args, **kwargs)
            ingredient_to_add = GroceryProduct.objects.get(id=product_id)
            RecipeIngredient.objects.update_or_create(recipe=obj, ingredient=ingredient_to_add)
            ingredients = RecipeIngredient.objects.filter(recipe=obj)
            ingredients = [recipe.ingredient for recipe in ingredients]
            
            context = {
                'ingredients' : ingredients,
                'rec_id' : self.request.session['rec_id'],
            }
            return render(self.request, 'partials/display_selected_at_edit.html', context)
        
        except (GroceryProduct.DoesNotExist, RecipeIngredient.DoesNotExist) as error:
            raise error
    
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            
            form.save()
            return super().form_valid(form)
        else:
            return super().form_invalid(form)


class SubCatEdit(TemplateView):
    
    template_name = 'partials/display_subcat_at_edit.html'
    
    def get(self, request, *args, **kwargs):
        cat_id = kwargs.get('cat_id')
        
        sub_categories = Subcategory.objects.filter(parent_category_id_id = cat_id)
        context = {
            'cat_id': cat_id,
            'sub_categories' : sub_categories,
        }
        return render(self.request, 'partials/display_subcat_at_edit.html', context)


class ProductEdit(TemplateView):
    
    template_name = "partials/display_products_at_edit.html"
    
    def get(self, request, *args, **kwargs):
        cat_id = kwargs.get('cat_id')
        rec_id = request.session['rec_id']
        sub_id = self.request.GET.get('sub_id')
        
        groceryproducts = GroceryProduct.objects.filter(category_id=cat_id, sub_category_id=sub_id)
        context = {
            'rec_id': rec_id,
            'groceryproducts': groceryproducts,
        }
        return render(self.request, "partials/display_products_at_edit.html", context)

