from django.conf import settings


def global_settings(request):
    # return any necessary values
    return {
        'DATA_URL': settings.DATA_URL,
        'STATIC_URL': settings.STATIC_URL
    }
