from django.urls import path ,include  

from . import views 

urlpatterns = [
    path('Account/',include('accounts.urls')),
    path('login',views.login,name="login"),
    path('register',views.register,name="register"),     

]