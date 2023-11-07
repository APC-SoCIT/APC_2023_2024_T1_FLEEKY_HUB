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
    path('generate-invoice/<int:order_id>/', views.generate_invoice, name='generate-invoice'),
    path('full-details/<int:order_id>/', views.view_full_details, name='full-details'),

    
    
    
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
    path('migrate-csv/<int:csv_id>/', views.migrate_csv, name='migrate-csv'),
    path('get-csv-data/<int:file_id>/', views.get_csv_data, name='get-csv-data'),

    path('successful-orders/', views.successful_orders, name='successful-orders'),
    path('download-successful-orders-csv/', views.download_successful_orders_csv, name='download-successful-orders-csv'),

    path('fchub-data-model', views.view_fchub_model, name='fchub-data-model'),
    path('fchub/migrate-fchub-data/', views.migrate_fchub_data, name='migrate-fchub-data'),
    path('delete-all-data/', views.delete_all_data, name='delete-all-data'),
    path('delete-fabric-data/', views.delete_fabrics_data, name='delete-fabric-data'),
    path('delete-setType-data/', views.delete_setType_data, name='delete-setType-data'),
    path('delete-color-data/', views.delete_color_data, name='delete-color-data'),
    path('delete-location-data/', views.delete_location_data, name='delete-location-data'),





    path('fchub/migrate-fabric-data/', views.migrate_fabric_data, name='migrate-fabric-data'),
    path('migrate-category-data/', views.migrate_category_data, name='migrate-category-data'),
    path('migrate-location-data/', views.migrate_location_data, name='migrate-location-data'),
    path('migrate-color-data/', views.migrate_color_data, name='migrate-color-data'),


    path('sales/', views.sales_for_fabric_list, name='sales-for-fabric-list'),
    path('sales-for-category/', views. SalesForCategoryView.as_view(), name='sales-for-category-list'),
    
    path('sales-for-location/', views.sales_for_location_list, name='sales-for-location'),
    path('sales-for-color/', views.SalesForColorView.as_view(), name='sales-for-color-list'),





]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
