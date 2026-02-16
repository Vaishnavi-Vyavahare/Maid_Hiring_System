from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('switch-language/', views.switch_language, name='set_language'),
    path('register/', views.register_view, name='register'),
    path('register-maid/', views.register_maid, name='register_maid'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin Module URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('portal-admin/users/<str:category>/', views.admin_user_list, name='admin_user_list'),
    path('portal-admin/profile/<int:user_id>/', views.admin_user_profile, name='admin_user_profile'),
    path('portal-admin/maid-detail/<int:maid_id>/', views.admin_maid_detail, name='admin_maid_detail'),
    path('portal-admin/approve/<int:maid_id>/', views.approve_maid, name='approve_maid'),
    path('portal-admin/reject/<int:maid_id>/', views.reject_maid, name='reject_maid'),
    path('portal-admin/formal-reject-email/<int:maid_id>/', views.admin_send_formal_rejection_email, name='admin_send_formal_rejection_email'),
    
    # User Feature URLs
    path('maids/', views.maid_list_view, name='maid_list'),
    path('maid-profile/<int:maid_id>/', views.customer_maid_profile, name='customer_maid_profile'),
    path('send-email/<int:maid_id>/', views.send_email_to_maid, name='send_email_to_maid'),
]
