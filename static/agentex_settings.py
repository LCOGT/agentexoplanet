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
decision_images = {
    'D':{'name':'Dip','image':'choice_dip.png'},
    'N':{'name':'No Dip','image':'choice_nodip.png'},
    'O':{'name':'Odd','image':'choice_odd.png'},
    'B':{'name':'Blip','image':'choice_blip.png'},
    'P':{'name':'Periodic','image':'choice_periodic.png'},
    'S':{'name':'Noise','image':'choice_noise.png'},
    'R':{'name':'Other','image':'choice_other.png'},
}

planet_level = {
    'corot2b' : 'beginner',
    'ogletr132b' : 'advanced',
}