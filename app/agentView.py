from django.shortcuts import render

def agenthome(request):
    print('hiii')
    return render(request, 'agent/agent.html')