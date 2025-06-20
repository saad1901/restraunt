from django.http import HttpResponse
from django.shortcuts import render
from app.models import Hotel, Table

def show_menu(request, hotel, table):
    
    context = {'hotel' : hotel, 'table': table}
    return render(request, 'usertemplates/menupage.html', context)
