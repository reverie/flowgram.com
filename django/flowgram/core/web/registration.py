import random

from django.contrib import auth
from django.contrib.auth import models as auth_models
from django.http import HttpResponseRedirect

from flowgram import localsettings
from flowgram.core import avatar, controller, helpers, log, models
from flowgram.core.forms import AvatarForm
from flowgram.core.require import require


@require(None, ['enc=html', 'next=/'])
def register(request, enc, next):
    from flowgram.core.forms import RegistrationForm

    default_avatar = random.choice(avatar.BUILTIN_AVATARS)
    default_avatar_url = avatar.builtin_avatar_url(default_avatar, 32)
    
    context = {
        'avatar_name' : default_avatar,
        'avatar_url' : default_avatar_url,
        'builtin_avatars' : avatar.BUILTIN_AVATARS,
        'use_regcode': localsettings.FEATURE['use_regcode'],
    }

    avatar_form = AvatarForm()
    if request.method == 'GET':
        controller.record_stat(request, 'view_register', '0', '')
        context.update({'form': RegistrationForm(),
                        'avatar_form': avatar_form,
                        'next': next,
                        'next_greeting': ''})
        return helpers.req_render_to_response(request, 'register/register.html', context)

    registration_form = RegistrationForm(request.POST)
    
    if not registration_form.is_valid():
        controller.record_stat(request, 'view_register', '0', 'form errors')
        context.update({'form': registration_form,
                        'avatar_form': avatar_form,
                        'next': next})
        return helpers.req_render_to_response(request, 'register/register.html', context)

    # Registration successful:
    # Create new user
    data = registration_form.cleaned_data

    return complete_registration(request, next, data)


@require('POST', ['enc=html', 'next=/', 'which_form'])
def register_steps(request, enc, next, which_form):
    from flowgram.core.forms import LoginForm, RegistrationFormStep1, RegistrationFormStep2

    next_greeting = ''
    if next.find('create') >= 0:
        next_greeting = 'Please login or register to get started making Flowgrams. It\'s quick and easy!'
    elif next.find('subscribe') >= 0:
        next_greeting = 'Please login or register to subscribe to a user. It\'s quick and easy!'
    
    form = LoginForm()

    default_avatar = random.choice(avatar.BUILTIN_AVATARS)
    default_avatar_url = avatar.builtin_avatar_url(default_avatar, 32)

    # register step 1
    if which_form == 'register_step_1':
        reg_form = RegistrationFormStep1(request.POST)
        
        # Reg step 1 data is bad
        if not reg_form.is_valid():
            controller.record_stat(request, 'view_register_step_1', '0', 'form errors')
            context = {'reg_form': reg_form,
                       'form' : form,
                       'next': next,
                       'next_greeting': next_greeting,
                       'which_form_reg': 'register_step_1'}
            return helpers.req_render_to_response(request, 'login/login.html', context)
        # Reg step 1 data is good, keep data and set up for step 2
        else:
            controller.record_stat(request, 'view_register_step_1', '0', 'success')
            context = {'form': RegistrationFormStep2(),
                       'next': next,
                       'next_greeting': next_greeting,
                       'which_form_reg': 'register_step_2',
                       'username': request.POST.get('username'),
                       'password1': request.POST.get('password1'),
                       'password2': request.POST.get('password2'),
                       'avatar_form': AvatarForm(),
                       'avatar_name' : default_avatar,
                       'avatar_url' : default_avatar_url,
                       'builtin_avatars' : avatar.BUILTIN_AVATARS}
            return helpers.req_render_to_response(request, 'register/register_step_2.html', context)
    # register_step_2
    else:
        form = RegistrationFormStep2(request.POST)
        
        # Reg step 2 data is bad
        if not form.is_valid():
            controller.record_stat(request, 'view_register_step_2', '0', 'form errors')
            context = {'form': form,
                       'next': next,
                       'next_greeting': next_greeting,
                       'which_form_reg': 'register_step_2',
                       'username': request.POST.get('username'),
                       'password1': request.POST.get('password1'),
                       'password2': request.POST.get('password2'),
                       'avatar_form': AvatarForm(),
                       'avatar_name' : default_avatar,
                       'avatar_url' : default_avatar_url,
                       'builtin_avatars' : avatar.BUILTIN_AVATARS}
            return helpers.req_render_to_response(request, 'register/register_step_2.html', context)
        # Reg step 2 data is good, create account and continue
        else:
            controller.record_stat(request, 'view_register_step_2', '0', 'success')
            
            data = form.cleaned_data
            data['username'] = request.POST.get('username')
            data['password1'] = request.POST.get('password1')

            return complete_registration(request, next, data)


@require('GET', ['enc=html', 'next'])
def reg_success(request, enc, next):
    return helpers.req_render_to_response(request, 'register/reg_success.html', {'next': next})


@require(None, ['enc=html', 'name=', 'email=', 'how=', 'comment='])
def request_regcode(request, enc, name, email, how, comment):
    from flowgram.queueprocessors.sendemailrequestprocessor import add_to_mail_queue

    if request.method != 'POST':
        return HttpResponseRedirect('/register/')

    if email or comment:
        log.debug("send_mail from request_regcode to chris and tony")        
        add_to_mail_queue(
            'mailman@flowgram.com',
            'regrequests@flowgram.com',
            'Request for regcode',
            '%s <%s> requests a regcode, saying "%s".  Heard about us from: "%s"' % \
                (name, email, comment, how))
    helpers.add_good_message(
        request,
        "Thanks for signing up for our private beta. Keep your eye out for a registration code from us.")
    return HttpResponseRedirect('/register/')


# HELPERS-------------------------------------------------------------------------------------------


def complete_registration(request, next, data):
    new_user = auth_models.User.objects.create_user(data['username'],
                                                    data['email'],
                                                    data['password1'])

    new_profile = models.UserProfile.objects.create(
        user=new_user,
        gender=data['gender'],
        newsletter_optin=data['newsletter_optin'],
        birthdate=data['birthdate'],
        description=data['description'],
        homepage=data['homepage'])
    subscription = models.EmailSubscriptionRequest.objects.create(
        should_subscribe=new_profile.newsletter_optin,
        email_address=new_user.email)
    log.info(subscription.should_subscribe)
    log.info(subscription.email_address)

    new_user = auth.authenticate(username=data['username'], password=data['password1'])
    auth.login(request, new_user)
    controller.record_stat(request, 'add_user_website', '0', '')

    # Mark registration code as used
    if localsettings.FEATURE['use_regcode']:
        regcode = data['registration_code']
        regcode.user = new_user
        regcode.used = True
        regcode.count = regcode.count - 1
        regcode.save()

    # Handle avatar
    avatar_form = AvatarForm(request.POST, request.FILES)
    if avatar_form.is_valid():
        avatar.save_uploaded_avatar(new_profile, avatar_form)
    else:
        avatar.save_builtin_avatar(new_profile, request.POST.get('builtin_avatar_name'))

    if next == '/create/':
        return HttpResponseRedirect('/reg_success/create/')

    helpers.add_good_message(request, "Your account was created.  Welcome to Flowgram!")

    return HttpResponseRedirect(next if next != '/' else new_profile.url() + "/new_fg_user")
