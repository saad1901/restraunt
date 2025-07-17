from django.http import HttpResponse
from django.shortcuts import render
from app.models import Hotel, Table, MenuCategory, MenuItem

def show_menu(request, hotel, table=None):
    hotel = Hotel.objects.get(id=hotel)
    categories = MenuCategory.objects.filter(hotel=hotel).prefetch_related('menuitem_set')
    table_obj = None
    if table is not None:
        try:
            table_obj = Table.objects.get(id=table, hotel=hotel)
        except Table.DoesNotExist:
            table_obj = None
    menu = []
    for category in categories:
        items = category.menuitem_set.all()
        menu.append({
            'name': category.name,
            'icon': category.icon,
            'items': items
        })

    context = {
        'hotel': hotel,
        'table': table_obj,
        'menu': menu
    }
    return render(request, 'usertemplates/menupage.html', context)
