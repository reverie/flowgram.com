from django.contrib import auth
from django.http import HttpResponseRedirect

from flowgram import settings
from flowgram.core import controller, forms, helpers
from flowgram.core.require import require
from flowgram.core.response import data_response


@require(None, ['enc=html'])
def login(request, enc):
    next = request.GET.get('next', '/')

    if request.user.is_authenticated():
        return helpers.redirect(next)
    
    next_greeting = ''
    if next.find('create') >= 0:
        next_greeting = "Please login or register to get started making Flowgrams. It's quick and easy!"
    elif next.find('subscribe') >= 0:
        next_greeting = "Please login or register to subscribe to a user. It's quick and easy!"
    
    if request.method == 'POST':
        succeeded = False
        form = forms.LoginForm(request.POST)

        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password'])
            assert(user)
            auth.login(request, user)
            request.session[settings.PERSISTENT_SESSION_KEY] = form.cleaned_data['remember_user']
            succeeded = True

        if not succeeded:
            request.session['processed_login_form'] = form.as_p()
            controller.record_stat(request, 'view_login_website', '0', 'unsuccessful')
            return HttpResponseRedirect('/login')

        next = request.POST.get('next', '')
        if next:
            controller.record_stat(request,
                                   'view_login_website',
                                   '0',
                                   'successful, next url = %s' % next)
            return helpers.redirect(next)

        controller.record_stat(request, 'view_login_website', '0', 'successful, next url = /')
        return HttpResponseRedirect('/')
    else:
        form = forms.LoginForm()
        reg_form = forms.RegistrationFormStep1()
        return helpers.req_render_to_response(request,
                                              'login/login.html',
                                              {'next': next,
                                               'next_greeting': next_greeting,
                                               'reg_form': reg_form,
                                               'which_form_reg': 'register_step_1'})


def my_logout(request):
    controller.record_stat(request, 'view_logout_website', '0', '')
    auth.logout(request)
    if request.GET.get('redirect', 'true').lower() == 'true':
        return helpers.go_back(request)
    else:
        return data_response.create(request.POST.get('enc', 'json'), 'ok', {})
