from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import *
import json 
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_POST
from .forms import CategoryForm, MenuItemForm, TableForm

def home(request):
    tables = Table.objects.all().order_by('name')
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

today = timezone.now().date()
yesterday = today - timedelta(days=1)

def owner(request):
    tables = Table.objects.all()
    orders = Order.objects.filter(completed=False)
    total_income_today = Order.objects.filter(completed=True, created_at__date=today).aggregate(total=Sum('total'))['total'] or 0
    total_income_yesterday = Order.objects.filter(completed=True,created_at__date=yesterday).aggregate(total=Sum('total'))['total'] or 0
    total_orders_today = Order.objects.filter(created_at__date=today, completed=True).count()
    return render(request, 'admin.html', {'tables':tables, 'orders':orders , 'tid':total_income_today, 'tiy':total_income_yesterday, 'tot':total_orders_today})    


@require_POST
def complete_order(request):
    try:
        data = json.loads(request.body)
        order_id = data.get("order_id")
        discount = float(data.get("discount", 0))
        final_total = float(data.get("final_total"))
        phone = data.get("phone", "").strip()

        if not order_id or final_total is None:
            return JsonResponse({"success": False, "message": "Missing required fields."})

        # Retrieve the active order; ensure it's not already completed
        order = Order.objects.get(id=order_id, completed=False)

        # Update order details
        order.discount = discount  # discount percentage
        order.total = final_total   # final total after discount
        order.phone_number = phone
        order.completed = True
        order.save()

        # Mark the table as unoccupied now that the order is complete
        table = order.table
        table.occupied = False
        table.save()

        return JsonResponse({"success": True, "message": "Order completed successfully!"})
    except Order.DoesNotExist:
        return JsonResponse({"success": False, "message": "Active order not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
    
@require_POST
def delete_order(request):
    try:
        data = json.loads(request.body)
        order_id = data.get("order_id")
        if not order_id:
            return JsonResponse({"success": False, "message": "Missing order ID."})
        
        order = Order.objects.get(id=order_id)
        table = order.table
        order.delete()
        
        # If there are no active orders for this table, mark it as unoccupied.
        if not Order.objects.filter(table=table, completed=False).exists():
            table.occupied = False
            table.save()
            
        return JsonResponse({"success": True, "message": "Order deleted successfully."})
    except Order.DoesNotExist:
        return JsonResponse({"success": False, "message": "Order not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

@require_POST
def update_quantity(request):
    try:
        data = json.loads(request.body)
        order_item_id = data.get("order_item_id")
        change = int(data.get("change", 0))
        if not order_item_id or change == 0:  # Corrected here
            return JsonResponse({"success": False, "message": "Invalid parameters."})
        
        order_item = OrderItems.objects.get(id=order_item_id)
        order = order_item.order
        new_quantity = order_item.quantity + change
        
        if new_quantity < 1:
            order_item.delete()
            new_quantity = 0
        else:
            order_item.quantity = new_quantity
            order_item.save()
        
        # Recalculate the order total
        total = sum(item.item.price * item.quantity for item in order.orderitems_set.all())
        order.total = total
        order.save()
        
        return JsonResponse({
            "success": True,
            "new_quantity": new_quantity,
            "order_total": float(total),
            "order_id": order.id,
        })
    except OrderItems.DoesNotExist:
        return JsonResponse({"success": False, "message": "Order item not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

def settings(request):
    tables = Table.objects.all().order_by('name')
    categories = MenuCategory.objects.all()
    menu_items = MenuItem.objects.all().order_by('category')
    return render(request, 'settings.html', {'categories': categories, 'tables':tables,
                                             'menu_items':menu_items})


# from django.contrib.auth.decorators import login_required

# views.py

# @login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
        else:
            messages.error(request, 'Error adding category: ' + str(form.errors))
        return redirect('settings')

# @login_required
def edit_category(request):
    if request.method == 'POST':
        # Make sure MenuCategory matches your actual model name
        category = get_object_or_404(MenuCategory, id=request.POST.get('id'))
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
        else:
            messages.error(request, 'Error updating category: ' + str(form.errors))
        return redirect('settings')

# @login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(MenuCategory, id=category_id)
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('settings')

# @login_required
def add_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item added successfully!')
        else:
            messages.error(request, 'Error adding menu item: ' + str(form.errors))
        return redirect('settings')
# 
# @login_required
def edit_menu_item(request):
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=request.POST.get('id'))
        form = MenuItemForm(request.POST, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated successfully!')
        else:
            messages.error(request, 'Error updating menu item: ' + str(form.errors))
        return redirect('settings')

# @login_required
def delete_menu_item(request, item_id):
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id)
        menu_item.delete()
        messages.success(request, 'Menu item deleted successfully!')
        return redirect('settings')
    

def add_table(request):
    print(1)
    if request.method == "POST":
        print(2)
        name = request.POST.get("table_number")
        if name:
            print(name)
            Table.objects.create(name=name, occupied=False)  # Always False when adding a new table
            messages.success(request, "Table added successfully!")
        return redirect('settings')



# def edit_table(request, table_id):
#     table = get_object_or_404(Table, id=table_id)
#     if request.method == "POST":
#         table.name = request.POST.get("name")
#         table.save()
#         messages.success(request, "Table updated successfully!")
#     return redirect('restaurant_settings')

# def edit_table(request, table_id):
#     table = get_object_or_404(Table, id=table_id)
#     if request.method == 'POST':
#         form = TableForm(request.POST, instance=table)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Table updated successfully!")
#         else:
#             messages.error(request, "Error updating table: " + str(form.errors))
#         return redirect('settings')
    
def edit_table(request):
    print(1)
    if request.method == 'POST':
        table = get_object_or_404(Table, id=request.POST.get('table_id'))
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table updated successfully!')
        else:
            messages.error(request, 'Error updating Table: ' + str(form.errors))
    return redirect('settings')
        
def delete_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    table.delete()
    messages.success(request, "Table deleted successfully!")
    return redirect('restaurant_settings')
