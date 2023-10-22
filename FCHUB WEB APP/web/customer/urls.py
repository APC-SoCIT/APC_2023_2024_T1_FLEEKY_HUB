from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
app_name = 'customer'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.customer_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('home/', views.customer_home_view, name='home'),

    path('profile/', views.profile, name='profile'),
    path('profile/edit-profile', views.edit_profile, name='edit-profile'),
    path('my-order', views.my_order_view,name='my-order'),

    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart_view, name='add-to-cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart_view, name='remove-from-cart'),
    path('clear-cart/', views.clear_cart_view, name='clear-cart'),

    path('proceed-purchase/', views.proceed_purchase_view, name='proceed-purchase'),
    path('customers/proceed-purchase/pay-online', views.online_payment_view, name='pay-online'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
