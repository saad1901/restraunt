from django.shortcuts import render

def terms_view(request):
    """
    Display Terms of Service page.
    """
    return render(request, 'frontsite/terms.html')

def privacy_view(request):
    """
    Display Privacy Policy page.
    """
    return render(request, 'frontsite/privacy.html')

def cookies_view(request):
    """
    Display Cookies Policy page.
    """
    return render(request, 'frontsite/cookies.html')

def help_center_view(request):
    """
    Display Help Center page.
    """
    return render(request, 'frontsite/help-center.html')

def documentation_view(request):
    """
    Display Documentation page.
    """
    return render(request, 'frontsite/documentation.html')

def api_view(request):
    """
    Display API Reference page.
    """
    return render(request, 'frontsite/api.html')

def status_view(request):
    """
    Display System Status page.
    """
    return render(request, 'frontsite/status.html') 