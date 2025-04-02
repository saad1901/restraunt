from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import *
import json
import calendar
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.views.decorators.http import require_POST
from .forms import CategoryForm, MenuItemForm, TableForm
from .sendmsg import sendbill
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.contrib.auth import get_user_model

#THis is for waiters
@login_required
def home(request): 
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    if not hotel.status:
        agent_cell = hotel.agent.phone if hotel.agent else "NOAGENT"
        agent_name = hotel.agent.first_name if hotel.agent else "NOAGENT"
        return render(request, 'notallowed.html', {'agent_cell':agent_cell, 'agent_name':agent_name})
    tables = Table.objects.filter(hotel=request.user.staffof).order_by('name')
    categories = MenuCategory.objects.filter(hotel=request.user.staffof)
    items = MenuItem.objects.filter(hotel=request.user.staffof)
    return render(request, 'waiter.html',{'hotel':hotel,'tables':tables , 'categories':categories, 'items':items})

def submit_order(request):
    if request.method == "POST":
        try:
            # hotel = Hotel.objects.get(owner=request.user)
            data = json.loads(request.body)
            table_id = data.get("table")
            items = data.get("items", [])

            if not table_id or not items:
                return JsonResponse({"success": False, "message": "Invalid order details. Missing table or items."})
            
            table = Table.objects.get(id=table_id)

            if not table.occupied:
                # Create a new order for a free table
                order = Order.objects.create(table=table, total=0, hotel=request.user.staffof, completedby=request.user)
                table.occupied = True
                table.save()
                total_price = 0
            else:
                # Attempt to retrieve the active order
                try:
                    order = Order.objects.get(table=table, completed=False, hotel=request.user.staffof)
                    total_price = order.total
                except Order.DoesNotExist:
                    # Handle the edge case if no active order exists for an occupied table
                    order = Order.objects.create(table=table, total=0, hotel=request.user.staffof, completedby=request.user)
                    total_price = 0

            
            for item_data in items:
                item = MenuItem.objects.get(id=item_data["item"])
                quantity = int(item_data["quantity"])
                OrderItems.objects.create(order=order, item=item, quantity=quantity, hotel=request.user.staffof)
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

@login_required
def owner(request):
    if request.user.role != 'owner':
        return JsonResponse({"success": False, "message": "You are not authorized to view this page. Please login as an owner."})
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    if not hotel.status:
        agent_cell = hotel.agent.phone if hotel.agent else "NOAGENT"
        agent_name = hotel.agent.first_name if hotel.agent else "NOAGENT"
        return render(request, 'notallowed.html', {'agent_cell':agent_cell, 'agent_name':agent_name})
    tables = Table.objects.filter(hotel=request.user.staffof).order_by('name')
    orders = Order.objects.filter(completed=False, hotel=request.user.staffof)
    total_income_today = Order.objects.filter(completed=True, created_at__date=today, hotel=request.user.staffof).aggregate(total=Sum('total'))['total'] or 0
    total_income_yesterday = Order.objects.filter(completed=True,created_at__date=yesterday, hotel=request.user.staffof).aggregate(total=Sum('total'))['total'] or 0
    total_orders_today = Order.objects.filter(created_at__date=today, completed=True, hotel=request.user.staffof).count()
    try:
        upi = PaymentDetails.objects.get(hotel=hotel)
    except:
        upi = []
    return render(request, 'admin.html', {'hotel':hotel, 'tables':tables, 'orders':orders , 'tid':total_income_today, 
                                          'tiy':total_income_yesterday, 'tot':total_orders_today,
                                          'upi':upi})    


@require_POST
def complete_order(request):
    try:
        # hotel = Hotel.objects.get(id=request.user.staffof.id)
        data = json.loads(request.body)
        order_id = data.get("order_id")
        discount = float(data.get("discount", 0))
        final_total = float(data.get("final_total"))
        phone = data.get("phone", "").strip()

        if not order_id or final_total is None:
            return JsonResponse({"success": False, "message": "Missing required fields."})

        # Retrieve the active order; ensure it's not already completed
        order = Order.objects.get(id=order_id, completed=False, hotel=request.user.staffof)

        # Update order details
        order.discount = discount  # discount percentage
        order.total = final_total   # final total after discount
        order.phone_number = phone
        order.completed = True
        order.save()
        sendbill(final_total, order.id)
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
        # hotel = Hotel.objects.get(id=request.user.staffof.id)
        data = json.loads(request.body)
        order_id = data.get("order_id")
        if not order_id:
            return JsonResponse({"success": False, "message": "Missing order ID."})
        
        order = Order.objects.get(id=order_id)
        table = order.table
        order.delete()
        
        # If there are no active orders for this table, mark it as unoccupied.
        if not Order.objects.filter(table=table, completed=False, hotel=request.user.staffof).exists():
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
        total = sum(item.item.price * item.quantity for item in order.orderitems.all())
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
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    tables = Table.objects.get(hotel=request.user.staffof).order_by('name')
    categories = MenuCategory.objects.get(hotel=request.user.staffof)
    menu_items = MenuItem.objects.get(hotel=request.user.staffof).order_by('category')
    return render(request, 'settings.html', {'categories': categories, 'tables':tables,
                                             'menu_items':menu_items})

def payment(request):
    # Get the hotel associated with the current user
    try:
        hotel = Hotel.objects.get(id=request.user.staffof.id)
    except ObjectDoesNotExist:
        return HttpResponse('ERROR __ Associated hotel not found')
    
    # Handle form submission
    if request.method == "POST":
        upiid = request.POST.get('upi_id')
        name = request.POST.get('business_name')

        # Update or create payment details
        PaymentDetails.objects.update_or_create(
            hotel=hotel,
            defaults={
                'upiid': upiid,
                'name': name
            }
        )
        # return redirect('payment')
        return redirect("/payment/?success")   # Redirect to prevent duplicate submissions

    # Try to get existing payment details
    try:
        upi = PaymentDetails.objects.get(hotel=hotel)
    except ObjectDoesNotExist:
        upi = None

    return render(request, 'paymentsetting.html', {'upi': upi})


# from django.contrib.auth.decorators import login_required

# views.py

# @login_required
def add_category(request):
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)  # Don't save yet
            category.hotel = hotel  # Assign hotel before saving
            category.save()
            messages.success(request, 'Category added successfully!')
        else:
            messages.error(request, 'Error adding category: ' + str(form.errors))
        return redirect('category')

# @login_required
def edit_category(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    if request.method == 'POST':
        # Make sure MenuCategory matches your actual model name
        category = get_object_or_404(MenuCategory, id=request.POST.get('id'))
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
        else:
            messages.error(request, 'Error updating category: ' + str(form.errors))
        return redirect('category')

# @login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(MenuCategory, id=category_id)
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category')

# @login_required
def add_menu_item(request):
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            menuitem = form.save(commit=False)  # Don't save yet
            menuitem.hotel = hotel  # Assign hotel before saving
            menuitem.save()
            messages.success(request, 'Menu item added successfully!')
        else:
            messages.error(request, 'Error adding menu item: ' + str(form.errors))
        return redirect('item')
# 
# @login_required
def edit_menu_item(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=request.POST.get('id'))
        form = MenuItemForm(request.POST, instance=menu_item)
        if form.is_valid(): 
            form.save()
            messages.success(request, 'Menu item updated successfully!')
        else:
            messages.error(request, 'Error updating menu item: ' + str(form.errors))
        return redirect('item')

# @login_required
def delete_menu_item(request, item_id):
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id)
        menu_item.delete()
        messages.success(request, 'Menu item deleted successfully!')
        return redirect('item')
    

def add_table(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    if request.method == "POST":
        name = request.POST.get("table_number")
        if name:
            Table.objects.create(name=name, occupied=False, hotel=request.user.staffof)  # Always False when adding a new table
            messages.success(request, "Table added successfully!")
        return redirect('table')


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
    return redirect('table')
        
def delete_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    table.delete()
    messages.success(request, "Table deleted successfully!")
    return redirect('table')

@login_required
def button(request):
    return render(request, 'buttons.html')

def table(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    tables = Table.objects.filter(hotel=request.user.staffof).order_by('name')
    return render(request, 'table.html', {'tables':tables})

def category(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    categories = MenuCategory.objects.filter(hotel=request.user.staffof)
    return render(request, 'category.html', {'categories':categories})

def item(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    items = MenuItem.objects.filter(hotel=request.user.staffof).order_by('category')
    categories = MenuCategory.objects.filter(hotel=request.user.staffof)
    return render(request, 'items.html', {'menu_items':items, 'categories':categories})

def reports(request):
    # items = MenuItem.objects.all()
    return render(request, 'reports/reports.html')

def inventory(request):
    return render(request, 'reports/inventory.html')

def sales(request):
    return render(request, 'reports/sales/sales.html')

@login_required
def dailytransc(request):
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            # Convert the date string to a date object
            selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            # Filter orders for the given day (assuming created_at is a DateTimeField)
            orders = Order.objects.filter(
                hotel=request.user.staffof, 
                created_at__date=selected_date_obj
            ).prefetch_related('orderitems').order_by('created_at')
        except ValueError:
            orders = Order.objects.filter(hotel=request.user.staffof).prefetch_related('orderitems').order_by('created_at')
            selected_date_obj = None
    else:
        orders = Order.objects.filter(hotel=request.user.staffof).prefetch_related('orderitems').order_by('created_at')
        selected_date_obj = None

    return render(request, 'reports/sales/dailytransc.html', {
        'orders': orders,
        'selected_date': selected_date_obj,
        'grand_total' : orders.aggregate(total=Sum('total'))['total'] or 0,

    })

@login_required
def monthly_report(request):

    # Get month parameter from GET request in "YYYY-MM" format; default to current month if not provided.
    month_str = request.GET.get('month')
    if month_str:
        try:
            selected_year, selected_month = map(int, month_str.split('-'))
        except ValueError:
            selected_year, selected_month = datetime.today().year, datetime.today().month
            month_str = f"{selected_year}-{selected_month:02d}"
    else:
        selected_year, selected_month = datetime.today().year, datetime.today().month
        month_str = f"{selected_year}-{selected_month:02d}"

    # Determine the number of days in the selected month
    num_days = calendar.monthrange(selected_year, selected_month)[1]
    day_data = []

    def get_day_suffix(day):
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        return suffix

    grand_total = 0

    for day in range(1, num_days + 1):
        current_date = date(selected_year, selected_month, day)
        # Filter orders for the current date
        orders = Order.objects.filter(
            hotel=request.user.staffof,
            created_at__date=current_date
        )
        # Aggregate the total revenue for the day
        total_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        
        # Format the date as "2nd Mar" or "10th Dec"
        day_suffix = get_day_suffix(day)
        formatted_date = f"{day}{day_suffix} {current_date.strftime('%b')}"
        
        day_data.append({
            'day': day,
            'date': formatted_date,  # This will now be like "2nd Mar"
            'total_revenue': total_revenue,
            'org_date': current_date.strftime('%Y-%m-%d'),
            'whichday' : current_date.weekday()
        })
        grand_total+=total_revenue

    return render(request, 'reports/sales/monthlytransac.html', {
        'selected_year': selected_year,
        'selected_month': calendar.month_name[selected_month],
        'day_data': day_data,
        'month_str': month_str,
        'grand_total': grand_total,

    })



def revenue(request):
    return render(request, 'reports/revenue.html')

def timeanalysis(request):
    # Get time filter from request (default to 1 day)
    days = int(request.GET.get('days', 1))
    start_date = timezone.now() - timedelta(days=days)
    
    # Filter orders based on time range and annotate hours
    orders = (
        Order.objects
        .filter(created_at__gte=start_date)
        .annotate(hour=ExtractHour('created_at'))
        .values('hour')
        .annotate(total=Count('id'))
        .order_by('hour')
    )

    # Create complete 24-hour structure with zeros for missing hours
    hour_dict = {entry['hour']: entry['total'] for entry in orders}
    full_hours = []
    full_totals = []
    
    for hour in range(24):
        full_hours.append(hour)
        full_totals.append(hour_dict.get(hour, 0))

    context = {
        'hours': json.dumps(full_hours),
        'totals': json.dumps(full_totals),
        'selected_days': days
    }
    return render(request, 'reports/timeanalysis.html', context)

def staff(request):
    User = get_user_model()
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    staff_members = User.objects.filter(staffof=hotel)
    return render(request, 'addstaff.html', {'staff_members':staff_members})

from django.contrib.auth import get_user_model
# @login_required
def add_staff(request):
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    User = get_user_model()
    if request.method == 'POST':
        print(2)
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Choose another one.")
        else:
            User.objects.create(username=username, staffof=hotel, hint=password ,password=make_password(password), role=role)
            messages.success(request, "Staff member added successfully.")

    return redirect('staff')


User = get_user_model()
@login_required
def edit_staff(request):
    if request.method == 'POST':
        staff = get_object_or_404(User, id=request.POST.get('id'))
        staff.username = request.POST.get('username')
        if request.POST.get('password'):
            staff.password = make_password(request.POST.get('password'))
        staff.role = request.POST.get('role')
        staff.save()
        messages.success(request, "Staff details updated.")

    return redirect('staff')

@login_required
def toggle_hotel_status(request, hotel_id):
    if request.user.role != 'superadmin':
        return JsonResponse({"success": False, "message": "You are not authorized to perform this action"})
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    if request.method == 'POST':
        print(hotel_id)
        # Toggle the allowed status
        if hotel.status == 1:
            hotel.status = 0
        else:
            hotel.status = 1
        hotel.save()
        messages.success(request, 'Hotel status updated successfully.')
    return redirect('home')  # Adjust with your portal URL name
