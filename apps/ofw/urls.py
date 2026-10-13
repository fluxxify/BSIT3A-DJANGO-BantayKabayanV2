from django.urls import path

from . import crud, views

app_name = 'ofw'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('m/<slug:module>/', crud.module_list, name='module_list'),
    path('m/<slug:module>/ajax/get/<int:pk>/', crud.module_get_ajax, name='module_get_ajax'),
    path('m/<slug:module>/ajax/save/', crud.module_save_ajax, name='module_save_ajax'),
    path('m/<slug:module>/ajax/delete/<int:pk>/', crud.module_delete_ajax, name='module_delete_ajax'),
]
