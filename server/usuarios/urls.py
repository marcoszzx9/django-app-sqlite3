from django.urls import path
from . import views

urlpatterns = [
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('signup/', views.signup_view, name='signup'),
    path('verify_email/', views.verify_email_view, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.init_view, name='dashboard'),
    path('add_reminder/', views.add_reminder, name='add_reminder'),
    path('edit_reminder/<int:pk>/', views.edit_reminder, name='edit_reminder'),
    path('delete_reminder/<int:pk>/', views.delete_reminder, name='delete_reminder'),
    path('account/', views.account_view, name='account'),
]
