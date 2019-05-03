from django.conf import settings


def global_settings(request):
    # return any necessary values
    return {
        'STATIC_URL': settings.STATIC_URL
    }
