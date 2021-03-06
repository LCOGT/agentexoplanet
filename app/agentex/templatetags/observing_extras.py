from django.templatetags.static import static
from django.template import Library
from django.conf import settings
from math import fabs,floor
from agentex.agentex_settings import decision_images
from agentex.models import Datapoint

register = Library()

@register.filter(name="planetprogress")
def planet_progress(user, planet):
    if user.is_authenticated:
        completed = Datapoint.objects.filter(user=user, data__event=planet, pointtype='S').count()
    else:
        completed = 0
    return completed

@register.filter(name='readableangle')
def readableangle(value):
    angle = value
    newangle = fabs(value)
    remainder = newangle - floor(newangle)
    newangle = int(floor(newangle))
    hour = int(floor(remainder*60))
    minute = (remainder*60  - hour)*60
    value = "%d:%d:%.2f" % (newangle,hour,minute)
    if (angle < 0):
      value = "-" + value
    return value

@register.filter
def convert_ra(value):
    # Adjust RA for catalog values which are in 0-360 not 0-24
    ra = value
    value = ra/15
    return readableangle(value)

@register.filter(name='is_false')
def is_false(arg):
    return arg is False

@register.filter(name='decisionconvert')
def decisionconvert(arg):
    dec = decision_images
    try:
        image = dec[arg]['image']
        name = dec[arg]['name']
        url = static('images/{}'.format(image))

        html = '<img src="{url}" alt="{alt}" title="Classified as {title}">'.format(
            url=url,
            alt=name,
            title=name,
        )
        return html
    except:
        return ""


@register.filter(name='progress_bars')
def progress_bars(value):
    try:
        value = int(value)
    except:
        return "ffff00"
    if (value<= 25):
        return "ff6633|cccccc|cccccc|cccccc"
    elif (value>25 and value<=50):
        return "ff6633|ff6633|cccccc|cccccc"
    elif (value>50 and value<=75):
        return "ff6633|ff6633|ff6633|cccccc"
    elif (value>75 and value<=100):
        return "ff6633|ff6633|ff6633|ff6633"
    else :
        return "ffff00"

@register.filter(name='hexangletodec')
def hexangletodec(value):
    value = value.split(":")
    if (int(value[0]) >= 0):
        sign = 1
    else :
        sign = -1
    return (int(value[0])+(sign*(float(value[1])/60)+(float(value[2])/3600)))
