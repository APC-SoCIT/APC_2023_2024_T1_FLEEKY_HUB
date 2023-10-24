from django.shortcuts import redirect, render
from django.core.cache import cache
from django.contrib.auth import logout
# Create your views here.
def dashboard(request):
    active = request.user.fleekyadmin
    return render(request, 'dashboard.html', {'active': active})

def fchub_logout(request):
    logout(request)
    cache.clear()  # Clear the cache for all users
    return redirect('guest:index')