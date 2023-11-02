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
    path('update-status/<int:order_id>/', views.update_status, name='update-status'),
    
    
    
    
    path('category/', views.category_list, name='category'),
    path('category/add', views.add_category, name='add-category'),
    path('category/edit/<int:category_id>/', views.edit_category, name='edit-category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete-category'),
    

    path('products/', views.view_product, name='products'),
    path('products/add-products/', views.add_product, name='add-products'),
    path('products/delete-product/<int:pk>', views.delete_product,name='delete-product'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit-product'),
    
    path('materials/', views.view_materials, name='materials'),
    path('materials/edit-material/<int:material_id>/', views.edit_material, name='edit-material'),
    path('materials/delete-material/<int:pk>/', views.delete_material, name='delete-material'),
    path('materials/add-material/', views.add_material, name='add-material'),
    
    path('track-purchase/', views.view_purchase, name='track-purchase'), 
    path('track-purchase/add-purchase/', views.add_purchase, name='add-purchase'),
    path('track-purchase/edit-purchase/<int:purchase_id>/', views.edit_purchase, name='edit-purchase'),
    path('track-purchase/delete-purchase/<int:purchase_id>/', views.delete_purchase, name='delete-purchase'),
    
    
    path('manage-business/', views.view_manage_business, name='manage-business'),
    
    path('manage-business/users-admins', views.users_admins, name='users-admins'),
    path('users/', views.users_admins, name='users-admins'),
    path('list-admins/add-admin/', views.add_admin, name='add-admin'),
    path('list-admins/delete-admin/<int:pk>/', views.delete_admin, name='delete-admin'),

    path('upload-csv', views.upload_csv, name='upload-csv'),
    path('delete-csv/', views.delete_csv, name='delete-csv'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
