from django.shortcuts import render

class ErrorPageRedirectMiddleware:
    def __init__(self, get_response):
        print("__init__")
        self.get_response = get_response
    
    def __call__(self, request):
        print("__call__")
        response = self.get_response(request)
        status = response.status_code
        if 400 <= status and status <= 499:
            message = "client side error"
        elif 500 <= status and status <= 599:
            message = "server side error"
        else:
            return response
        return render(request, 'partials/error.html', {"status": response.status_code, "message": message})
