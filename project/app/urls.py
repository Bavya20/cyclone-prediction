from django.urls import path 
from app import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('home', views.home, name='home'),
    path('view_dataset', views.view_dataset, name='view_dataset'),
    path('model_train', views.model_train, name='model_train'),
    path('prediction', views.prediction, name='prediction'),
    path('logout', views.view_logout, name='logout'),
]