from django.contrib.auth import models as auth_models
from django.http import Http404, HttpResponseRedirect

from flowgram.core import forms, helpers, models
from flowgram.core.require import require


@require(None, ['enc=html'], ['login'])
def change_password(request, enc):
    if request.method == 'GET':
        return helpers.req_render_to_response(request,
                                              'user/change_password.html',
                                              {'form': forms.ChangePasswordForm()})

    form = forms.ChangePasswordForm(request.POST)
    if form.is_valid():
        request.user.set_password(form.cleaned_data['password1'])
        request.user.save()
        return helpers.req_render_to_response(request,
                                              'user/change_password_done.html',
                                              {'created': True,
                                               'username': request.user.username})

    return helpers.req_render_to_response(request, 'user/change_password.html', {'form': form})


@require(None, ['enc=html', 'user=', 'key='])
def reset_password_makenew(request, enc, user, key):
    from flowgram.core.mail import validate_password_reset_hash

    if request.method == 'POST':
        if not validate_password_reset_hash(user, key):
            raise Http404
        new_password = request.POST['new_password']
        user.set_password(new_password)
        user.save()
        helpers.add_good_message(request, "Your new password was set.")
        return HttpResponseRedirect('/you/')

    if not user or not key:
        helpers.add_bad_message(request,
                                "Please make sure you copied the whole URL from your email.")
        return HttpResponseRedirect('/reset/')

    if not validate_password_reset_hash(user, key):
        helpers.add_bad_message(
            request,
            'Please make sure you copied the whole URL from your email. If the email is more than one day old, request a new email on this page.')
        return HttpResponseRedirect('/reset/')

    return helpers.req_render_to_response(request,
                                          'user/enter_new_password.html',
                                          {'user': user,
                                           'key': key})


@require('POST', ['enc=html', 'username=', 'email='])
def reset_password_post(request, enc, user, email):
    from flowgram.core.mail import reset_password

    if email:
        try:
            user = auth_models.User.objects.get(email=email)
        except auth_models.User.DoesNotExist:
            helpers.add_bad_message(request, "No account was found for that email address.")
            return helpers.req_render_to_response(request, 'user/reset_password.html')
    
    if not user:
        helpers.add_bad_message(request, "You must enter your username or email.")
        return helpers.req_render_to_response(request, 'user/reset_password.html')
        
    if reset_password(user):
        helpers.add_good_message(request, "Your password reset email has been sent. Follow the emailed instructions.")
        return helpers.req_render_to_response(request, 'user/reset_password.html')
    else:
        helpers.add_bad_message(request, "We were unable to reach your account email address.")
        return helpers.req_render_to_response(request, 'user/reset_password.html')
