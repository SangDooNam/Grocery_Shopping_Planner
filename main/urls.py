from django.urls import path
from .views import (Home, LogInView, log_out, RegistrationView, 
                    ProfileView, ProfileUpdateView, GetPlan, 
                    CustomizeProduct, PartialSubcategory, partial_display_sub,
                    PartialProduct, partial_display_sub_two)


app_name = 'main'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('login/', LogInView.as_view(), name='login'),
    path('logout/', log_out, name='logout'),
    path('signup/', RegistrationView.as_view(), name='registration'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit/', ProfileUpdateView.as_view(), name='update'),
    path('plan/', GetPlan.as_view(), name='plan'),
    path('customize/', CustomizeProduct.as_view(), name='customize'),
    path('partialsub/', PartialSubcategory.as_view(), name='partialsub'),
    path('partialsub_sec/', partial_display_sub, name='partialsub_sec'),
    path('partialproduct/', PartialProduct.as_view(), name='partialproduct'),
    path('partialsub_third/', partial_display_sub_two, name='partialsub_third'),
]
