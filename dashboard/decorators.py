from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def staff_member_required(view_func):
    """Allow only SHOP_OWNER and ADMIN roles."""
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff_member:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped