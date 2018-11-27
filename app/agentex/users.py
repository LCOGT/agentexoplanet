from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context
from django.template.loader import get_template
from django.urls import reverse
from django.conf import settings
from django.db.models import Count

from agentex.models import *
from agentex.forms import RegisterForm, CommentForm, RegistrationEditForm
from agentex.datareduc import personcheck

def briefing(request):
    #return render_to_response('agentex/briefing.html', context_instance=RequestContext(request))
    return render(request, 'agentex/briefing.html', {})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        # Check if User has already registered with same username or email address
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'],form.cleaned_data['emailaddress'],form.cleaned_data['password'])
            user.first_name=form.cleaned_data['firstname']
            user.last_name=form.cleaned_data['lastname']
            user.save()
            messages.success(request,"Your account has been created")
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password'])
            login(request, new_user)
            next = request.GET.get('next','')
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('index'))
        else:
            #return render_to_response("register.html",{'form': form},context_instance=RequestContext(request))
            return render(request, 'agentex/register.html', {'form': form})
    else:
        #return render_to_response("register.html",{'form': RegisterForm()},context_instance=RequestContext(request))
        return render(request, 'agentex/register.html', {'form': RegisterForm()})


@login_required
def editaccount(request):
    p = personcheck(request)
    if request.method == 'POST':
        form = RegistrationEditForm(request.POST)
        # Check if User has already registered with same username or email address
        user = p.user
        if form.is_valid():
            f = form.cleaned_data
            user.first_name=f['firstname']
            user.last_name=f['lastname']
            user.email=f['emailaddress']
            password =f['password']
            if password:
                user.set_password(password)
            user.save()
            messages.success(request,"Your account has been updated")
        # data = {'firstname' : p.user.first_name,'lastname' : p.user.last_name,'emailaddress':p.user.email,'password':p.user.password,'username':p.user.username}
        #return render_to_response("register.html",{'form': form,'edit':True},context_instance=RequestContext(request))
        return render(request, 'agentex/register.html', {'form': form,'edit':True})
    else:
        form = RegistrationEditForm({'firstname' : p.first_name,'lastname' : p.last_name,'emailaddress':p.email,'password':p.password})
        #return render_to_response("register.html",{'form': form,'edit':True},context_instance=RequestContext(request))
        return render(request, 'agentex/register.html', {'form': form,'edit':True})

@login_required
def profile(request):
    a = Achievement.objects.filter(person=request.user).order_by('badge')
    nomeas = Datapoint.objects.filter(user=request.user).values('taken').annotate(Count('taken')).count()
    noplanet = DataCollection.objects.filter(person=request.user).values('planet').annotate(Count('person')).count()
    completed = DataCollection.objects.values('planet').filter(person=request.user).annotate(Count('complete')).count()
    #ndecs = Decision.objects.filter(person=request.user,planet=d[0].event,current=True).count()
    badgelist = Badge.objects.exclude(id__in=[b.badge.id for b in a]).order_by('name')
    #return render_to_response("agentex/profile.html",{'unlocked':a,'badges':badgelist,'planets':noplanet,'measurements':nomeas,'completed':completed},context_instance=RequestContext(request))
    return render(request, 'agentex/profile.html', {'unlocked':a,'badges':badgelist,'planets':noplanet,'measurements':nomeas,'completed':completed})

@login_required
def feedback(request):
    form_class = CommentForm

    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            form_content = request.POST.get('comment', '')

            # Email the profile with the
            # contact information
            contact_email = request.user.email
            template = get_template('agentex/email_comments.txt')
            context = Context({
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'content': form_content,
            })
            content = template.render(context)

            email = EmailMessage(
                "Agent Exoplanet: Feedback from {} {}".format(request.user.first_name, request.user.last_name),
                content,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_REPLYTO],
                headers = {'Reply-To': contact_email }
            )
            email.send()
            messages.success(request,"Your comments have been sent to the administrator")
            return redirect(reverse('index'))

    return render(request, 'agentex/comments_box.html', {
        'form': form_class,
    })

def addcomment(request):
# Log user comments in the Django log
    if request.POST:
        message = request.POST.get('comment','')
        if message:
            if request.user.is_authenticated():
              userid = request.user.pk
              email = request.user.email
            else:
              userid = 1
              email = request.POST.get('emailaddress','')
              message = "%s : %s" % (message,email)

            # Attach the comment to User content type pk = 3
            contentpk = 3
            LogEntry.objects.log_action(
                user_id         = userid,
                content_type_id = contentpk,
                object_id       = userid,
                object_repr     = smart_unicode(User.objects.get(id=userid)),
                action_flag     = ADDITION,
                change_message  = message,
            )
            messages.success(request,'Thank you for your comments!')
            data = {'emailaddress' : email,'comment':' '}
            form = CommentForm()
        else:
            form = CommentForm(request.POST)
    else:
        if request.user.is_authenticated():
          data = {'emailaddress' : request.user.email,'comment':' '}
          form = CommentForm(data)
        else:
            form = CommentForm()
    #return render_to_response('agentex/comments_box.html', {'form':form}, context_instance=RequestContext(request))
    return render(request, 'agentex/comments_box.html', {'form':form})
