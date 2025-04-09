import aut.views as aut
import viewing.views as viewing
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("coin_list/<str:coin_id>/", viewing.coin_detail, name = 'coin_detail' ),
    path("", viewing.home, name = 'home'),
    path("coin_list/", viewing.coin_list, name = 'coin_list'),
    path("register/", aut.register, name = 'registration'),
    path("login/", aut.login, name = 'login'),
]
