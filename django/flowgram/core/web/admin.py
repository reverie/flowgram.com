import time, datetime, os

from django.http import Http404, HttpResponseRedirect

from flowgram import localsettings
from flowgram.core import cached_sets, forms, helpers, models, webhelpers
from flowgram.core.require import require

from django.conf import settings


# --------------------------------------------------------------------------------------------------
DEFAULT_INVITATION = """Hi,

You are invited to Flowgram.

To see what we've been working on, go to %s and sign up.

You'll be able to see a bunch of Flowgrams and get a sense of how they are useful. 
You can also make your own Flowgrams which can be private (you control who sees them) or public.

See you there!

-""" % (localsettings.my_URL_BASE + 'register/')
# --------------------------------------------------------------------------------------------------

@require(None, ['enc=html','file_to_delete='], ['staff'])
def admin_files(request, enc, file_to_delete):
    form = forms.AdminFilesForm()
    root_url = localsettings.INTERNAL_MEDIA_URL
    dirlist = os.listdir(localsettings.INTERNAL_MEDIA_ROOT)
    
    if request.method == 'POST':
        form = forms.AdminFilesForm(request.POST, request.FILES)
        if form.is_valid():
            filename_prefix = form.cleaned_data['filename_prefix']
            file = request.FILES['image']
            content = file['content']
            content_type = file['content-type']
            file_extension = ''
            if content_type == 'image/png':
                file_extension = '.png'
            elif content_type == 'image/jpeg':
                file_extension = '.jpg'
            elif content_type == 'image/gif':
                file_extension = '.gif'
            filename = filename_prefix + '_' + str(int(time.mktime(datetime.datetime.now().timetuple()))) + file_extension
            f = open(localsettings.INTERNAL_MEDIA_ROOT + filename, 'wb')
            f.write(content)
            f.close()
            file_path = localsettings.INTERNAL_MEDIA_URL + filename
            helpers.add_good_message(request, "Image upload successful.  Filepath is: %s" % file_path)
        else:
            helpers.add_bad_message(request, "There was a problem.  sadtrombone.com")
        
        # refresh directory listing
        dirlist = os.listdir(localsettings.INTERNAL_MEDIA_ROOT)
        
        return helpers.req_render_to_response(
            request,
            "admin/admin_files.html",
            {
                'form': form,
                'dirlist': dirlist,
                'root_url': root_url,
            })
    
    # request.method == 'GET'
    counter = 0
    if file_to_delete != '': # deleting file
        file_to_delete = int(file_to_delete)
        for filename in dirlist:
            if file_to_delete == counter:
                os.remove(localsettings.INTERNAL_MEDIA_ROOT + filename)
                # refresh directory listing
                dirlist = os.listdir(localsettings.INTERNAL_MEDIA_ROOT)
                helpers.add_good_message(request, "You deleted a file: %s" % filename)
                return HttpResponseRedirect('/adminfiles/')   
            counter += 1
        
    # refresh directory listing
    dirlist = os.listdir(localsettings.INTERNAL_MEDIA_ROOT)

    return helpers.req_render_to_response(
        request,
        "admin/admin_files.html",
        {
            'form': form,
            'dirlist': dirlist,
            'root_url': root_url,
        })


# TODO(westphal): Break-up these methods into multiple, smaller methods.
# TODO(westphal): Clean up the naming convention used in this file.


@require(None, ['enc=html'], ['staff'])
def admin_featured(request, enc):
    area = int(request.GET.get('area', 0))

    if request.method == 'POST':
        form = request.POST['form']
        if form == 'create_new':
            fgid = request.POST['id']
            rank = float(request.POST['rank'])
            area = int(request.POST['area'])
            try:
                fg = models.Flowgram.objects.get(id=fgid)
            except models.Flowgram.DoesNotExist:
                models.add_bad_message(request, "Invalid Flowgram ID %s" % fgid)
            else:
                models.Featured.objects.create(area=area, flowgram=fg, rank=rank)
        elif form == 'modify':
            to_delete = []
            for (key, value) in request.POST.items():
                if key.find('__') == -1:
                    continue
                (feat_id, attr) = key.split('__')
                feat = models.Featured.objects.get(id=feat_id)
                if attr == 'id':
                    fgid = value
                    if not fgid:
                        to_delete.append(feat)
                        continue
                    try:
                        fg = models.Flowgram.objects.get(id=fgid)
                    except models.Flowgram.DoesNotExist:
                        models.add_bad_message(request, "Invalid Flowgram ID %s" % fgid)
                        break
                    feat.flowgram = fg
                    feat.save()
                elif attr == 'pri':
                    feat.rank = float(value)
                    feat.save()
                else:
                    raise Http500
            for feat in to_delete:
                feat.delete()
        else:
            raise Http500
    featured = models.Featured.objects.filter(area=area)
    return helpers.req_render_to_response(
        request,
        "admin/admin_featured.html",
        {
            'featured':featured,
            'area': area,
            'areas': models.FEATURED_AREAS,
        })


@require(None, ['enc=html'], ['staff'])
def admin_newest(request, enc):
    return webhelpers.flowgram_lister(request,
                                      enc='html',
                                      queryset=cached_sets.admin_newest(),
                                      template_name='admin/admin_newest.html',
                                      extra_context={
                                          'mostviewed' : cached_sets.most_viewed()[:6],
                                          'displayAdminTools': True,
                                          'fg_timestamp': True,
                                      })
 
 
@require(None, ['enc=html', 'current_poll_id='], ['staff'])
def admin_polls(request, enc, current_poll_id):
    polls = models.FlowgramPoll.objects.filter().order_by('-date_created')
    
    if request.method == 'GET':
        if not current_poll_id == '':
            current_poll = models.FlowgramPoll.objects.get(id=current_poll_id)
            (fg1, fg2, fg3) = models.Flowgram.objects.filter(id__in=[current_poll.candidate_id_1,
                                                                     current_poll.candidate_id_2,
                                                                     current_poll.candidate_id_3])
            
            return helpers.req_render_to_response(
                request,
                'admin/admin_polls.html',
                {
                    'current_poll': current_poll,
                    'current_poll_id': current_poll_id,
                    'fg1': fg1,
                    'fg2': fg2,
                    'fg3': fg3,
                })
        else:
            return helpers.req_render_to_response(request, 'admin/admin_polls.html', {'polls': polls})
    elif request.method == 'POST':
        form = request.POST['form']
        if form == 'create_new':
            poll_short_name = request.POST['poll_short_name']
            poll_title = request.POST['poll_title']
            candidate_id_1 = request.POST['candidate_id_1']
            candidate_id_2 = request.POST['candidate_id_2']
            candidate_id_3 = request.POST['candidate_id_3']

            had_exception = False

            try:
                fg = models.Flowgram.objects.get(id=candidate_id_1)
            except models.Flowgram.DoesNotExist:
                had_exception = True
                models.add_bad_message(
                    request,
                    "Candidate ID 1 is invalid.  Please try again, cheeto-breath.")

            try:
                fg = models.Flowgram.objects.get(id=candidate_id_2)
            except models.Flowgram.DoesNotExist:
                had_exception = True
                models.add_bad_message(
                    request,
                    "Candidate ID 2 is invalid.  Please try again, cheeto-breath.")

            try:
                fg = models.Flowgram.objects.get(id=candidate_id_3)
            except models.Flowgram.DoesNotExist:
                had_exception = True
                models.add_bad_message(
                    request,
                    "Candidate ID 3 is invalid.  Please try again, cheeto-breath.")

            if had_exception:
                return helpers.req_render_to_response(
                    request,
                    'admin/admin_polls.html', {
                        'polls': polls,
                        'poll_short_name': poll_short_name,
                        'poll_title': poll_title,
                        'candidate_id_1': candidate_id_1,
                        'candidate_id_2': candidate_id_2,
                        'candidate_id_3': candidate_id_3,
                    })
                
            poll_active = request.POST['poll_active_hidden'].lower() == 'true'
            
            models.FlowgramPoll.objects.create(poll_short_name=poll_short_name,
                                               poll_title=poll_title,
                                               candidate_id_1=candidate_id_1,
                                               candidate_id_2=candidate_id_2,
                                               candidate_id_3=candidate_id_3,
                                               poll_active=poll_active)
            helpers.add_good_message(request, "You created a new poll called %s." % poll_title)
                
            return helpers.req_render_to_response(request, 'admin/admin_polls.html', {'polls': polls})
        elif form == 'modify':
            current_poll = models.FlowgramPoll.objects.get(id=request.POST['poll_id'])
            current_poll.poll_short_name = request.POST['poll_short_name']
            current_poll.poll_title = request.POST['poll_title']
            current_poll.candidate_id_1 = request.POST['candidate_id_1']
            current_poll.candidate_id_2 = request.POST['candidate_id_2']
            current_poll.candidate_id_3 = request.POST['candidate_id_3']
            current_poll_id = request.POST['current_poll_id']

            had_exception = False

            try:
                fg = models.Flowgram.objects.get(id=current_poll.candidate_id_1)
            except models.Flowgram.DoesNotExist:
                had_exception = True
                models.add_bad_message(request, "Candidate ID 1 is invalid.")

            try:
                fg = models.Flowgram.objects.get(id=current_poll.candidate_id_2)
            except models.Flowgram.DoesNotExist:
                had_exception = True
                models.add_bad_message(request, "Candidate ID 2 is invalid.")

            try:
                fg = models.Flowgram.objects.get(id=current_poll.candidate_id_3)
            except models.Flowgram.DoesNotExist:
                had_exception = True
                models.add_bad_message(request, "Candidate ID 3 is invalid.")
            
            if had_exception:
                return HttpResponseRedirect('/adminpolls/%s' % current_poll_id)
            
            current_poll.poll_active = request.POST['poll_active_hidden'].lower() == 'true'
            current_poll.save()
            
            helpers.add_good_message(request, "You modified the poll called %s." % current_poll.poll_title)
            
            return helpers.req_render_to_response(request, 'admin/admin_polls.html', {'polls': polls})


@require(None, ['enc=html', 'current_press_id='], ['staff'])
def admin_press(request, enc, current_press_id):
    press_list = models.FlowgramPress.objects.filter().order_by('-link_date')
    fgpr_press_list = press_list.filter(press_category='R')
    featured_press_list = press_list.filter(press_category='F')
    more_press_list = press_list.filter(press_category='M')
    
    if request.method == 'GET':
        if not current_press_id == '':
            current_press_item = models.FlowgramPress.objects.get(id=current_press_id)

            fpf = forms.FlowgramPressForm(initial={
                    'link_date': current_press_item.link_date,
                    'link_text': current_press_item.link_text,
                    'link_url': current_press_item.link_url,
                    'lede_text': current_press_item.lede_text,
                    'full_text': current_press_item.full_text,
                    'press_category': current_press_item.press_category,
                })

            return helpers.req_render_to_response(
                request,
                'admin/admin_press.html',
                {
                    'current_press_item': current_press_item,
                    'fpf': fpf,
                })
    elif request.method == 'POST':
        form = request.POST['form']
        f = forms.FlowgramPressForm(request.POST)
        if form == 'create_new':
            if f.is_valid():
                cleaned = f.cleaned_data
                models.FlowgramPress.objects.create(link_date=cleaned['link_date'],
                                                    link_text=cleaned['link_text'],
                                                    link_url=cleaned['link_url'],
                                                    lede_text=cleaned['lede_text'],
                                                    full_text=cleaned['full_text'],
                                                    press_category=cleaned['press_category'])

                helpers.add_good_message(
                    request,
                    "You created a new press item.  Good for you, cheeto-fingers.")
        elif form == 'modify':
            current_press_item = models.FlowgramPress.objects.get(id=request.POST['press_id'])
            f = forms.FlowgramPressForm(request.POST)
            if f.is_valid():
                cleaned = f.cleaned_data
                current_press_item.link_date = cleaned['link_date']
                current_press_item.link_text = cleaned['link_text']
                current_press_item.link_url = cleaned['link_url']
                current_press_item.lede_text = cleaned['lede_text']
                current_press_item.full_text = cleaned['full_text']
                current_press_item.press_category = cleaned['press_category']
                current_press_item.save()

                helpers.add_good_message(
                    request,
                    "You modified a press item.  Good for you, cheeto-fingers.")
            
    fpf = forms.FlowgramPressForm()
        
    return helpers.req_render_to_response(
        request,
        'admin/admin_press.html',
        {
            'press_list': press_list,
            'fgpr_press_list': fgpr_press_list,
            'featured_press_list': featured_press_list,
            'more_press_list': more_press_list,
            'fpf': fpf,
        })


@require(None, ['enc=html', 'current_press_id='], ['staff'])
def delete_press(request, enc, current_press_id):
    if request.method == 'GET':
        return helpers.req_render_to_response(
            request,
            'dialogs/delete_press.html',
            {'current_press_item': models.FlowgramPress.objects.get(id=current_press_id)})
    else:    
        models.FlowgramPress.objects.get(id=current_press_id).delete()
        helpers.add_good_message(request, "You deleted a press item.  Congratulations.")
        return HttpResponseRedirect('/adminpress')


@require(None, ['enc=html', 'recipients=', 'email_body='], ['staff'])
def inviter(request, enc, recipients, email_body):
    from django.template import Context, Template
    from flowgram.queueprocessors.sendemailrequestprocessor import add_to_mail_queue

    if request.method == 'GET':
        context = {'from_email' : request.user.email,
                   'default_email' : DEFAULT_INVITATION + request.user.username}
        return helpers.req_render_to_response(request, 'admin/inviter.html', context)

    for recipient in helpers.get_email_addresses_from_comma_separated_string(recipients):
        context = {}
        if localsettings.FEATURE['use_regcode']:
            context['regcode'] = models.Regcode.objects.create(sender=request.user).code
        # TODO(westphal): Figure out and remove or document: Why are we using unicode and then a 
        #                 non-unicode string.
        body = '%s' % unicode(Template(email_body).render(Context(context)))
        add_to_mail_queue(request.user.email, recipient, "Invitation to Flowgram.com", body)

    helpers.add_good_message(request, 'Emails added to queue.')
    return HttpResponseRedirect('/a/inviter/')
