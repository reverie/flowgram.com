import shutil, codecs, Image, cStringIO, urllib2

from flowgram import localsettings, settings
from flowgram.analytics.models import StatRecord
from flowgram.core import log, s3, toolbar, permissions
from flowgram.core.helpers import _mkdir
from flowgram.core.models import Flowgram, UserProfile, UnboundPage, Page, Comment, Tag, ThumbQueue, Highlight, Audio, StatusCode, Favorite, EventType, UserHistory, Subscription
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
#from xml.dom.minidom import parseString

PAGEFILE_ENCODING = "utf-8"
DEFAULT_FG_TITLE = "Untitled"
DEFAULT_FG_DESCRIPTION = ""
DEFAULT_PAGE_TITLE = DEFAULT_FG_TITLE
ZOOM_AND_CROP_WIDE_THUMBS = True

#
# Used internally:
#
		
def set_page_duration(page, duration):
    page.duration = duration
    page.save()
    
    for highlight in page.highlight_set.filter(name=settings.HL_DURATION_NAME):
        highlight.time = duration
        highlight.save()

def set_working_flowgram(user, fg):
    if permissions.can_edit(user, fg):
        profile = user.get_profile()
        profile.working_flowgram_id = fg.id
        
        profile.save()
        
        log.debug("Action log: set_working_flowgram to %s for %s" % (fg.id, str(user.id)))

def set_tags(user, flowgram, tags):
    Tag.objects.filter(flowgram=flowgram).delete()

    for tag in tags:
        stripped_tag = tag.strip()

        if stripped_tag:
            Tag.objects.create(name=stripped_tag, flowgram=flowgram, adder=user)

def deleted_pages_dir():
    return "%s/deleted_pages/" % localsettings.my_WOWKASTDIR
_mkdir(deleted_pages_dir())


def highlighted_page_filename(page):
    return str(page.id) + '_hl.html'

def unbound_page_path(upage):
    """Returns the file unbound page content is stored in."""
    return "%s/unbound_pages/%s.html" % (localsettings.my_WOWKASTDIR, upage.id)

def full_page_path(page):
    return page.flowgram.directory() + page_filename(page)

def add_file_to_flowgram(flowgram, filename, content, encoding=None):
    dir = flowgram.directory()
    _mkdir(dir)
    if encoding is None:
        f = open(dir+filename, 'wb')
    else:
        f = codecs.open(dir+filename, 'wb', encoding)
    f.write(content)
    f.close()

def get_next_position(flowgram):
    """The 1-indexed page position that will become the last position in flowgram"""
    position = 1 + max([p.position for p in Page.objects.filter(flowgram=flowgram)]+[0])
    return position

def page_filename(page):
    return str(page.id)+'.html'

def add_default_time(page):
    page.duration = settings.DEFAULT_DURATION
    page.save()
    
    try:
        # Trying first to update an existing highlight.
        highlight = Highlight.objects.get(page=page.id, name=settings.HL_DURATION_NAME)
        highlight.time = settings.DEFAULT_DURATION
        highlight.save()
    except Highlight.DoesNotExist:
        Highlight.objects.create(name=settings.HL_DURATION_NAME, page=page, time = settings.DEFAULT_DURATION)

def make_thumbnail(page):
    """
    Adds the page to the screenshot queue. Webrenderer will read the page html,
    generate a thumbnail, and then write its path to page.thumb_path directly in the db.
    """
    page.thumb_path = ''
    page.save()
    path = page.flowgram.directory() + page_filename(page)
    type = page.get_type()

    ThumbQueue.objects.create(page=page, path=path, type=type)

def get_file_from_flowgram(flowgram, filename, encoding=None):
    """Returns file contents."""
    #"""Returns open file handle."""
    dir = flowgram.directory()
    path = dir + filename
    if encoding is None:
        f = open(path, 'rb')
    else:
        f = codecs.open(path, 'rb', encoding)
    content = f.read()
    f.close()
    return content 

#
# Used externally:
#

def set_unbound_page_contents(upage, html):
    path = unbound_page_path(upage)
    f = codecs.open(path, 'wb', PAGEFILE_ENCODING)
    f.write(html)
    f.close()

def unbound_page_contents(upage):
    path = unbound_page_path(upage)
    f = codecs.open(path, 'rb', PAGEFILE_ENCODING)
    content = f.read()
    f.close()
    return content

def html_for_static_flex_file(filename):
    from flowgram.localsettings import my_DEV_STATIC_FLEX_MEDIA
    f = codecs.open(my_DEV_STATIC_FLEX_MEDIA + filename, 'rb', PAGEFILE_ENCODING)
    content = f.read()
    f.close()
    return content

def page_contents(page):
    from flowgram.localsettings import my_DEV_STATIC_MEDIA
    
    if page.get_loading_status() == StatusCode.DONE:
        # If the page has been loaded, send the real content.
        
        flowgram = page.flowgram
        filename = page_filename(page)
        return get_file_from_flowgram(flowgram, filename, PAGEFILE_ENCODING)
    else:
        # If the page has not been loaded, send the "processing" temporary content.
    
        htmlfile = 'processingpage.html'
        if page.get_loading_status() == StatusCode.ERROR:
            htmlfile = 'processingerror.html'
        
        f = codecs.open('%s%s' % (my_DEV_STATIC_MEDIA, htmlfile), 'rb', PAGEFILE_ENCODING)
        content = f.read()
        f.close()
        return content

def page_hl_contents(page):
    flowgram = page.flowgram
    filename = highlighted_page_filename(page)
    return get_file_from_flowgram(flowgram, filename, PAGEFILE_ENCODING)

def set_page_contents(page, html, sethl=False):
    flowgram = page.flowgram
    filename = page_filename(page)
    add_file_to_flowgram(flowgram, filename, html, PAGEFILE_ENCODING)
    if sethl:
        filename = highlighted_page_filename(page)
        add_file_to_flowgram(flowgram, filename, html, PAGEFILE_ENCODING)       
    
def set_page_hl_contents(page, html):
    if page.get_loading_status() != StatusCode.DONE:
        return
    
    flowgram = page.flowgram
    filename = highlighted_page_filename(page)
    add_file_to_flowgram(flowgram, filename, html, PAGEFILE_ENCODING)

def delete_page_files(page):
    """Must be called before you unset page.flowgram"""
    flowgram = page.flowgram
    # Move original file
    source_orig = flowgram.directory() + page_filename(page)
    dest_orig = deleted_pages_dir() + page_filename(page)
    try:
        shutil.move(source_orig, dest_orig)
    except IOError:
        pass

    # Move highlighted file
    source_hl = flowgram.directory() + highlighted_page_filename(page)
    dest_hl = deleted_pages_dir() + highlighted_page_filename(page)
    try: 
        shutil.move(source_hl, dest_hl)
    except IOError:
        pass

def undelete_page_files(page, flowgram):  
    # Move original file
    source_orig = flowgram.directory() + page_filename(page)
    dest_orig = deleted_pages_dir() + page_filename(page)
    try:
        shutil.move(dest_orig, source_orig) # like delete_page_files above but args switched
    except IOError:
        pass

    # Move highlighted file
    source_hl = flowgram.directory() + highlighted_page_filename(page)
    dest_hl = deleted_pages_dir() + highlighted_page_filename(page)
    try:
        shutil.move(dest_hl, source_hl)  # like delete_page_files above but args switched
    except IOError:
        pass

def copy_page_to_flowgram(page, flowgram):
    """Returns the new page"""
    src_dir = page.flowgram.directory()
    src_file = page_filename(page)
    src_path = src_dir + src_file

    new_position = get_next_position(flowgram)
    new_page = Page.objects.create( flowgram    = flowgram, 
                                    title       = page.title, 
                                    description = page.description, 
                                    source_url  = page.source_url, 
                                    position    = new_position 
                                    )
    new_page.save()

    dest_dir = flowgram.directory()
    dest_file = page_filename(new_page)
    dest_path = dest_dir + dest_file

    shutil.copy(src_path, dest_path)
    make_thumbnail(new_page)
    add_default_time(new_page)
    return new_page

def deep_copy_page_to_flowgram(page, flowgram):
    # TODO(gobaudd): make a q
    
    """Includes audio, highlights, position, all html..."""
    
    # Create new page object
    new_page = Page.objects.create(flowgram = flowgram,
                                   owner = page.owner,
                                   title = page.title,
                                   description = page.description,
                                   source_url = page.source_url,
                                   duration = page.duration,
                                   position = page.position,
                                   audio_path = page.audio_path,
                                   thumb_path = page.thumb_path,
                                   thumb_dir = page.thumb_dir,
                                   transition_type = page.transition_type,
                                   fade_in = page.fade_in,
                                   fade_out = page.fade_out,
                                   is_custom = page.is_custom,
                                   max_highlight_id_used = page.max_highlight_id_used)

    # Copy highlight objects
    for hl in page.highlight_set.all():
        new_hl = Highlight.objects.create(name = hl.name,
                                          page = new_page,
                                          time = hl.time)
    
    # Copy HTML files
    src_dir = page.flowgram.directory()
    dest_dir = flowgram.directory()

    src_file = page_filename(page)
    src_path = src_dir + src_file
    dest_file = page_filename(new_page)
    dest_path = dest_dir + dest_file
    shutil.copy(src_path, dest_path)

    src_file = highlighted_page_filename(page)
    src_path = src_dir + src_file
    dest_file = highlighted_page_filename(new_page)
    dest_path = dest_dir + dest_file
    
    try:
        shutil.copy(src_path, dest_path)
    except IOError:
        pass
    
    # Copy audio objects and files
    for audio in page.audio_set.all():
        new_audio = Audio.objects.create(page = new_page,
                                         time = audio.time,
                                         path = "s3",
                                         duration = audio.duration
                                        )

        src_key = audio.id + ".flv"
        dest_key = new_audio.id + ".flv"
        s3.copy(localsettings.S3_BUCKET_AUDIO, src_key, localsettings.S3_BUCKET_AUDIO, dest_key)
    
    # copy thumbs
    src_key = page.id + '_full.jpg'
    dest_key = new_page.id + '_full.jpg'
    try:
    	s3.copy(localsettings.S3_BUCKET_THUMB, src_key, localsettings.S3_BUCKET_THUMB, dest_key, "private")
    except NameError:
    	pass
    
    src_key = "%s_%d_%d.jpg" % (page.id, 320, 240)
    dest_key = "%s_%d_%d.jpg" % (new_page.id, 320, 240)
    try:
    	s3.copy(localsettings.S3_BUCKET_THUMB, src_key, localsettings.S3_BUCKET_THUMB, dest_key)
    except NameError:
    	pass
    
    src_key = "%s_%d_%d.jpg" % (page.id, 150, 100)
    dest_key = "%s_%d_%d.jpg" % (new_page.id, 150, 100)
    try:
    	s3.copy(localsettings.S3_BUCKET_THUMB, src_key, localsettings.S3_BUCKET_THUMB, dest_key)
    except NameError:
    	pass
    
    new_page.thumb_path = "s3"
    new_page.thumb_dir = "s3"
    new_page.save()
    
    return new_page

def new_flowgram(owner, title=None):
    if title is None:
        title = DEFAULT_FG_TITLE
    flowgram = Flowgram.objects.create(owner=owner, 
                                    title=title[:255], 
                                    published=False, 
                                    public=False)
    _mkdir(flowgram.directory())
    return flowgram

def get_working_flowgram(user):
    profile = user.get_profile()

    try:
        log.debug("get_working_flowgram for user %s with working_flowgram_id = %s" % (str(user.id), profile.working_flowgram_id))
        
        if profile.just_published and profile.working_flowgram_id != "":
            log.critical("User %s has just_published AND working_flowgram_id = %s." % (user, profile.working_flowgram_id))

        working_flowgram = None
        if profile.working_flowgram_id != "":
            working_flowgram = Flowgram.objects.get(id=profile.working_flowgram_id)

        if profile.just_published or (working_flowgram and not permissions.can_edit(user, working_flowgram)):
            flowgram = new_flowgram(user)
            set_working_flowgram(user, flowgram)
            
            profile.just_published = False
            profile.save()
            
            return (flowgram, True)
    
        if working_flowgram:
            return (working_flowgram, False)
    except Flowgram.DoesNotExist:
        pass

    # Finally, return their latest-modified Flowgram if one exists, or else a new flowgram
    try:
        return (Flowgram.objects.filter(owner=user, published=False).latest('modified_at'), False)
    except Flowgram.DoesNotExist:
        flowgram = new_flowgram(user)
        set_working_flowgram(user, flowgram)
        
        return (flowgram, True)

def create_page_to_flowgram(flowgram, page, html, do_make_thumbnail=True, set_position=True):
    """Expects a page object with title and source_url already set."""
    # TODO(andrew): move functionality into or out of this awkward function?
    
    # put it at the end of the flowgram:
    if set_position:
        page.position = get_next_position(flowgram)

    log.debug("create_page_to_flowgram: " + str(flowgram))
    page.flowgram = flowgram
    page.save()
    
    # save the file:
    filename = page_filename(page)
    add_file_to_flowgram(flowgram, filename, html, PAGEFILE_ENCODING)
    
    # Set the title of the flowgram if this is the first page:
    if flowgram.title == DEFAULT_FG_TITLE:
        flowgram.title = page.title
        flowgram.save()  
                
    
    if do_make_thumbnail:
        make_thumbnail(page)
    add_default_time(page)
    
    return page

def do_bind_page(user, upage, flowgram=None):
    """Binds an unbound page to a specified or default Flowgram"""
    if flowgram is None:
        flowgram, new = get_working_flowgram(user)

    position = get_next_position(flowgram)

    # Create the new page object
    page = Page.objects.create(flowgram=flowgram, 
                    title=upage.title, 
                    source_url= upage.source_url, 
                    position=position)
    make_thumbnail(page)
    add_default_time(page)

    # Copy the html file
    upage_path = unbound_page_path(upage)
    _mkdir(flowgram.directory())
    page_path = full_page_path(page)
    shutil.copy(upage_path, page_path)
    
    # Remove the user's 'just_published' attribute
    profile = user.get_profile()
    profile.just_published = False
    profile.save()

    # Set the title of the flowgram if this is the first page:
    if (flowgram.title == DEFAULT_FG_TITLE) and (position == 1):
        flowgram.title = page.title
        flowgram.save()   

    return (page, flowgram)

def copy_flowgram(user, flowgram):
    new_fg = Flowgram.objects.create(
        #owner = flowgram.owner,
        owner = user,
        title = flowgram.title,
        description = flowgram.description,
        duration = flowgram.duration,
    )

    _mkdir(new_fg.directory())
    
    for page in flowgram.page_set.all():
        deep_copy_page_to_flowgram(page, new_fg)

    return new_fg

def save_thumb_to_s3(page, path):
    i = Image.open(path)
    size = i.size
    
    is_wide_thumb = size[0] > size[1]
    
    thumb = i.copy()
    thumb_filename = "%s_full.png" % (page.id)
    thumbIO = cStringIO.StringIO()
    thumb.save(thumbIO, "png")
    thumbIO.seek(0)
    s3.save_string_to_bucket(localsettings.S3_BUCKET_THUMB, thumb_filename, thumbIO.read(), "public-read", "image/png")
    thumbIO.close()
    
    for dim in settings.THUMB_DIMENSIONS:
        w = dim[0]
        h = dim[1]

        if is_wide_thumb and ZOOM_AND_CROP_WIDE_THUMBS:
            ratio = max(float(h) / size[1], float(w) / size[0])
        else:
            ratio = min(float(h) / size[1], float(w) / size[0])

        new_width = int(size[0] * ratio)
        new_height = int(size[1] * ratio)

        if i.mode == 'RGBA':
            thumb = Image.new('RGBA', (w, h), (255, 255, 255, 255))
        else:
            thumb = Image.new('RGB', (w, h), (255, 255, 255))

        thumbImage = i.resize((new_width, new_height), Image.ANTIALIAS)

        if i.mode == 'RGBA':
            if is_wide_thumb and ZOOM_AND_CROP_WIDE_THUMBS:
                # Cropping from the top, left.
                thumbImage = thumbImage.crop((0, 0, new_width, new_height))
                thumb.paste(thumbImage, (0, 0), thumbImage)
            else:
                thumb.paste(thumbImage, ((w - new_width) / 2, (h - new_height) / 2), thumbImage)
            thumb = thumb.convert('RGB')
        else:
            thumb.paste(thumbImage, ((w - new_width) / 2, (h - new_height) / 2))
        
        thumb_filename = "%s_%d_%d.jpg" % (page.id, w, h)
        thumbIO = cStringIO.StringIO()
        thumb.save(thumbIO, "jpeg", quality=95)
        thumbIO.seek(0)
        s3.save_string_to_bucket(localsettings.S3_BUCKET_THUMB, thumb_filename, thumbIO.read(), "public-read", "image/jpeg")
        thumbIO.close()
    
    page.thumb_path = "s3"
    page.thumb_dir = "s3"
    page.save()


def record_stat(request, type_value, num_value, string_value):	
	# Adding view flowgram to the old analytics db as well.
	if type_value == 'view_flowgram':
		fgid = string_value
		toolbar.record_view(Flowgram.objects.get(id=fgid), request.user, 'F0D')
	elif type_value == 'view_widget_play':
	    fgid = string_value
	    fg = Flowgram.objects.get(id=fgid)
	    fg.views += 1
	    fg.widget_views += 1
	    fg.save()
		
	StatRecord.objects.create(user=request.user if request.user.is_authenticated() else None,
								referrer=request.META.get('HTTP_REFERER', ''),
								ip=request.META.get('REMOTE_ADDR', ''),
								type=type_value,
								num_parameter=num_value,
								string_parameter=string_value)

def get_favorite_fgs_paginated(user, page_size, page_number):
    favorites = Favorite.objects.filter(owner=user)
    num_flowgrams = favorites.count()
    favorites = favorites.order_by('-created_at')[(page_number - 1) * page_size:page_number * page_size]
    
    flowgram_ids = [favorite.flowgram_id for favorite in favorites]
    
    flowgrams = Flowgram.objects.filter(id__in=flowgram_ids)
    return {'num_flowgrams': num_flowgrams, 'flowgrams': flowgrams}


def reponse_non_user_agent(flowgram_id, hash=None):
    fg = get_object_or_404(Flowgram, pk=flowgram_id)
    if not hash == None and hash.find("page_id-") == 0:
        page_id = hash.split("page_id-")[1]
        page = get_object_or_404(Page, pk=page_id)
        if not page.flowgram_id:
            raise Http404
         
        # need to put meta inside <title> tag
        # <meta name="description" content="Flowgram page title: page.title" />
        added_meta = "<meta name=\"description\" content=\"%s\" />" % (page.title or DEFAULT_FG_TITLE)
        pagehtml = page_contents(page)
        newhtml = []
        if pagehtml.find("<head>") >= 0:
            newhtml.append(pagehtml.split("<head>")[0])
            newhtml.append("<head>")
            newhtml.append(added_meta)
            newhtml.append(pagehtml.split("<head>")[1])
            return newhtml
        else:
            return added_meta + pagehtml
 
    tags = Tag.objects.filter(flowgram=fg)
    fghtml = []
    fghtml.append("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n")
    fghtml.append("<html>\n")
    fghtml.append("<head>\n")
    fghtml.append("    <title>%s</title>\n" % (fg.title or DEFAULT_FG_TITLE))
    fghtml.append("    <meta name=\"http-equiv\" content=\"text/html\" charset=\"UTF-8\" />\n")
    fghtml.append("    <meta name=\"description\" content=\"" + fg.description + "\" />\n")
    fghtml.append("    <meta name=\"title\" content=\"" + fg.title + "\" />\n")
    fghtml.append("    <meta name=\"keywords\" content=\"blog post, business, communication, education, facebook, flickr, Flowgram, flowgrams, lecture, literature, photo, photo slideshow , powerpoint, powerpoint sharing, presentation, private message, roundup, sharing, share, slide, slide show, slides, slideshow, technology, tutorial, youtube, ")
    for onetag in tags:
        fghtml.append("%s, " % (onetag.name)) 
    fghtml.append("\" />\n")
    # start to pull out pages
    pages = Page.objects.filter(flowgram=fg)
    comments = Comment.objects.filter(flowgram=fg)
    import re
    matchstr = re.compile(r'<.*?>', re.DOTALL|re.MULTILINE)
    host_page = localsettings.my_URL_BASE + "p/"
    for onepage in pages:
        onepage_url = "%s%s/page_id-%s" % (host_page, fg.id, onepage.id)
        fghtml.append("    <link rel=\"flowpage\" href=\"" + onepage_url + "\" />\n")
        # remove html scrape for now, Google thinks it's spam
        # onepage_sourcehtml = matchstr.sub(" ", page_contents(onepage)).replace('\n', '')
        # fghtml.append("<p>" + onepage_sourcehtml + "</p>")
        # fghtml.append("<h5>from:" + onepage.source_url + "</h5>")
    fghtml.append("</head>\n")
    fghtml.append("<body>\n")
    fghtml.append("<div>\n")
    fghtml.append("    <h1>" + fg.title + "</h1>\n")
    fghtml.append("    <p>" + fg.description + "</p>\n")
    fghtml.append("    <h4>Source urls and notes:</h4>\n")
    fghtml.append("    <ul>\n")
    for onepage in pages:
        fghtml.append("        <li><a href=\"%s\">%s</a></li>\n" % (onepage.source_url,onepage.title))
        fghtml.append("        <p>" + onepage.description +"</p>\n")
    fghtml.append("    </ul>\n\n")
    fghtml.append("    <h5>Posted by %s on: %s</h5>\n" % (fg.owner.username, fg.created_at))
    fghtml.append("    <h4>Comments:</h4>\n")
    fghtml.append("    <ul>\n")
    for onecomment in comments:
        fghtml.append("        <li>%s said on %s:</li>\n" % (onecomment.owner.username, onecomment.created_at))
        fghtml.append("        <p>" + onecomment.text + "</p>\n")
    fghtml.append("    </ul>\n")
    fghtml.append("</div>\n")
    fghtml.append("</body>\n")
    fghtml.append("</html>\n")
    return "".join(fghtml)
    
    
# ========= SUBSCRIPTIONS & NOTIFICATIONS ===============
def store_subscription_event(data):
	""" 
	Stores subscription event in UserHisotry
	"""
	try:
		# Unpack dict
		currentUser = data['user']
		targetUser = data['target_user']
		eventCode = data['eventCode']
		#raw = "%s" % (data)
		flowgramId = "none"
		
		# HTML CODE BUILD
		iconHtmlCode = get_icon_code(eventCode) # Get icon image path + html based on eventCode
		currentUserLink = create_user_link(currentUser) # returns html link to user
		targetUserLink = create_user_link(targetUser) # returns html link to user
		
		# Determine proper message and add html code sets
		if eventCode == "SUB":
			secondPersonPresent = "%s <span>You subscribed to %s.</span>" % (iconHtmlCode,targetUserLink) 
			thirdPersonPast = "%s <span>%s subscribed to %s.</span>" % (iconHtmlCode,currentUserLink,targetUserLink) 
			secondPersonPast = "%s %s subscribed to you." % (iconHtmlCode,currentUserLink) 
		else: #assumes eventCode == "UNSUB"
			secondPersonPresent = "%s <span>You unsubscribed from %s.</span>" % (iconHtmlCode,targetUserLink) 
			thirdPersonPast = "%s <span>%s unsubscribed from %s.</span>" % (iconHtmlCode,currentUserLink,targetUserLink) 
			secondPersonPast = "%s <span>%s unsubscribed from you.</span>" % (iconHtmlCode,currentUserLink) 
		
		# save event obj to UserHistory
		UserHistory.objects.create(currentUser=currentUser,targetUser=targetUser,eventCode=eventCode,flowgramId=flowgramId,thirdPersonPast=thirdPersonPast,secondPersonPast=secondPersonPast,secondPersonPresent=secondPersonPresent)
	except:
		log.debug("Attempted to create (UN)SUB UserHistory event FAILED") # log error
		
def store_fgcomented_event(data):
    """
    Stores Flowgram Commented event in UserHistory
    """
    
    try:
        # Unpack dict
        currentUser = data['commentor']
        eventCode = data['eventCode']
        flowgramIdStr = data['fg_id']
        fg = Flowgram.objects.get(pk=flowgramIdStr)# Get Flowgram info from flowgramID
        
        # if the fg is private, we need to kill this here
        if fg.public == True:
            flowgramTitle = fg.title
            targetUser = fg.owner
        
            # HTML CODE BUILD
            iconHtmlCode = get_icon_code(eventCode) # img icon
            currentUserLink = create_user_link(currentUser) # user link
            targetUserLink = create_user_link(targetUser) # user link
            flowgramLink = create_fg_details_link(flowgramIdStr, flowgramTitle) # fg link
        
            # Determine proper message and add html code sets
            secondPersonPresent = "%s <span>You commented on %s's Flowgram named %s.</span>" % (iconHtmlCode,targetUserLink,flowgramLink) 
            secondPersonPast = "%s <span>%s commented on your Flowgram named %s.</span>" % (iconHtmlCode,currentUserLink,flowgramLink)          
            thirdPersonPast = "%s <span>%s commented on %s's Flowgram named %s.</span>" % (iconHtmlCode,currentUserLink,targetUserLink,flowgramLink) 
        
            # save event obj to UserHistory
            #UserHistory.objects.create(user=commentor,targetUser=target_user,ThirdPersonMsg=ThirdPerson,ThirdPersonYouMsg=ThirdPersonYou,FirstPersonMsg=FirstPerson,rawData=raw)
            UserHistory.objects.create(currentUser=currentUser,targetUser=targetUser,eventCode=eventCode,flowgramId=flowgramIdStr,thirdPersonPast=thirdPersonPast,secondPersonPast=secondPersonPast,secondPersonPresent=secondPersonPresent)
    except:
        log.debug("Attempted to create FG_COMMENTED event FAILED")# log error


def store_fgfaved_event(data):
    """
    Stores Flowgram Favorited event in UserHistory
    """
    try:
        # Unpack dict
        currentUser = data['current_user']
        eventCode = data['eventCode']
        flowgramIdStr = data['fg_id']
        fg = Flowgram.objects.get(pk=flowgramIdStr) 

        # if the fg is private, we need to kill this here
        if fg.public == True:

            # Get Flowgram info from flowgramIdStr
            flowgramTitle = fg.title
            targetUser = fg.owner
        
            # HTML CODE BUILD
            iconHtmlCode = get_icon_code(eventCode) # img icon
            currentUserLink = create_user_link(currentUser) # user link
            targetUserLink = create_user_link(targetUser) # user link
            flowgramLink = create_fg_details_link(flowgramIdStr, flowgramTitle) # fg link
        
            # Determine proper message and add html code sets
            secondPersonPresent = "%s <span>You favorited %s's Flowgram named %s.</span>" % (iconHtmlCode,targetUserLink,flowgramLink) 
            thirdPersonPast = "%s <span>%s favorited %s's Flowgram named %s.</span>" % (iconHtmlCode,currentUserLink,targetUserLink,flowgramLink) 
            secondPersonPast = "%s <span>%s favorited your Flowgram named %s.</span>" % (iconHtmlCode,currentUserLink,flowgramLink)             
        
            # save event obj to UserHistory
            UserHistory.objects.create(currentUser=currentUser,targetUser=targetUser,eventCode=eventCode,flowgramId=flowgramIdStr,thirdPersonPast=thirdPersonPast,secondPersonPast=secondPersonPast,secondPersonPresent=secondPersonPresent)
    
    except:
        log.debug("Attempted to create FG_FAVED UserHistory obj FAILED")# log error



def store_fgtagged_event(data):
    """
    Stores Flowgram Tagged event in UserHistory
    """
    try:
        # Unpack dict
        currentUser = data['current_user']
        eventCode = data['eventCode']
        flowgramIdStr = data['fg_id']
        fg = Flowgram.objects.get(pk=flowgramIdStr) 
        
        # if the fg is private, we need to kill this here
        if fg.public == True:
        
            # Get Flowgram info from fg_id
            flowgramTitle = fg.title
            targetUser = fg.owner
        
            iconHtmlCode = get_icon_code(eventCode) # Get icon html based on eventCode
            currentUserLink = create_user_link(currentUser)
            targetUserLink = create_user_link(targetUser)
            flowgramLink = create_fg_details_link(flowgramIdStr, flowgramTitle) # Get fg html link
            
            # Determine proper message and add html code sets
            secondPersonPresent = "%s <span>You tagged %s's Flowgram named %s.</span>" % (iconHtmlCode,targetUserLink,flowgramLink) 
            thirdPersonPast = "%s <span>%s tagged %s's Flowgram named %s.</span>" % (iconHtmlCode,currentUserLink,targetUserLink,flowgramLink) 
            secondPersonPast = "%s <span>%s tagged your Flowgram named %s.</span>" % (iconHtmlCode,currentUserLink,flowgramLink)            
        
            # save event obj to UserHistory
            UserHistory.objects.create(currentUser=currentUser,targetUser=targetUser,eventCode=eventCode,flowgramId=flowgramIdStr,thirdPersonPast=thirdPersonPast,secondPersonPast=secondPersonPast,secondPersonPresent=secondPersonPresent)
    except Exception:
        log.debug("Attempted to create FG_TAGGED UserHistory obj FAILED")# log error	


def check_fgviews_landmark(user, new_count):
	"""
	Determines if the new flowgram view count causes total views to surpass a set increment 
	if so, store the event in UserHistory
	"""
	# increments taken from views/show_user
	if (new_count == 100) or (new_count == 500) or (new_count == 1000)  or (new_count == 5000) or (new_count == 10000):
		try: # UserHistory: BADGE_FGVIEWS
		    if new_count >= 10000:
		        eventCode = "BADGE_FGVIEWS_10k"
		    elif new_count >= 5000:
		        eventCode = "BADGE_FGVIEWS_5k"
		    elif new_count >= 1000:
		        eventCode = "BADGE_FGVIEWS_1k"
		    elif new_count >= 500:
		        eventCode = "BADGE_FGVIEWS_500"
		    elif new_count >= 100:
		        eventCode = "BADGE_FGVIEWS_100"
		    else:
		        eventCode = "BADGE_FGVIEWS_generic"
		
		    data = {'current_user':user,'fg_views':new_count,'eventCode':eventCode} # Build dict for UserHistory Event
		    store_badge_fgviews_event(data)

		
		except:
			log.debug("attempted to send BADGE_FGVIEWS event to store_badge_fgviews_event -- FAILED")# log error
	


def store_badge_fgviews_event(data):
	"""
	Stores Badge event in UserHistory
	"""
	try:
		# Unpack dict & Get User / Flowgram info
		eventCode = data['eventCode']
		flowgramIdStr = "none"
		flowgramViewsCount = data['fg_views']
		currentUser = data['current_user'] 
		targetUser = currentUser
		
		# Get HTML code
		iconHtmlCode = get_icon_code(eventCode)
		currentUserLink = create_user_link(currentUser)
		
		# Determine proper message and add html code sets
		secondPersonPresent = "%s <span>Congrats! Your Flowgrams have reached %s views!</span>" % (iconHtmlCode,flowgramViewsCount) 
		thirdPersonPast = "%s <span>Wow! %s's Flowgrams have reached %s views.</span>" % (iconHtmlCode,currentUserLink,flowgramViewsCount) 
		secondPersonPast = "" # no case for this msg type
		
		# save event obj to UserHistory
		UserHistory.objects.create(currentUser=currentUser,targetUser=targetUser,eventCode=eventCode,flowgramId=flowgramIdStr,thirdPersonPast=thirdPersonPast,secondPersonPast=secondPersonPast,secondPersonPresent=secondPersonPresent)
	except Exception:
		log.debug("Attempted to create BADGE_FGVIEWS UserHistory event FAILED")# log error		


def store_fgmade_event(data):
    """
    Stores Flowgram Made event in UserHistory
    """
    eventCode = data['eventCode']
    flowgramIdStr = data['fg_id']
    fgAction = data['active']
    fg = Flowgram.objects.get(pk=flowgramIdStr) 
    
    if fgAction == "make_active":
        flowgramTitle = fg.title
        currentUser = fg.owner # in this case, current user is the flowgram owner 
        targetUser = fg.owner # there is no target user in this case, populating with current_user as placeholder
            
        # Get HTML code
        iconHtmlCode = get_icon_code(eventCode)
        currentUserLink = create_user_link(currentUser)
        flowgramLink = create_fg_details_link(flowgramIdStr, flowgramTitle) # Get fg html link
        
        # Determine proper message and add html code sets
        secondPersonPresent = "%s <span>Congrats! Your Flowgram named %s was made public.</span>" % (iconHtmlCode,flowgramLink) 
        thirdPersonPast = "%s <span>%s's Flowgram named %s was made public.</span>" % (iconHtmlCode,currentUserLink,flowgramLink) 
        secondPersonPast = "" # no case for this msg type
        historyItem, created = UserHistory.objects.get_or_create(flowgramId=flowgramIdStr, eventCode=eventCode, defaults={'currentUser':currentUser,'targetUser':targetUser,'thirdPersonPast':thirdPersonPast,'secondPersonPast':secondPersonPast,'secondPersonPresent':secondPersonPresent})       
        if not created:
            historyItem.eventActive = True
            historyItem.save()              
    else: # assumes 'make_inactive' 
        try:
            historyItem = UserHistory.objects.get(flowgramId=flowgramIdStr, eventCode=eventCode)        
            # make inactive / else do nothing, no worries 
            historyItem.eventActive = False
            historyItem.save()  
        except UserHistory.DoesNotExist:
            return


	
def store_invitation_event(data):
	"""INACTIVE"""
	
def store_message_event(data):
	"""INACTIVE"""
		
def store_kudos_event(data):
	"""INACTIVE"""

def create_fg_link(fg_id, fg_title):
	"""
	Returns a full html link to flowgram
	"""
	fg_link = "<a href=\"%sp/%s\">%s</a>" % (localsettings.my_URL_BASE, fg_id, fg_title)
	return fg_link

def create_fg_details_link(fg_id, fg_title):
	"""
	Returns a full html link to flowgram
	"""
	fg_link = "<a href=\"%sfg/%s\">%s</a>" % (localsettings.my_URL_BASE, fg_id, fg_title)
	return fg_link

def create_user_link(incoming_user):
	"""
	Returns a full html link to incoming_user
	"""
	user_link = "<a href=\"%s%s\">%s</a>" % (localsettings.my_URL_BASE, incoming_user, incoming_user)
	return user_link

def get_icon_code(code):
	"""
	Return full icon html img code associated with EventType 'code', if fail, returns default icon 
	"""
	try:
		eventType = EventType.objects.get(eventCode__exact=code) 
		iconPath = "<img src=\"%s%s\" />" % (localsettings.my_URL_BASE, eventType.icon_path)
		return iconPath
	except:
		iconPath = "<img src=\"%smedia/images/hearts/small_heart_red.png\" />" % localsettings.my_URL_BASE # default icon
		return iconPath

def get_all_subs():
	try:
		all_subs = Subscription.objects.all()
		subscriptions = []
		for sub in all_subs:
			subscriptions.append({'user':sub.user, 'subscriber':sub.subscriber, 'date':sub.date_subscribed})
		return subscriptions
	except Exception:
		raise


def get_user_subscriptions(user):
	try:
		user_subscriptions = Subscription.objects.filter(subscriber=user)
		subscriptions = []
		for sub in user_subscriptions:
			subscriptions.append({'user':sub.user,'subscriber':sub.subscriber,'date':sub.date_subscribed})
		return subscriptions
	except Exception:
		raise


def get_user_subscribers(user):
	try:
		user_subscribers = Subscription.objects.filter(user=user)
		subscribers = []
		for sub in user_subscribers:
			subscribers.append({'user':sub.user,'subscriber':sub.subscriber,'date':sub.date_subscribed})
		return subscribers
	except Exception:
		raise


