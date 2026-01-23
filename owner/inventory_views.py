from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import InventoryItem, InventoryTransaction, MenuCategory
from django.core.paginator import Paginator
from decimal import Decimal

@login_required
def inventory(request):
    hotel = request.user.staffof
    items_query = InventoryItem.objects.filter(hotel=hotel).select_related('category')
    categories = MenuCategory.objects.filter(hotel=hotel)
    
    # Handle filters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'name')
    
    # Apply filters
    if status_filter:
        items_query = items_query.filter(status=status_filter)
    if category_filter:
        items_query = items_query.filter(category_id=category_filter)
    if search_query:
        items_query = items_query.filter(name__icontains=search_query)
    
    # Apply sorting
    if sort_by == 'quantity_asc':
        items_query = items_query.order_by('quantity')
    elif sort_by == 'quantity_desc':
        items_query = items_query.order_by('-quantity')
    elif sort_by == 'price_asc':
        items_query = items_query.order_by('unit_price')
    elif sort_by == 'price_desc':
        items_query = items_query.order_by('-unit_price')
    elif sort_by == 'updated':
        items_query = items_query.order_by('-last_updated')
    else:
        items_query = items_query.order_by('name')
    
    # Paginate results
    page = request.GET.get('page', 1)
    per_page = 20  # Show 20 items per page
    paginator = Paginator(items_query, per_page)
    items = paginator.get_page(page)
    
    # Get all items for metrics (without pagination)
    all_items = items_query
    
    # Metrics for dashboard
    total_items = all_items.count()
    low_stock_count = all_items.filter(status='low_stock').count()
    out_of_stock_count = all_items.filter(status='out_of_stock').count()
    
    # Calculate inventory value (consider using aggregate sum in DB for larger datasets)
    total_inventory_value = sum(item.quantity * item.unit_price for item in all_items)
    
    context = {
        'inventory_items': items,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_items': total_items,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_inventory_value': total_inventory_value,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': items,
    }
    
    return render(request, 'owner/reports/inventory.html', context)

@login_required
def add_inventory_item(request):
    if request.method == 'POST':
        hotel = request.user.staffof
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        quantity = Decimal(request.POST.get('quantity'))
        unit = request.POST.get('unit')
        unit_price = Decimal(request.POST.get('unit_price'))
        reorder_level = Decimal(request.POST.get('reorder_level') or 10)
        category_id = request.POST.get('category')
        
        try:
            category = None
            if category_id:
                category = MenuCategory.objects.get(id=category_id, hotel=hotel)
            
            # Create new inventory item
            item = InventoryItem.objects.create(
                hotel=hotel,
                name=name,
                description=description,
                quantity=quantity,
                unit=unit,
                unit_price=unit_price,
                reorder_level=reorder_level,
                category=category
            )
            
            # Create initial purchase transaction
            InventoryTransaction.objects.create(
                hotel=hotel,
                item=item,
                transaction_type='purchase',
                quantity=quantity,
                unit_price=unit_price,
                notes=f"Initial inventory setup for {name}",
                created_by=request.user
            )
            
            messages.success(request, f"Item '{name}' added to inventory successfully.")
        except Exception as e:
            messages.error(request, f"Error adding inventory item: {str(e)}")
            
        return redirect('inventory')
    
    return redirect('inventory')

@login_required
def edit_inventory_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        hotel = request.user.staffof
        
        try:
            item = InventoryItem.objects.get(id=item_id, hotel=hotel)
            
            # Store original quantity for transaction record
            original_quantity = item.quantity
            
            # Update fields
            item.name = request.POST.get('name')
            item.description = request.POST.get('description', '')
            item.unit = request.POST.get('unit')
            item.unit_price = Decimal(request.POST.get('unit_price'))
            item.reorder_level = Decimal(request.POST.get('reorder_level') or 0)
            
            category_id = request.POST.get('category')
            item.category = None if not category_id else MenuCategory.objects.get(id=category_id, hotel=hotel)
            
            # Handle quantity change
            new_quantity = Decimal(request.POST.get('quantity'))
            quantity_diff = new_quantity - original_quantity
            item.quantity = new_quantity
            
            item.save()
            
            # Create transaction record if quantity changed
            if quantity_diff != 0:
                transaction_type = 'adjustment'
                notes = f"Manual quantity adjustment from {original_quantity} to {new_quantity}"
                
                InventoryTransaction.objects.create(
                    hotel=hotel,
                    item=item,
                    transaction_type=transaction_type,
                    quantity=abs(quantity_diff),
                    notes=notes,
                    created_by=request.user
                )
            
            messages.success(request, f"Item '{item.name}' updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating inventory item: {str(e)}")
        
        return redirect('inventory')
    
    return redirect('inventory')

@login_required
def delete_inventory_item(request, item_id):
    if request.method == 'POST':
        hotel = request.user.staffof
        
        try:
            item = InventoryItem.objects.get(id=item_id, hotel=hotel)
            item_name = item.name
            
            # Create write-off transaction before deleting
            InventoryTransaction.objects.create(
                hotel=hotel,
                item=item,
                transaction_type='writeoff',
                quantity=item.quantity,
                notes=f"Item deleted from inventory",
                created_by=request.user
            )
            
            item.delete()
            messages.success(request, f"Item '{item_name}' deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting inventory item: {str(e)}")
        
        return redirect('inventory')
    
    return redirect('inventory')

@login_required
def inventory_transaction(request):
    if request.method == 'POST':
        hotel = request.user.staffof
        item_id = request.POST.get('item_id')
        transaction_type = request.POST.get('transaction_type')
        
        try:
            # Force safe Decimal conversion for quantity with extra safeguards
            quantity_str = request.POST.get('quantity', '0')
            quantity_str = quantity_str.replace(',', '.') if quantity_str else '0'
            quantity = Decimal(quantity_str)
            
            notes = request.POST.get('notes', '')
            
            # Safe handling of unit price with explicit conversion
            unit_price_str = request.POST.get('unit_price', '')
            unit_price = None
            if unit_price_str and unit_price_str.strip():
                unit_price_str = unit_price_str.replace(',', '.') 
                unit_price = Decimal(unit_price_str)
            
            item = InventoryItem.objects.get(id=item_id, hotel=hotel)
            
            # Force conversion of item.quantity to Decimal
            current_quantity_str = str(item.quantity)
            current_quantity = Decimal(current_quantity_str)
            
            # Use full explicit calculations avoiding in-place operators
            if transaction_type == 'purchase':
                new_quantity = current_quantity + quantity
                item.quantity = new_quantity
                if unit_price:
                    item.unit_price = unit_price
            elif transaction_type == 'usage':
                if current_quantity < quantity:
                    messages.error(request, f"Cannot use {quantity} {item.get_unit_display()} - only {current_quantity} {item.get_unit_display()} available.")
                    return redirect('inventory')
                new_quantity = current_quantity - quantity
                item.quantity = new_quantity
            elif transaction_type == 'adjustment':
                adjustment_type = request.POST.get('adjustment_type')
                if adjustment_type == 'add':
                    new_quantity = current_quantity + quantity
                    item.quantity = new_quantity
                else:  # subtract
                    if current_quantity < quantity:
                        messages.error(request, f"Cannot subtract {quantity} {item.get_unit_display()} - only {current_quantity} {item.get_unit_display()} available.")
                        return redirect('inventory')
                    new_quantity = current_quantity - quantity
                    item.quantity = new_quantity
            
            # Force final conversion before saving to ensure type consistency
            item.quantity = Decimal(str(item.quantity))
            item.save()
            
            # Create transaction record
            InventoryTransaction.objects.create(
                hotel=hotel,
                item=item,
                transaction_type=transaction_type,
                quantity=quantity,
                notes=notes,
                unit_price=unit_price if transaction_type == 'purchase' else None,
                created_by=request.user
            )
            
            messages.success(request, f"Transaction recorded successfully for '{item.name}'.")
        except Exception as e:
            # Provide detailed error for debugging
            import traceback
            print(f"Inventory transaction error: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"Error recording transaction: {str(e)}")
        
        return redirect('inventory')
    
    return redirect('inventory')

@login_required
def inventory_history(request):
    hotel = request.user.staffof
    item_id = request.GET.get('item_id', '')
    transaction_type = request.GET.get('transaction_type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Base query with prefetching
    transactions = InventoryTransaction.objects.filter(hotel=hotel).select_related('item', 'created_by')
    
    # Apply filters
    if item_id:
        transactions = transactions.filter(item_id=item_id)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if start_date:
        transactions = transactions.filter(transaction_date__gte=start_date)
    if end_date:
        transactions = transactions.filter(transaction_date__lte=end_date)
    
    # Paginate results
    page = request.GET.get('page', 1)
    per_page = 20  # Show 20 transactions per page
    paginator = Paginator(transactions, per_page)
    transactions_page = paginator.get_page(page)
    
    # Get all inventory items for filter dropdown
    items = InventoryItem.objects.filter(hotel=hotel).order_by('name')
    
    context = {
        'transactions': transactions_page,
        'inventory_items': items,
        'item_id': item_id,
        'transaction_type': transaction_type,
        'start_date': start_date,
        'end_date': end_date,
        'transaction_types': InventoryTransaction.TRANSACTION_TYPES,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': transactions_page,
    }
    
    return render(request, 'reports/inventory_history.html', context) 