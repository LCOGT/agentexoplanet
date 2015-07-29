## Find all the Decision objects with the wrong sources
decs = Decision.objects.filter(planet__name='qatar1b')
for dec in decs:
    c = dec.source
    cats = CatSource.objects.filter(xpos__lt=c.xpos+5,ypos__lt=c.ypos+5,xpos__gt=c.xpos-5,ypos__gt=c.ypos-5,data__event__name='qatar1b')
    if cats:
        c = cats[0]
        dec.save()
        print dec.person.username, dec.current, c.name
        
ds = Datapoint.objects.filter(data__id=976,pointtype='S')
users = [d.user for d in ds]
def update_calibrators(users):
    for u in users:
        dc =  DataCollection.objects.filter(person=u,planet__name='qatar1b')
        for c in Datapoint.objects.filter(data__id=976,pointtype='C',user=u):
            cats = CatSource.objects.filter(xpos__lt=c.xpos+5,ypos__lt=c.ypos+5,xpos__gt=c.xpos-5,ypos__gt=c.ypos-5,data__event__name='qatar1b')
            if cats:
                c.coorder.source = cats[0]
                c.coorder.save()
                print u, c.coorder.source, c.coorder.calid
            else:
                print u, "no catalogue source found", c.coorder.calid
