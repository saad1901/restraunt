from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
import json 

def home(request):
    tables = Table.objects.all()
    categories = MenuCategory.objects.all()
    items = MenuItem.objects.all()
    return render(request, 'waiter.html',{'tables':tables , 'categories':categories, 'items':items})


def submit_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            table_id = data.get("table")
            items = data.get("items", [])

            if not table_id or not items:
                return JsonResponse({"success": False, "message": "Invalid order details. Missing table or items."})
            
            table = Table.objects.get(id=table_id)

            if not table.occupied:
                # Create a new order for a free table
                order = Order.objects.create(table=table, total=0)
                table.occupied = True
                table.save()
                total_price = 0
            else:
                # Attempt to retrieve the active order
                try:
                    order = Order.objects.get(table=table, completed=False)
                    total_price = order.total
                except Order.DoesNotExist:
                    # Handle the edge case if no active order exists for an occupied table
                    order = Order.objects.create(table=table, total=0)
                    total_price = 0

            
            for item_data in items:
                item = MenuItem.objects.get(id=item_data["item"])
                quantity = int(item_data["quantity"])
                OrderItems.objects.create(order=order, item=item, quantity=quantity)
                total_price += item.price * quantity

            order.total = total_price
            order.save()

            return JsonResponse({"success": True, "message": "Order placed successfully!"})

        except Exception as e:
            print("Error:", str(e))  # Debugging Log
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)



def owner(request):
    tables = Table.objects.all()
    orders = Order.objects.filter(table__occupied=False)

    return render(request, 'admin.html', {'tables':tables, 'orders':orders})    