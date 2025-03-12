from django.shortcuts import render
from .models import Hotel, Order
from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def agenthome(request):
    if request.user.role != 'agent':
        return HttpResponse('You are not allowed to view this page.............. ! Simon Go Back')
    hotels = Hotel.objects.all()
    total = Order.objects.aggregate(Sum('total'))['total__sum'] or 0
    print(total)
    return render(request, 'agent/agent.html',{'hotels':hotels, 'total':total})