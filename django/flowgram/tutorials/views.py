
import time, datetime

from django.http import HttpResponseRedirect

from flowgram import settings, localsettings
from flowgram.core import helpers, controller, permissions, s3
from flowgram.core.require import require
from flowgram.core.forms import TutorialForm
from flowgram.tutorials.models import Tutorial
from flowgram.tutorials import tutorialhelpers

@require(None, ['enc=html','tutorial_id='], ['staff'])
def admin_tutorials(request, enc, tutorial_id):
    
    if tutorial_id: # edit existing tutorial
        
        tutorial = Tutorial.objects.get(id=tutorial_id)
        video_path = ''
        
        if request.method == 'POST':
            
            form = TutorialForm(request.POST)
            if form.is_valid():
                cleaned = form.cleaned_data
                tutorial.title = cleaned['title']
                tutorial.position = cleaned['position']
                if cleaned['content']:
                    tutorial.content = cleaned['content']
                else:
                    tutorial.content = ''
                tutorial.active = cleaned['active']
                tutorial.save()
                
                tutorialhelpers.save_uploaded_video(request, tutorial, form)

                helpers.add_good_message(
                    request,
                    "You modified a tutorial.  Congratulations.")
            
            else:
                print 'Some kind of problem with your form entry, try again.'
                
            if tutorial.video_path:
                video_path = tutorialhelpers.get_tutorial_video_path(tutorial)
            
            return helpers.req_render_to_response(
                request,
                "admin/admin_tutorials.html",
                {
                    'form': form,
                    'tutorial_id': tutorial_id,
                    'tutorial': tutorial,
                    'video_path': video_path,
                })
            
        else: # request.method == 'GET'
            form = TutorialForm(initial={
                    'position': tutorial.position,
                    'title': tutorial.title,
                    'content': tutorial.content,
                    'active': tutorial.active,
                })
            
            if tutorial.video_path:
                video_path = tutorialhelpers.get_tutorial_video_path(tutorial)
            
            return helpers.req_render_to_response(
                request,
                "admin/admin_tutorials.html",
                {
                    'form': form,
                    'tutorial_id': tutorial_id,
                    'tutorial': tutorial,
                    'video_path': video_path,
                })
    
    else: # create new tutorial / list existing tutorials
        
        if request.method == 'POST': # create new tutorial
        
            form = TutorialForm(request.POST)
            
            if form.is_valid():
                cleaned = form.cleaned_data
                if cleaned['content']:
                    newcontent = cleaned['content']
                else:
                    newcontent = ''
                current_tutorial = Tutorial.objects.create(position=cleaned['position'],
                                        title=cleaned['title'],
                                        content=newcontent,
                                        active=cleaned['active'])
                                        
                tutorialhelpers.save_uploaded_video(request, current_tutorial, form)

                helpers.add_good_message(
                    request,
                    "You created a new tutorial.  Good for you, cheeto-fingers.")
            
            else:
                print 'Some kind of problem with your form entry, try again.'
            
            form = TutorialForm()
            tutorials = Tutorial.objects.filter().order_by('position')
            
            return helpers.req_render_to_response(
                request,
                "admin/admin_tutorials.html",
                {
                    'form': form,
                    'tutorials': tutorials,
                })
    
        else: # request.method == 'GET'

            form = TutorialForm()
            tutorials = Tutorial.objects.filter().order_by('position')
            
            return helpers.req_render_to_response(
                request,
                "admin/admin_tutorials.html",
                {
                    'form': form,
                    'tutorials': tutorials,
                })
                
@require(None, ['enc=html','tutorial_id='], ['staff'])               
def delete_tutorial(request, enc, tutorial_id):
    tutorial = Tutorial.objects.get(id=tutorial_id)
    if request.method == 'GET':
        return helpers.req_render_to_response(
            request,
            'dialogs/delete_tutorial.html',
            {'tutorial': tutorial,})
    else:
        Tutorial.objects.get(id=tutorial_id).delete()
        helpers.add_good_message(request, "You deleted a tutorial.  Congratulations.")
        return HttpResponseRedirect('/admintutorials')

@require('GET', ['enc=html'], ['authorized'])  
def tutorials_index(request, enc):
    tutorials = Tutorial.objects.filter(active=True).order_by('position')
    return helpers.req_render_to_response(
        request,
        "tutorials/tutorial_index.html",
        {
            'tutorials': tutorials,
        })
        
@require('GET', ['enc=html', 'tutorial_id='], ['authorized'])  
def tutorial(request, enc, tutorial_id):
    tutorial = Tutorial.objects.get(id=tutorial_id)
    video_path = ''
    if tutorial.video_path:
        video_path = tutorialhelpers.get_tutorial_video_path(tutorial)
    return helpers.req_render_to_response(
        request,
        "tutorials/view_tutorial.html",
        {
            'tutorial': tutorial,
            'video_path': video_path,
        })
