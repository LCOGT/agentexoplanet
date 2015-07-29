/*
Copyright (c) 2009, Simon Harrison.

All rights reserved.

    This file is part of django-calendar.

    django-calendar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    django-calendar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with django-calendar.  If not, see <http://www.gnu.org/licenses/>.
*/

var Cal = function(cal){ this.init(cal) } 

Cal.prototype = {

    range:{},
    on:false,               
	trigger:false,
	dates:[],
	
    init:function(cal) {
  		var self = this
		self.behaviour()
    },
	 
    loadRange:function(){
		var t = this
	
        $('#django_calendar').find('td a.on').each(function()
		{
            t.dates.push($(this).attr('href'))
        });

        if(t.dates.length == 1) 
            var url = t.dates[0]
        else 
            var url = t.dates[0] + "" + t.dates[t.dates.length-1]

		if(do_with_ajax)
		{
			url = '/ajax'+url+'/'
			// http://www.solo-technology.com/blog/2006/01/04/me-ajax-and-firefox/
			// i am temporarilly using GET to get past this issue 
			$.ajax({ type: "GET", url: url,
				success:function(response)
				{
					// clear the memory
					t.dates = []
					t.range = {}
					t.behaviour()
					// update whatever HTML you need to
					$('#django_calendar_response').html(response)
				},
				error:function(r)
				{   // this should never be called
					$('#django_calendar_response').html('<p>Unanticipated Error</p>')
				}
			});
		}
		//  or do with a standrad HTTP request for your own apps purpose
		else
			window.location.href = url	
		//	or whatever
    },
	
    date:function(day, month, year){
		var t = this
		//	slighly obscure calendar while we are thinking
		$('#django_calendar').animate({opacity: 0.5}, 500, function() 
		{
			// get HTML for calendar with new date
			$.ajax({ type: "GET", url: "/calendar/update/"+day+"/"+month+"/"+year+"/",
				success:function(response)
				{
					// update HTML
					$('#django_calendar').html(response)
					// add behaviour to buttons
					t.behaviour()
					// remove 'on' class
					$('#django_calendar td.on').each(function() {
						$(this).removeClass('on')
					});
					// reapply to correct element
					$('#django_calendar table td').each(function(){
						// except whitespace in comparisom 
						if($(this).text().replace(/^\s*|\s*$/g,'') == day)
							$(this).addClass('on')
					});			
					//	restore opacity
					$('#django_calendar').animate({opacity: 1}, 50)
				},
				error:function(response)
				{
					// this should NEVER be called
					$('#django_calendar').html('<p>unanticipated error</p>')
				}
			});		
		})
    },
	
	select_forward:function(){
		/* This allows a user to select dates over multiple months
		*/
		
		var t = this
		// put dates so far into the container
		$('#django_calendar').find('td a.on').each(function()
		{
            t.dates.push($(this).attr('href'))
        });
		
		// animate the button. if animation completes, execute
		$('#lastday a').animate( { backgroundColor: 'red' }, 1500, function(){
			if(t.trigger)
			{
				t.trigger = false
				// load next month
				var next = $('#next-m').attr('href') + 'more/'
				$.ajax({ type: "GET", url: next,
					success:function(response)
					{	
						// update HTML
						$('#django_calendar').fadeOut()
						$('#django_calendar').html(response)
						// set the 1st day as selected
						$('#firstday a').addClass('on')
						t.on = true
						t.select_from = $('#firstday a')
						// add behaviour
						t.behaviour()
						$('#django_calendar').fadeIn()
					},
					error:function(r)
					{   // debugging
						$('#django_calendar_response').html('<p>Unanticipated Error</p>')
					}
				});
			}
			else { 
				$(this).removeClass('on') 
				$(this).css('background-color', 'transparent')
			}
		});
	},
	
	behaviour:function(){
	
		var t = this
		
		// ups and downs of dates
		$('.dxhr').each(function () 
		{ 
			$(this).click(function() 
			{
				var date_array = $(this).attr('href').split('/')
				t.date(day=date_array[2],month=date_array[3],year=date_array[4]) 
				return false
			});
		});   
		        
		// grab all the 'a' elements that we need
		var as = $('#django_calendar').find('td a')
		
		// get current months date range
        var count = 0
		// ensure range is clean
		t.range = {}
		as.each(function(){
			// remove default behaviour
			$(this).click(function() { return false })
			// give each td a property 'day' that reflects their position in the grid
            $(this).data('day', count)
            t.range[count] = $(this)
            count++
        })
		// we now have the range of dates for this month

		
		// make a note of the start day
		as.mousedown(function(){
		    // but ensure there are none on already
			$('#django_calendar td a.on').each(function() 
			{
				$(this).removeClass('on')
			});
            t.on = true
			$(this).addClass('on')
            t.select_from = $(this)
            return false
        })
		
		// mouse up can happen anywhere on the page
        $('html').mouseup(function(){

            if(t.on) 
			{ 
                t.on = false
                t.select_to = this
                t.loadRange()
                return false
            }
        })
		
        as.mouseover(function(){
            if(t.on) {
                if($.data(this, 'day') >= t.select_from.data('day')) 
				{
                    var upperlimit = $.data(this, 'day')
                    var lowerlimit = t.select_from.data('day')
                } 
				else 
				{
                    var lowerlimit = $.data(this, 'day')
                    var upperlimit = t.select_from.data('day')
                }
		
                for(var a in t.range)
				{
                    var td = t.range[a]
                    if(a >= lowerlimit && a <= upperlimit)
                        td.addClass('on')
                    else 
						td.removeClass('on')
                }
            }
        })
		
		// special moves on the last day of the month - AJAX only
		$('#lastday').mouseover(function() {
			t.trigger = true
			if(t.on)
				t.select_forward()	
		});
		$('#lastday').mouseout(function() {
			t.trigger = false
		});
    }
}

$(document).ready(function(){
   var cal = new Cal($('#calendar'))
})
