from django.shortcuts import HttpResponseRedirect
# Create your views here.

def myLoginRequired(function):
    def wrapper(request, *args, **kw):
        userObj = request.session['user']
        if userObj is None:
            return HttpResponseRedirect('/login/show/')
        else:
            return function(request, *args, **kw)
    return wrapper
