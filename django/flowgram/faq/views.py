from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from flowgram.core.decorators import authorized
from django.views.decorators.vary import vary_on_headers
from django.conf import settings
from flowgram.core import log, controller
from flowgram.core.helpers import req_render_to_response
from flowgram.faq.models import Category, Question

@authorized
def help(request):
    
    category_list = Category.objects.all()
    controller.record_stat(request, 'view_help_website', '0', 'help index')
    return req_render_to_response(request, 'help/help.html', {
        'category_list': category_list,
    })

def help_article(request, question_id):

    question = Question.objects.get(id=question_id)
    controller.record_stat(request, 'view_help_website', '0', question_id)
    return req_render_to_response(request, 'help/help_article.html', {
        'question': question,
    })