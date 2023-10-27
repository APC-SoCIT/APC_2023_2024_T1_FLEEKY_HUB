from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
app_name = 'fchub'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.fchub_logout, name='logout'),


    path('customers/', views.view_customer, name='customers'),
    path('orders/', views.view_order, name='orders'),

    path('products/', views.view_product, name='products'),
    path('products/add-products/', views.add_product, name='add-products'),
    path('products/delete-product/<int:pk>', views.delete_product,name='delete-product'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit-product'),
    
    
    path('materials/', views.view_materials, name='materials'),

    path('manage-business/', views.view_manage_business, name='manage-business'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
