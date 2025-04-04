from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from .models import Warning

def dashboard(request):
    warnings = Warning.objects.all().order_by('-timestamp') 
    print(warnings)
    return render(request, 'monitor/dashboard.html', {'warnings': warnings})
