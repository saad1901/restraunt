from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from app.models import MenuItem, MenuCategory, Hotel
from django.views.decorators.csrf import csrf_exempt

def homepage(request):
    popular_items = MenuItem.objects.order_by('?')[:6]
    categories = MenuCategory.objects.all()
    try:
        hotel = Hotel.objects.filter(status=True).first()
    except:
        hotel = None
    context = {
        'popular_items': popular_items,
        'categories': categories,
        'hotel': hotel,
    }
    return render(request, 'frontsite/homepage.html', context)

