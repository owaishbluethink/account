
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views
from django.conf.urls import url


urlpatterns = [
    path('pages/', include('pages.urls')),
     path('accounts/', include('accounts.urls')),

     path('', admin.site.urls),
     path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
  
]
