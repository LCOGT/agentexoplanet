from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib import messages

from agentex.models import Achievement, Badge

def achievementscheck(person,planet,nmeas,nplan,ncals,ndcsn,ncomp):
    resp = []
    if nmeas == 1 : resp.append(achievementunlock(person,planet,'measurement_1'))
    elif nmeas == 5 : resp.append(achievementunlock(person,planet,'measurement_5'))
    elif nmeas == 10 : resp.append(achievementunlock(person,planet,'measurement_10'))
    elif nmeas == 25 : resp.append(achievementunlock(person,planet,'measurement_25'))
    elif nmeas == 50 : resp.append(achievementunlock(person,planet,'measurement_50'))
    elif nmeas == 100 : resp.append(achievementunlock(person,planet,'measurement_100'))
    elif nmeas == 250 : resp.append(achievementunlock(person,planet,'measurement_250'))
    elif nmeas == 500 : resp.append(achievementunlock(person,planet,'measurement_500'))
    elif nmeas == 1000 : resp.append(achievementunlock(person,planet,'measurement_1000'))
    elif nmeas == 1500 : resp.append(achievementunlock(person,planet,'measurement_1500'))
    elif nmeas == 2000 : resp.append(achievementunlock(person,planet,'measurement_2000'))

    if ncals >= 3 : resp.append(achievementunlock(person,planet,'calibrator_3'))
    elif ncals >= 5 : resp.append(achievementunlock(person,planet,'calibrator_5'))
    elif ncals >= 10 : resp.append(achievementunlock(person,planet,'calibrator_10'))
    elif ncals >= 15 : resp.append(achievementunlock(person,planet,'calibrator_15'))
    elif ncals >= 25 : resp.append(achievementunlock(person,planet,'calibrator_25'))

    if nplan == 1 : resp.append(achievementunlock(person,planet,'planet_1'))
    elif nplan == 2 : resp.append(achievementunlock(person,planet,'planet_2'))
    elif nplan == 3 : resp.append(achievementunlock(person,planet,'planet_3'))
    elif nplan == 4 : resp.append(achievementunlock(person,planet,'planet_4'))
    elif nplan == 5 : resp.append(achievementunlock(person,planet,'planet_5'))
    elif nplan == 6 : resp.append(achievementunlock(person,planet,'planet_6'))
    elif nplan == 7 : resp.append(achievementunlock(person,planet,'planet_7'))
    elif nplan == 8 : resp.append(achievementunlock(person,planet,'planet_8'))
    elif nplan == 9 : resp.append(achievementunlock(person,planet,'planet_9'))

    if ndcsn >= 3 : resp.append(achievementunlock(person,planet,'lightcurve_1star'))
    if ndcsn >= 10 : resp.append(achievementunlock(person,planet,'lightcurve_2star'))

    if ncomp == 1 : resp.append(achievementunlock(person,planet,'completed_1'))
    elif ncomp == 2 : resp.append(achievementunlock(person,planet,'completed_2'))
    elif ncomp == 3 : resp.append(achievementunlock(person,planet,'completed_3'))
    elif ncomp == 4 : resp.append(achievementunlock(person,planet,'completed_4'))
    elif ncomp == 5 : resp.append(achievementunlock(person,planet,'completed_5'))
    elif ncomp == 6 : resp.append(achievementunlock(person,planet,'completed_6'))
    elif ncomp == 7 : resp.append(achievementunlock(person,planet,'completed_7'))
    elif ncomp == 8 : resp.append(achievementunlock(person,planet,'completed_8'))
    elif ncomp == 9 : resp.append(achievementunlock(person,planet,'completed_9'))

    return resp


def achievementunlock(person,planet,typea):
    # Check what badges user has to see if they deserve more
    # The planet will simply be to record where they got this achievement
    achs = Achievement.objects.filter(person=person) #,planet=planet
    try:
        badge =  Badge.objects.get(name=typea)
    except Badge.DoesNotExist:
        return {'msg' : 'Wrong badge code', 'code': messages.ERROR}
    if achs.filter(badge=badge).count() == 0:
        newa = Achievement(badge=badge,planet=planet,person=person)	# ,planet=planet
        try:
            newa.save()
            LogEntry.objects.log_action(
                user_id         = person.id,
                content_type_id = ContentType.objects.get_for_model(newa).pk,
                object_id       = newa.pk,
                object_repr     = smart_text(newa),
                action_flag     = ADDITION,
                change_message  = 'Achievement automatically unlocked'
            )
            return {'msg': 'Achievement unlocked', 'image':"%s" % badge.image, 'code': messages.SUCCESS }
        except:
            return {'msg' : 'Achievement save error', 'image':"%s" % badge.image, 'code': messages.ERROR }
    else:
        return {'msg' : 'Already has this badge', 'image': '', 'code': messages.WARNING }

def dictconv(data,ref):
    tmp = []
    for i in ref:
        try:
            tmp.append(data[i])
        except:
            tmp.append(0.)
    return tmp
