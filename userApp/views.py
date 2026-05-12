from django.http import HttpResponse
from django.shortcuts import render
from app.models import Hotel, Table, MenuCategory, MenuItem, Order, OrderItems

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

    # Fetch active (uncompleted) orders for this table
    bill_items = []
    bill_total = 0
    if table_obj:
        active_orders = Order.objects.filter(hotel=hotel, table=table_obj, completed=False)
        for order in active_orders:
            for oi in order.orderitems.select_related('item').all():
                subtotal = oi.item.price * oi.quantity
                bill_items.append({
                    'name': oi.item.name,
                    'price': oi.item.price,
                    'quantity': oi.quantity,
                    'subtotal': subtotal,
                })
                bill_total += subtotal

    context = {
        'hotel': hotel,
        'table': table_obj,
        'menu': menu,
        'bill_items': bill_items,
        'bill_total': bill_total,
    }
    return render(request, 'usertemplates/menupage.html', context)
