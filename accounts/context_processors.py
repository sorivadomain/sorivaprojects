from django.conf import settings


def user_profile_data(request):
    profile_pic_url = '/static/images/user.png'  # Default fallback
    if request.user.is_authenticated:
        if request.user.is_superuser or getattr(request.user, 'adminuser', None):
            profile_pic_url = request.user.profile_picture.url if request.user.profile_picture else '/static/images/user.png'
    return {'profile_pic_url': profile_pic_url}