from django.core.exceptions import ObjectDoesNotExist
import calendar
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib import messages
from app.models import *
from superadmin.models import BillingPlans
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.views.decorators.http import require_POST
from app.forms import TableForm
from app.sendmsg import sendbill
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.contrib.auth import get_user_model
import json
from django.views.decorators.csrf import csrf_exempt
from payments import pay_link_customer

@login_required
def owner(request):
    if request.user.role != 'owner':
        return JsonResponse({"success": False, "message": "You are not authorized to view this page. Please login as an owner."})
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    
    # Get current date in Indian timezone
    india_tz = timezone.get_current_timezone()
    current_date = timezone.now().astimezone(india_tz).date()
    yesterday_date = current_date - timedelta(days=1)
    tables = Table.objects.filter(hotel=request.user.staffof).order_by('name')
    orders = Order.objects.filter(completed=False, hotel=request.user.staffof)
    
    # Use current_date for today's calculations
    total_income_today = Order.objects.filter(
        completed=True, 
        created_at__date=current_date, 
        hotel=request.user.staffof
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Use yesterday_date for yesterday's calculations
    total_income_yesterday = Order.objects.filter(
        completed=True,
        created_at__date=yesterday_date, 
        hotel=request.user.staffof
    ).aggregate(total=Sum('total'))['total'] or 0
    
    total_orders_today = Order.objects.filter(
        created_at__date=current_date, 
        completed=True, 
        hotel=request.user.staffof
    ).count()
    
    # Get categories and menu items for the new order modal
    categories = MenuCategory.objects.filter(hotel=request.user.staffof)
    items = MenuItem.objects.filter(hotel=request.user.staffof).order_by('category')
    try:
        upi = PaymentDetails.objects.get(hotel=hotel)
    except:
        upi = []
    
    # Get subscription status and agent contact info
    expiry = hotel.expiry
    subscription_active = hotel.expiry >= date.today()
    agent_name = hotel.agent.first_name if hotel.agent else "NOAGENT"
    agent_cell = hotel.agent.phone if hotel.agent else "NOAGENT"
    
    context = {
        'hotel': hotel,
        'tables': tables,
        'orders': orders,
        'tid': total_income_today,
        'tiy': total_income_yesterday,
        'tot': total_orders_today,
        'upi': upi,
        'categories': categories,
        'items': items,
        'subscription_active': subscription_active,
        'agent_name': agent_name,
        'agent_cell': agent_cell,
        'expiry' : expiry
    }
    
    return render(request, 'owner/home.html', context)

# @login_required
def submit_order(request):
    if request.method == "POST":
        try:
            hotel = Hotel.objects.get(id=request.user.staffof.id)
            # Check if hotel subscription is active
            if not hotel.status:
                return JsonResponse({
                    "success": False, 
                    "message": "Your hotel subscription has expired. Please contact support to enable ordering."
                })
            data = json.loads(request.body)
            order_type = data.get("order_type", "table")
            items = data.get("items", [])
            if order_type == "table":
                table_id = data.get("table")
                if not table_id or not items:
                    return JsonResponse({"success": False, "message": "Invalid order details. Missing table or items."})
                table = Table.objects.get(id=table_id)
                if not table.occupied:
                    # Create a new order for a free table
                    order = Order.objects.create(table=table, total=0, hotel=hotel, completedby=request.user, order_type='table')
                    table.occupied = True
                    table.save()
                    total_price = 0
                else:
                    try:
                        order = Order.objects.get(table=table, completed=False, hotel=hotel)
                        total_price = order.total
                    except Order.DoesNotExist:
                        order = Order.objects.create(table=table, total=0, hotel=hotel, completedby=request.user, order_type='table')
                        total_price = 0
            elif order_type == "online":
                online_source = data.get("online_source")
                if not online_source or not items:
                    return JsonResponse({"success": False, "message": "Invalid order details. Missing online source or items."})
                # Create order with no table, set order_type and online_source (assume model has these fields)
                order = Order.objects.create(table=None, total=0, hotel=hotel, completedby=request.user, order_type='online', online_source=online_source)
                total_price = 0
            else:
                return JsonResponse({"success": False, "message": "Invalid order type."})
            for item_data in items:
                item = MenuItem.objects.get(id=item_data["item"])
                quantity = int(item_data["quantity"])
                existing_item = OrderItems.objects.filter(order=order, item=item).first()
                if existing_item:
                    existing_item.quantity += quantity
                    existing_item.save()
                else:
                    OrderItems.objects.create(order=order, item=item, quantity=quantity, hotel=hotel)
                total_price += item.price * quantity
            order.total = total_price
            order.save()
            return JsonResponse({"success": True, "message": "Order placed successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

@require_POST
def complete_order(request):
    try:
        hotel = Hotel.objects.get(id=request.user.staffof.id)
        
        # Check if hotel subscription is active
        if not hotel.status:
            return JsonResponse({
                "success": False, 
                "message": "Your hotel subscription has expired. Please contact support to enable ordering."
            })
            
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
        hotel = Hotel.objects.get(id=request.user.staffof.id)
        
        # Check if hotel subscription is active
        if not hotel.status:
            return JsonResponse({
                "success": False, 
                "message": "Your hotel subscription has expired. Please contact support to enable ordering."
            })
            
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
        hotel = Hotel.objects.get(id=request.user.staffof.id)
        
        # Check if hotel subscription is active
        if not hotel.status:
            return JsonResponse({
                "success": False, 
                "message": "Your hotel subscription has expired. Please contact support to enable ordering."
            })
            
        data = json.loads(request.body)
        
        # Support both methods of identifying the order item
        order_item_id = data.get("order_item_id")
        order_id = data.get("order_id")
        menu_id = data.get("menu_id")
        change = int(data.get("change", 0))
        action = data.get("action")
        
        # Convert action to change if needed
        if change == 0 and action:
            if action == "increase":
                change = 1
            elif action == "decrease":
                change = -1
        
        if (not order_item_id and (not order_id or not menu_id)) or change == 0:
            return JsonResponse({"success": False, "message": "Invalid parameters."})
        
        # Find the order item by either direct ID or by order+menu ids
        if order_item_id:
            order_item = OrderItems.objects.get(id=order_item_id)
        else:
            # Find the order item by order_id and menu_id
            order = Order.objects.get(id=order_id)
            order_item = OrderItems.objects.filter(order_id=order_id, item_id=menu_id).first()
            
            if not order_item:
                return JsonResponse({"success": False, "message": "Order item not found for the given order and menu."})
        
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
    except Order.DoesNotExist:
        return JsonResponse({"success": False, "message": "Order not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

@login_required
@require_POST
@csrf_exempt  # If you want to allow AJAX from JS without CSRF token, otherwise remove this
def set_order_started(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        started = data.get('started', True)
        order = Order.objects.get(id=order_id)
        order.started = bool(started)
        order.save()
        return JsonResponse({'success': True, 'started': order.started})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
@login_required
def add_category(request):
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    if request.method == 'POST':
        name = request.POST.get('category_name')
        icon = request.POST.get('category_icon')
        
        # Create category directly
        MenuCategory.objects.create(
            name=name,
            icon=icon,
            hotel=hotel
        )
        messages.success(request, 'Category added successfully!')
        return redirect('category')

# @login_required
def edit_category(request):
    if request.method == 'POST':
        category = get_object_or_404(MenuCategory, id=request.POST.get('id'))
        
        # Get values directly from POST
        name = request.POST.get('name')
        icon = request.POST.get('icon')
        
        # Update category directly
        category.name = name
        category.icon = icon
        category.save()
        
        messages.success(request, 'Category updated successfully!')
        return redirect('category')
    
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
        # Get values directly from POST request
        name = request.POST.get('item_name')
        price = request.POST.get('item_price')
        category_id = request.POST.get('item_category')
        food_type = request.POST.get('food_type')
        # Create new menu item directly
        MenuItem.objects.create(
            name=name,
            price=price,
            food_type=food_type,
            category_id=category_id,
            hotel=hotel
        )
        
        messages.success(request, 'Menu item added successfully!')
        return redirect('item')

# @login_required
def edit_menu_item(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=request.POST.get('item_id'))
        
        # Get values directly from POST request
        name = request.POST.get('item_name')
        price = request.POST.get('item_price')
        category_id = request.POST.get('item_category')
        food_type = request.POST.get('food_type')
        # Update the menu item manually
        menu_item.name = name
        menu_item.price = price
        menu_item.category_id = category_id
        menu_item.food_type = food_type
        menu_item.save()
        
        messages.success(request, 'Menu item updated successfully!')
        return redirect('item')
    
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
def ajax_get_orders(request):

    if request.user.role != 'owner':
        return JsonResponse({"success": False, "message": "Unauthorized"})
    
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    
    # Get active orders
    orders = Order.objects.filter(completed=False, hotel=hotel)
    
    # Format orders data
    orders_data = []
    for order in orders:
        items_data = []
        for item in order.orderitems.all():
            items_data.append({
                'id': item.item.id,
                'name': item.item.name,
                'price': float(item.item.price),
                'quantity': item.quantity
            })
        
        orders_data.append({
            'id': order.id,
            'table_name': order.table.name if order.table else (order.online_source if order.order_type == 'online' else None),
            'total': float(order.total),
            'items': items_data,
            'created_time': order.created_at.strftime('%I:%M %p'),
            'attended_by': str(order.completedby) if order.completedby else None
        })
    # Get stats data
    india_tz = timezone.get_current_timezone()
    current_date = timezone.now().astimezone(india_tz).date()
    
    total_income_today = Order.objects.filter(
        completed=True, 
        created_at__date=current_date, 
        hotel=hotel
    ).aggregate(total=Sum('total'))['total'] or 0
    
    total_orders_today = Order.objects.filter(
        created_at__date=current_date, 
        completed=True, 
        hotel=hotel
    ).count()
    
    # Prepare response data
    response_data = {
        'success': True,
        'orders': orders_data,
        'stats': {
            'income_today': float(total_income_today),
            'orders_today': total_orders_today
        }
    }
    
    return JsonResponse(response_data)

@login_required
def custom_period(request):
    # Get date parameters from request with defaults
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Set default dates if not provided (last 30 days)
    if not start_date_str or not end_date_str:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    
    # Calculate date range
    date_range = (end_date - start_date).days + 1
    
    # Initialize stats
    transactions = []
    total_revenue = 0
    highest_day_revenue = 0
    highest_day_date = ""
    days_with_sales = 0
    
    # Function to get day suffix (1st, 2nd, 3rd, etc.)
    def get_day_suffix(day):
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        return suffix
    
    # Generate date range
    current_date = start_date
    previous_revenue = 0
    
    while current_date <= end_date:
        # Get orders for the current date
        orders = Order.objects.filter(
            hotel=request.user.staffof,
            created_at__date=current_date
        )
        
        # Calculate total revenue for the day
        day_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        
        # Calculate trend compared to previous day
        trend = day_revenue - previous_revenue
        if previous_revenue > 0:
            trend_percent = abs(int((trend / previous_revenue) * 100))
        else:
            trend_percent = 0
        
        # Track statistics
        if day_revenue > 0:
            days_with_sales += 1
            
        if day_revenue > highest_day_revenue:
            highest_day_revenue = day_revenue
            highest_day_date = current_date.strftime('%d %b')
        
        # Format date
        day = current_date.day
        day_suffix = get_day_suffix(day)
        formatted_date = f"{day}{day_suffix} {current_date.strftime('%b')}"
        
        # Add data to transactions list
        transactions.append({
            'date': formatted_date,
            'total_revenue': day_revenue,
            'trend': trend,
            'trend_percent': trend_percent,
            'org_date': current_date.strftime('%Y-%m-%d'),
            'whichday': current_date.weekday()
        })
        
        # Save revenue for trend calculation
        previous_revenue = day_revenue
        total_revenue += day_revenue
        
        # Increment date
        current_date += timedelta(days=1)
    
    # Calculate average daily revenue
    avg_daily_revenue = total_revenue / date_range if date_range > 0 else 0
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'transactions': transactions,
        'total_revenue': total_revenue,
        'highest_day_revenue': highest_day_revenue,
        'highest_day_date': highest_day_date,
        'days_with_sales': days_with_sales,
        'avg_daily_revenue': avg_daily_revenue,
        'total_days': date_range
    }
    
    return render(request, 'owner/reports/sales/custom_period.html', context)

@login_required
def button(request):
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    context = {
        'expiry' : hotel.expiry,
        'expired' : hotel.expiry < date.today(),
        'name' : hotel.name
    }
    return render(request, 'owner/settings.html', context=context)

def table(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    tables = Table.objects.filter(hotel=request.user.staffof).order_by('name')
    hotel = request.user.staffof
    owner = hotel.owner if hasattr(hotel, 'owner') else None
    return render(request, 'owner/table.html', {'tables': tables, 'owner': owner})

def category(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    categories = MenuCategory.objects.filter(hotel=request.user.staffof)
    return render(request, 'owner/category.html', {'categories':categories})

def item(request):
    # hotel = Hotel.objects.get(id=request.user.staffof.id)
    items = MenuItem.objects.filter(hotel=request.user.staffof).order_by('category')
    categories = MenuCategory.objects.filter(hotel=request.user.staffof)
    return render(request, 'owner/items.html', {'menu_items':items, 'categories':categories})

def reports(request):
    # items = MenuItem.objects.all()
    return render(request, 'owner/reports/reports.html')

def sales(request):
    return render(request, 'owner/reports/sales/sales.html')

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

    return render(request, 'owner/reports/sales/dailytransc.html', {
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
    highest_day_revenue = 0
    highest_day_date = ""
    days_with_sales = 0

    for day in range(1, num_days + 1):
        current_date = date(selected_year, selected_month, day)
        # Filter orders for the current date
        orders = Order.objects.filter(
            hotel=request.user.staffof,
            created_at__date=current_date
        )
        # Aggregate the total revenue for the day
        total_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        
        # Track statistics
        if total_revenue > 0:
            days_with_sales += 1
            
        if total_revenue > highest_day_revenue:
            highest_day_revenue = total_revenue
            highest_day_date = current_date.strftime('%d %b')
        
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

    # Calculate average daily revenue
    avg_daily_revenue = grand_total / num_days if num_days > 0 else 0

    return render(request, 'owner/reports/sales/monthlytransac.html', {
        'selected_year': selected_year,
        'selected_month': calendar.month_name[selected_month],
        'day_data': day_data,
        'month_str': month_str,
        'grand_total': grand_total,
        'highest_day_revenue': highest_day_revenue,
        'highest_day_date': highest_day_date,
        'days_with_sales': days_with_sales,
        'avg_daily_revenue': avg_daily_revenue,
    })



def revenue(request):
    return render(request, 'owner/reports/revenue.html')

def timeanalysis(request):
    # Get time filter from request (default to 1 day)
    days = int(request.GET.get('days', 1))
    start_date = timezone.now() - timedelta(days=days)
    
    # Filter orders based on time range and annotate hours
    orders = (
        Order.objects
        .filter(created_at__gte=start_date, hotel=request.user.staffof)
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
    
    # Get the most ordered items for this time period
    most_ordered_items = (
        OrderItems.objects
        .filter(order__created_at__gte=start_date, order__hotel=request.user.staffof, order__completed=True)
        .values('item__name')
        .annotate(total_ordered=Sum('quantity'))
        .order_by('-total_ordered')[:5]  # Get top 5 items
    )
    
    # Prepare data for chart
    top_item_names = [item['item__name'] for item in most_ordered_items]
    top_item_counts = [item['total_ordered'] for item in most_ordered_items]

    context = {
        'hours': json.dumps(full_hours),
        'totals': json.dumps(full_totals),
        'selected_days': days,
        'top_item_names': json.dumps(top_item_names),
        'top_item_counts': json.dumps(top_item_counts)
    }
    return render(request, 'owner/reports/timeanalysis.html', context)

def staff(request):
    User = get_user_model()
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    staff_members = User.objects.filter(staffof=hotel)
    return render(request, 'owner/addstaff.html', {'staff_members':staff_members})

from django.contrib.auth import get_user_model
# @login_required
def add_staff(request):
    hotel = Hotel.objects.get(id=request.user.staffof.id)
    User = get_user_model()
    if request.method == 'POST':
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

# Add the delete_staff function
@login_required
def delete_staff(request):
    if request.method == 'POST':
        staff_id = request.POST.get('id')
        staff = get_object_or_404(User, id=staff_id)
        
        # Don't allow deleting owners
        if staff.role == 'owner':
            messages.error(request, "Cannot delete an owner account.")
            return redirect('staff')
            
        staff.delete()
        messages.success(request, "Staff member deleted successfully.")

    return redirect('staff')

@login_required
def payment(request):
    # Get the hotel associated with the current user
    try:
        hotel = Hotel.objects.get(id=request.user.staffof.id)
    except ObjectDoesNotExist:
        messages.error(request, "Unable to find your hotel details. Please contact support.")
        return redirect('button')
    
    # Handle form submission
    if request.method == "POST":
        upiid = request.POST.get('upi_id', '').strip()
        name = request.POST.get('business_name', '').strip()
        
        if not upiid:
            messages.error(request, "UPI ID is required")
            return render(request, 'owner/paymentsetting.html', {'upi': None})

        # Update or create payment details
        try:
            PaymentDetails.objects.update_or_create(
            hotel=hotel,
            defaults={
                'upiid': upiid,
                'name': name
            }
        )
            return redirect("/owner/payment/?success")   # Redirect to prevent duplicate submissions
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'owner/paymentsetting.html', {'upi': None})

    # Try to get existing payment details
    try:
        upi = PaymentDetails.objects.get(hotel=hotel)
    except ObjectDoesNotExist:
        upi = None

    return render(request, 'owner/paymentsetting.html', {'upi': upi})

###################### FINANCE #########################

@login_required
def owner_billing(request):
    billing_plans = BillingPlans.objects.all().order_by('price')
    return render(request, 'owner/billing.html', {'billing_plans': billing_plans})

@login_required
def get_payment(request, plan_id):
    try:
        plan = BillingPlans.objects.get(id=plan_id)
    except BillingPlans.DoesNotExist:
        # print(f"Plan {plan_id} does not exist")
        return HttpResponseBadRequest("Invalid plan selected.")

    hotel = getattr(request.user, 'staffof', None)
    if not hotel:
        # print(f"User {request.user} has no hotel assigned")
        return HttpResponseBadRequest("This user is not linked to a hotel.")

    try:
        response = pay_link_customer.create_payment_link(request.user, plan.price)
        payment_link = response.get("link_url")
        print(response)
        if not payment_link:
            # print("Payment link missing in Cashfree response:", response)
            return HttpResponseBadRequest("Could not create payment link.")
    except Exception as e:
        # print("Error creating payment link:", e)
        return HttpResponseBadRequest("Payment error")
    return render(request, 'owner/paypage.html', {'link_url': payment_link})

@csrf_exempt
def cashfree_webhook(request):
    try:
        data = json.loads(request.body)
        order_id = data["data"]["order"]["order_tags"]["link_id"]  # internal order_id
        payment_status = data["data"]["payment"]["payment_status"]  # e.g. SUCCESS / FAILED / CANCELLED
    except Exception as e:
        return JsonResponse({"status": "failed", "reason": "invalid payload"}, status=400)

    try:
        payment = PaymentRecord.objects.get(order_id=order_id)
    except PaymentRecord.DoesNotExist:
        return JsonResponse({"status": "failed", "reason": "Unknown order_id"}, status=400)

    if payment.status != payment_status:
        if payment_status == "SUCCESS":
            hotel = payment.hotel
            if not hotel:
                return JsonResponse({"status": "failed", "reason": "Hotel not found"}, status=400)

            plan = BillingPlans.objects.get(price=payment.amount)
            if hotel.expiry and hotel.expiry >= date.today():
                hotel.expiry += timedelta(days=plan.expiry_days)
            else:
                hotel.expiry = date.today() + timedelta(days=plan.expiry_days)

            hotel.save()
            print(f"{hotel.name} is now active until {hotel.expiry}")

        payment.status = payment_status
        payment.save(update_fields=["status"])

    return JsonResponse({"status": "ok"})


@login_required
def bill_history(request):
    records = PaymentRecord.objects.filter(hotel=request.user.staffof).order_by('-created_at')
    context = {
        'records' : records
    }
    return render(request, 'owner/bill_history.html', context)

# @csrf_exempt
# def cashfree_webhook(request):
#     try:
#         data = json.loads(request.body)
#         order_id = data.get("order_id")
#         payment_status = data.get("payment_status")
#         print("Webhook data:", data)
#     except Exception as e:
#         print("Webhook parsing error:", e)
#         return JsonResponse({"status": "failed", "reason": "invalid payload"}, status=400)

#     try:
#         payment = PaymentRecord.objects.get(order_id=order_id)
#     except PaymentRecord.DoesNotExist:
#         return JsonResponse({"status": "failed", "reason": "Unknown order_id"}, status=400)

#     # Avoid double-processing
#     if payment.status != "SUCCESS" and payment_status == "SUCCESS":
#         hotel = payment.hotel
#         if not hotel:
#             return JsonResponse({"status": "failed", "reason": "Hotel not found"}, status=400)

#         # Extend expiry: if active, add to current expiry; else start from today
#         if hotel.expiry and hotel.expiry >= date.today():
#             hotel.expiry += timedelta(days=30)
#         else:
#             hotel.expiry = date.today() + timedelta(days=30)

#         hotel.save()
#         payment.status = "SUCCESS"
#         payment.save()

#         print(f"{hotel.name} is now active until {hotel.expiry}")

#     return JsonResponse({"status": "ok"})