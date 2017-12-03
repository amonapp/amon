from functools import wraps

from django.urls import reverse
from django.shortcuts import redirect

def user_is_admin(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated():
            pass
            # if request.role.type != 'Admin':
            #     return redirect(reverse('login'))

        return view(request, *args, **kwargs)
    
    return inner