from django.db.models.base import Model as Model
from django.db.models.query import QuerySet, Q
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.views.generic import TemplateView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from IngredientHub.models import Recipe, BreakfastLunchDinner, Category, Subcategory, GroceryProduct
from IngredientHub.forms import SubcategoryForm, GroceryProductForm
from typing import Any
from .forms import RegistrationForm, ProfileForm
from .models import Profile
from calendar import HTMLCalendar
from datetime import datetime, timedelta
import calendar
import re


# Create your views here.

class Home(TemplateView):
    template_name = 'main/home.html'
    
    def replace_day(self, base_url, day):
        day_url = f'{base_url}?day={day}'
        return f"<a href='{day_url}'>{day}</a>"

    def replace_cur_cal(self, base_url, day):
        
        today = datetime.today().day
        if int(day) >= today:
            day_url = f'{base_url}?day={day}'
            return f"<a href='{day_url}'>{day}</a>"
        else:
            return f'{day}'
    
    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        greeting = 'Hello.'
        if self.request.user.is_authenticated:
            greeting = f'Hello, {self.request.user.username}'
        
        context = super().get_context_data(**kwargs)

        today = datetime.today()
        
        next_month = (today.month % 12) + 1
        next_next_month = (next_month % 12) + 1
        next_year = today.year  + (today.month // 12)
        next_next_year = next_year + (next_month // 12)
        
        month_name = list(calendar.month_name)[today.month]
        next_month_name = list(calendar.month_name)[next_month]
        next_next_month_name = list(calendar.month_name)[next_next_month]
        
        cur_cal = HTMLCalendar().formatmonth(today.year, today.month)
        next_cal = HTMLCalendar().formatmonth(next_year, next_month)
        next_next_cal = HTMLCalendar().formatmonth(next_year, next_next_month)
        
        cur_url = reverse('IngredientHub:select_or_create', kwargs={'year':today.year, 'month_name': month_name})
        next_url = reverse('IngredientHub:select_or_create', kwargs={'year':next_year, 'month_name': next_month_name})
        next_next_url = reverse('IngredientHub:select_or_create', kwargs={'year':next_next_year, 'month_name': next_next_month_name})
        
        cur_cal = re.sub(r'(?<=>)\d+(?=<)', lambda match : self.replace_cur_cal(cur_url, match.group(0)), cur_cal)
        next_cal = re.sub(r'(?<=>)\d+(?=<)', lambda match : self.replace_day(next_url, match.group(0)), next_cal)
        next_next_cal = re.sub(r'(?<=>)\d+(?=<)', lambda match : self.replace_day(next_next_url, match.group(0)), next_next_cal)
        
        context['today_is'] = 'Today is' + ' ' +  today.strftime('%Y-%m-%d')
        context['greeting'] = greeting
        context['cur_cal'] = cur_cal
        context['next_cal'] = next_cal
        context['next_next_cal'] = next_next_cal
        
        return context


class LogInView(LoginView):
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    template_name = 'main/login.html'
    
    def get_success_url(self) -> str:
        return reverse_lazy('main:home')
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        
        return super().dispatch(request, *args, **kwargs)


class RegistrationView(FormView):
    template_name = 'main/registration.html'
    success_url = reverse_lazy('main:home')
    form_class = RegistrationForm
    
    def form_valid(self, form: Any) -> HttpResponse:
        form.save()
        return super().form_valid(form)


def log_out(request):
    logout(request)
    return redirect(reverse('main:home'))


class ProfileView(DetailView):
    model = Profile
    template_name = 'main/profile.html'
    context_object_name = 'profile'
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:
        self.rec_id = self.request.GET.get('rec_id')

        if self.request.method == 'DELETE':
            return self.delete()
        
        if self.request.method == 'POST':
            return self.post(request=request)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        try:
            if self.request.user.is_authenticated:
                return self.request.user
        except self.request.user.DoesNotExist as error:
            raise error
            
    
    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        today = datetime.today()
        end_date = today + timedelta(days=7)
        
        meal_plans = BreakfastLunchDinner.objects.filter(user=user, planned_date__gte=today, planned_date__lte=end_date)
        
        all_products = {}
        
        for plan in meal_plans:
            if plan.breakfast:
                for product in plan.breakfast.groceryproducts.all():
                    all_products[product.name] = all_products.get(product.name, 0) + 1
            if plan.lunch:
                for product in plan.lunch.groceryproducts.all():
                    all_products[product.name] = all_products.get(product.name, 0) + 1
            if plan.dinner:
                for product in plan.dinner.groceryproducts.all():
                    all_products[product.name] = all_products.get(product.name, 0) + 1
                
        
        recipes = Recipe.objects.filter(user=self.request.user)
        
        
        context['recipes'] = recipes
        context['meal_plans'] = meal_plans
        context['all_products'] = all_products
        
        return context
    
    def delete(self): 
        if self.rec_id:
            try:
                recipe_to_delete = Recipe.objects.get(id=self.rec_id)
                bld_objs = BreakfastLunchDinner.objects.filter(Q(breakfast=recipe_to_delete) | Q(lunch=recipe_to_delete) | Q(dinner=recipe_to_delete))
                
                for bld_obj in bld_objs:
                    updated = False
                    if bld_obj.breakfast == recipe_to_delete:
                        bld_obj.breakfast = None
                        updated = True
                    if bld_obj.lunch == recipe_to_delete:
                        bld_obj.lunch = None
                        updated = True
                    if bld_obj.dinner == recipe_to_delete:
                        bld_obj.dinner = None
                        updated = True
                        
                    if bld_obj.breakfast is None and bld_obj.lunch is None and bld_obj.dinner is None:
                        
                        bld_obj.delete()
                    
                    if updated and (bld_obj.breakfast is not None or bld_obj.lunch is not None or bld_obj.dinner is not None):
                        bld_obj.save()
                recipe_to_delete.delete()
                user = self.request.user
                today = datetime.today()
                end_date = today + timedelta(days=7)
                
                meal_plans = BreakfastLunchDinner.objects.filter(user=user, planned_date__gte=today, planned_date__lte=end_date)
                
                all_products = {}
                for plan in meal_plans:
                    if plan.breakfast:
                        for product in plan.breakfast.groceryproducts.all():
                            all_products[product.name] = all_products.get(product.name, 0) + 1
                    if plan.lunch:
                        for product in plan.lunch.groceryproducts.all():
                            all_products[product.name] = all_products.get(product.name, 0) + 1
                    if plan.dinner:
                        for product in plan.dinner.groceryproducts.all():
                            all_products[product.name] = all_products.get(product.name, 0) + 1
                
                recipes = Recipe.objects.filter(user=self.request.user)
                
                context = {
                    'profile': user,
                    'recipes': recipes,
                    'meal_plans' : meal_plans,
                    'all_products' : all_products,
                }
                return render(self.request, "main/profile.html", context)
            
            except recipe_to_delete.DoesNotExist:
                raise JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)

class ProfileUpdateView(UpdateView):
    form_class = ProfileForm
    template_name = "main/edit_profile.html"
    success_url = reverse_lazy('main:profile')
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.user
    
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            return super().form_valid(form)
        else:
            return super().form_invalid(form)
        

class GetPlan(TemplateView):
    
    template_name = "partials/display_plan.html"
    
    def post(self, request, *args, **kwargs):
        days_form_today = self.request.POST.get('days_from_today')
        user = self.request.user
        today = datetime.today()
        end_date = today + timedelta(days=int(days_form_today))
        
        meal_plans = BreakfastLunchDinner.objects.filter(user=user, planned_date__gte=today, planned_date__lte=end_date).order_by('planned_date')
        
        all_products = {}
        
        for plan in meal_plans:
            if plan.breakfast:
                for product in plan.breakfast.groceryproducts.all():
                    all_products[product.name] = all_products.get(product.name, 0) + 1
            if plan.lunch:
                for product in plan.lunch.groceryproducts.all():
                    all_products[product.name] = all_products.get(product.name, 0) + 1
            if plan.dinner:
                for product in plan.dinner.groceryproducts.all():
                    all_products[product.name] = all_products.get(product.name, 0) + 1
        
        context = {
            'meal_plans' : meal_plans,
            'all_products' : all_products,
        }
        
        return render(request, 'partials/display_plan.html', context )



class CustomizeProduct(FormView):
    form_class = SubcategoryForm
    template_name = 'main/customize_product.html'
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:
        
        if request.method == 'POST':
            return self.post(request=request)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        
        context = super().get_context_data(**kwargs)
        
        product_form = GroceryProductForm()
        
        context['category'] = Category.objects.all()
        context['sub_category'] = Subcategory.objects.all()
        context['product_form'] = product_form
        
        return context
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'delete_category':
            
            cat_id = request.POST.get('selected_category')
            delete_category = get_object_or_404(Category, id=cat_id)
            # delete_category.delete()
            return redirect('main:customize')
        
        elif action == 'add_product':
            
            name = request.POST.get('name')
            category_id = request.POST.get('select_category_third')
            subcategory_id = request.POST.get('selected_subcategory')
            description = request.POST.get('selected_subcategory')
            
            category = Category.objects.get(id=category_id)
            subcategory = Subcategory.objects.get(id=subcategory_id)
            
            # product = GroceryProduct.objects.create(
            #     name=name,
            #     category_id = category,
            #     sub_category_id = subcategory,
            #     description = description,
            # )
            print('OK')
            return redirect('main:customize')
        else:
            form = SubcategoryForm(request.POST)
            if form.is_valid():
                #form.save()
                return redirect('main:customize')
            else:
                return HttpResponse("failed to be added")
    
    

class PartialSubcategory(TemplateView):
    template_name = 'partials/subcategory.html'
    
    def dispatch(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:
        self.selected_category_id = self.request.GET.get('select_category')
        
        if request.method == 'POST':
            return self.post(request=request)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        selected_sub = Subcategory.objects.filter(parent_category_id=self.selected_category_id)
        
        context['selected_subcategories'] = selected_sub
        
        return context
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        
        if action == 'delete_subcategory':
            
            sub_id = request.POST.get('select_subcategory')
            delete_sub = get_object_or_404(Subcategory, id=sub_id)
            # delete_sub.delete()
        
        return redirect('main:customize')
    
def partial_display_sub(request):
    
    if request.method == 'GET':
        
        selected_category_id = request.GET.get('select_category_second')
        request.session['select_category_second'] = selected_category_id
        selected_sub = Subcategory.objects.filter(parent_category_id=selected_category_id)
        
        context = {
            'selected_subcategories_sec' : selected_sub
        }
        return render(request, 'partials/subcategory_second.html', context)


def partial_display_sub_two(request):
    
    if request.method == 'GET':
        
        selected_category_id = request.GET.get('select_category_third')
        request.session['select_category_third'] = selected_category_id
        selected_sub = Subcategory.objects.filter(parent_category_id=selected_category_id)
        
        context = {
            'selected_subcategories_third' : selected_sub
        }
        return render(request, 'partials/subcategory_third.html', context)


class PartialProduct(TemplateView):
    template_name = "partials/product.html"
    
    def dispatch(self, request, *args, **kwargs):
        self.selected_sub = request.GET.get('select_subcategory')
        self.selected_cat_id = request.session.get('select_category_second')
        
        if request.method == 'POST':
            return self.post(request=request)
        
        return super().dispatch(request, *args, **kwargs)
    
    
    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        
        selected_products = GroceryProduct.objects.filter(category_id=self.selected_cat_id, sub_category_id=self.selected_sub)
        
        context['selected_products'] = selected_products
        
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        
        if action == 'delete_product':
            
            product_id = request.POST.get('select_product')
            product_to_delete = GroceryProduct.objects.get(id=product_id)
            # product_to_delete.delete()
        
        return redirect('main:customize')

# class AddSubcategory(FormView):
#     form_class = SubcategoryForm
#     template_name = 'main/add_sub.html'
#     success_url = reverse_lazy('main:customize')
    
#     def form_valid(self, form):
#         form.save()
#         return super().form_valid(form)
    