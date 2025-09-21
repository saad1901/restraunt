from django.shortcuts import render
from django.http import JsonResponse
from app.models import *
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request): 
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    if not hotel.status:
        agent_cell = hotel.agent.phone if hotel.agent else "NOAGENT"
        agent_name = hotel.agent.first_name if hotel.agent else "NOAGENT"
        return render(request, 'auth/notallowed.html', {'agent_cell':agent_cell, 'agent_name':agent_name})
    tables = Table.objects.filter(hotel=request.user.staffof).order_by('name')
    categories = MenuCategory.objects.filter(hotel=request.user.staffof)
    items = MenuItem.objects.filter(hotel=request.user.staffof)
    return render(request, 'staff/waiter.html',{'hotel':hotel,'tables':tables , 'categories':categories, 'items':items})

@login_required
def waiter_active_orders(request):
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    orders = Order.objects.filter(completed=False, hotel=hotel).order_by('-created_at')
    orders_data = []
    for order in orders:
        items_data = []
        for item in order.orderitems.all():
            items_data.append({
                'name': item.item.name,
                'quantity': item.quantity,
                'price': float(item.item.price)
            })
        orders_data.append({
            'id': order.id,
            'table': order.table.name if order.table else '',
            'online_source': order.online_source if hasattr(order, 'online_source') and order.online_source else '',
            'total': float(order.total),
            'created_at': order.created_at.strftime('%d/%m/%y %I:%M %p'),
            'items': items_data,
            'started': order.started,  # Add this line
            'attendant': str(order.completedby) if order.completedby else '',
        })
    return JsonResponse({'orders': orders_data})