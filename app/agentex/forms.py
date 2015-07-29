'''
Citizen Science Portal: App containing Agent Exoplant and Show Me Stars for Las Cumbres Observatory Global Telescope Network
Copyright (C) 2014-2015 LCOGT

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''
from django import forms
from types import *
from django.forms import TextInput,Textarea
from django.contrib.auth.models import User

class DataEntryForm(forms.Form):
    sourceradius = forms.CharField(label='Aperture Radius (source)')
    sourcexpos = forms.CharField(label='Source x position')
    sourceypos = forms.CharField(label='Source y position')
    sourcecounts = forms.CharField(label='Source counts')
#    cal1radius = forms.CharField(label='Aperture Radius (calibrator)')
#    cal1xpos = forms.CharField(label='Calibrator x postion')
#    cal1ypos = forms.CharField(label='Calibrator y postion')
#    cal1counts = forms.CharField(label='Calibrator counts')
    bgradius = forms.CharField(label='Aperture Radius (background)')
    bgxpos = forms.CharField(label='Background x position')
    bgypos = forms.CharField(label='Background y position')
    bgcounts = forms.CharField(label='Background counts')
    
class RegisterForm(forms.Form):
    username = forms.CharField(label=u'Choose a username')
    password = forms.CharField(label= u'Password',widget=forms.PasswordInput(render_value=False))
    firstname = forms.CharField(label=u'What should we call you? (e.g. as a greeting)')
    lastname = forms.CharField(label=u'Full Name')
    emailaddress = forms.EmailField(label= u'Contact email address',widget=TextInput(attrs={'size':'60'}))
    
    def clean_username(self):
      username = self.cleaned_data['username']
      try:
          user = User.objects.get(username=username)
      except User.DoesNotExist:
          return username
      raise forms.ValidationError(u'%s already exists' % username )

            
class RegistrationEditForm(forms.Form):
    password = forms.CharField(label= u'Password',widget=forms.PasswordInput(render_value=False),required=False)
    firstname = forms.CharField(label=u'What should we call you? (e.g. as a greeting)')
    lastname = forms.CharField(label=u'Full Name')
    emailaddress = forms.EmailField(label= u'Contact email address',widget=TextInput(attrs={'size':'60'}))
    
class CommentForm(forms.Form):
    emailaddress = forms.EmailField(label= u'Contact email address',widget=TextInput(attrs={'size':'60'}),required=True)
    comment = forms.CharField(label='Comment',max_length=160, help_text='160 characters max.',widget=Textarea(attrs={'rows':4, 'cols':60}),required=True)