from datetime import datetime

from flowgram.core.securerandom import secure_random_id

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils.html import escape

from flowgram import urlbuilder, localsettings
from flowgram.core import log, avatar, s3
from flowgram.core.abstract_models import ModelWithCaching, ModelWithRandomID
from flowgram.core.helpers import stackTrace

from decimal import Decimal

ANONYMOUS_USERNAME = 'AnonymousUser'
ANONYMOUS_USER_OBJECT = User.objects.get_or_create(username=ANONYMOUS_USERNAME)[0]

GENDER_CHOICES = [('', ''),('M', 'Male'), ('F', 'Female')] 

FREQ_CHOICES = [('D', 'Daily'),('I', 'Instantly'), ('W', 'Weekly')] 

RENDERED_NEWS_FEED_CACHE_TYPE_CHOICES = [('E', 'Email'), ('R', 'Rss'), ('S', 'Short, Site'), ('L', 'Long, Site')]

NEWS_FEED_VOICE_CHOICES = [('U', 'Second Person, Present Tense'),
                           ('3', 'Third Person, Past Tense'),
                           ('P', 'Second Person, Past Tense')]
                           
PRESS_CATEGORY = [('F', 'Featured Articles'),('M', 'More Press'),('R', 'FG Press Release')] 

SERVICES_CHOICES = [('add_page_request', 'add page request'),
                    ('get_css_request', 'get css request'),
                    ('ppt_import_request', 'ppt import request'),
                    ('send_email_request', 'send email request'),
                    ('import_media_request', 'import media request')
                    ]

#class Group(ModelWithRandomID):
    #owner = models.ForeignKey(User)
    #name = models.CharField(max_length=255)

class UserProfile(ModelWithCaching, ModelWithRandomID):
    user = models.ForeignKey(User, unique=True) #Unfortunately we can't use a OneToOne b/c of detecting new in save() (id fixed early)
    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES)
    birthdate = models.DateField(blank=True, null=True)
    homepage = models.URLField(blank=True, max_length=2048, verify_exists=False)
    avatar = models.CharField(max_length=100, blank=True)
    avatar_filetype = models.CharField(max_length=4, blank=True)
    avatar_builtin = models.BooleanField(default=True)
    tutorial_state = models.IntegerField(default=0)
    description = models.TextField(blank=True, max_length=4096)
    newsletter_optin = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    notification_freq = models.CharField(max_length=1, blank=True, choices=FREQ_CHOICES)
    notify_by_email = models.BooleanField(default=True)
    has_public_news_feed = models.BooleanField(default=True)
    last_total_fg_badge_given = models.PositiveIntegerField(default=0)
    rss_key = models.CharField(max_length=settings.ID_FIELD_LENGTH)

    # Not currently used:
    #email_verified = models.BooleanField(default=False)
    
    # Flowgram that pages will be added to by default:
    working_flowgram_id = models.CharField(max_length=settings.ID_FIELD_LENGTH, blank=True)

    # True right after the user publishes a flowgram, so that the next add can go to a new flowgram
    just_published = models.BooleanField(default=False) 
    
    # Temporary for Beta
    invitations = models.IntegerField(default=10)
    
    # Newsfeed subscriptions
    #user_subscriptions = models.ManyToManyField(User, related_name='subscribers', blank=True)
    #flowgram_subscriptions = models.ManyToManyField('Flowgram', related_name='subscribers', blank=True)

    # # # Feed Related Settings # # # # # # # # #
    subscribe_fg_on_comment = models.BooleanField(default=False)
    subscribed_to_own_fgs   = models.BooleanField(default=True)
    subscribed_to_self      = models.BooleanField(default=True)
    get_news_via_email      = models.BooleanField(default=True)
    
    #groups = models.ManyToManyField(Group, related_name='users', blank=True)

    def url(self):
        return "/" + self.user.username
    def absolute_url(self):
        return localsettings.my_URL_BASE + self.user.username
    def link(self):
        return "<a href=\"%s\">%s</a>" % (self.url(), self.user)
    def __unicode__(self):
        return "UserProfile of %s" % self.user
    def avatar_200(self):
        return avatar.get_url(self, 200)
    def avatar_100(self):
        return avatar.get_url(self, 100)
    def avatar_32(self):
        return avatar.get_url(self, 32)
    def avatar_25(self):
        return avatar.get_url(self, 25)
    def delete(self):
        log.critical("UserProfile %s deletion blocked" % self.id)
        raise Exception
    def get_inviter(self):
        try:
            regcode_object = Regcode.objects.get(user = self.user)
        except Regcode.DoesNotExist:
            return ''    
        inviter = regcode_object.sender
        return inviter
    class Admin:
        list_display = ('user', 'gender', 'birthdate', 'homepage')
        search_fields = ['user']
        ordering = ['user']

    def save(self, **kwargs):
        from flowgram.core.mail import welcome_user
        
        new = not self.id
        if not self.rss_key:
            self.rss_key = secure_random_id(settings.ID_ACTUAL_LENGTH)
        super(UserProfile, self).save(**kwargs)
        #ReIndexGather.objects.save_re_index(3, 0, self.id)
        if new:
            welcome_user(self.user)


class PublishedFlowgramManager(models.Manager):
    def get_query_set(self):
        return super(PublishedFlowgramManager, self) \
            .get_query_set().filter(tutorial=False, public=True)

class Favorite(ModelWithRandomID):
    owner = models.ForeignKey(User)
    flowgram = models.ForeignKey('Flowgram', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Flowgram(ModelWithCaching, ModelWithRandomID):
    # Fields
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1024, blank=True)
    views = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=settings.DEFAULT_DURATION, null=True, blank=True) #never set
    public = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    tutorial = models.BooleanField(default=False)
    display_in_newest = models.BooleanField(default=True)
    sent_owner_done_email = models.BooleanField(default=False)
    background_audio = models.ForeignKey('Audio', null=True)
    background_audio_loop = models.BooleanField(default=True)
    background_audio_volume = models.PositiveIntegerField(default=50)
    widget_views = models.PositiveIntegerField(default=0)
    share_emails = models.PositiveIntegerField(default=0)

    # Denormalization fields
    num_ratings = models.IntegerField(default=0)
    total_rating = models.IntegerField(default=0)
    avg_rating = models.FloatField(default=0)
    num_comments = models.IntegerField(default=0)

    #groups = models.ManyToManyField(Group, related_name='flowgrams', blank=True)

    # Managers
    from_published = PublishedFlowgramManager()    
    
    # Metadata
    class Admin:
        list_display = ('owner', 'title', 'views', 'created_at')
        search_fields = ['owner__username', 'title']
        date_hierarchy = 'created_at'
    class Meta:
        ordering = ['-published_at', '-created_at']
    
    # Methods
    def __unicode__(self):
        return self.title
    def url(self):
        return "/fg/%s/" % self.id
    def full_url(self):
        return localsettings.my_URL_BASE[:-1]+self.url()
    def link(self):
        return "<a href=\"%s\">%s</a>" % (self.url(), self)
    def date_for_display(self):
        return self.modified_at
    def play_url(self, hash=None):
        if hash:
            # Use this URL if reloading between Flowgrams.
            return localsettings.my_URL_BASE + '/p/%s/%s/' % (self.id, hash)
            # Use this URL if using hashnav.
            #return localsettings.my_URL_BASE+("f/p.html#%s,%s" % (self.id, hash.replace('-', '=').replace('__', ',')))
        else:
            # Use this URL if reloading between Flowgrams.
            return localsettings.my_URL_BASE + '/p/%s/' % self.id
            # Use this URL if using hashnav.
            #return localsettings.my_URL_BASE+("f/p.html#%s" % (self.id))
    def record_url(self):
        url = "%sr/%s" % (localsettings.my_URL_BASE, self.id)
        return url
    def flex_url(self):
        url = "%sp/%s" % (localsettings.my_URL_BASE, self.id)
        return url
    def edit_url(self):
        return "/p/%s/" % (self.id)
    def widget_code(self):
        widgetUrl = localsettings.my_URL_BASE + 'widget/flexwidget.swf'
        widgetCode = '<object type="application/x-shockwave-flash" data="%s" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab" width="400" height="342"><param name="movie" value="%s" /><param name="flashVars" value="id=%s&hasLinks=true" /><param name="allowScriptAccess" value="always" /><param name="allowNetworking" value="all" /><param name="pluginurl" value="http://www.adobe.com/go/getflashplayer" /></object>' % (widgetUrl, widgetUrl, self.id)
        return widgetCode
    def tags(self):
        return self.tag_set.order_by('name')
    def thumb_url(self):
        pages = Page.objects.filter(flowgram=self).order_by('position')
        if len(pages) > 0:
            return pages[0].thumb_url()
        else:
            return None
    def get_rating(self):
        """Returns the average rating, divided by 2, to make it on a 5 point
        scale instead of a 10 point scale."""
        if self.num_ratings == 0:
            return 0
        else:
            return self.avg_rating
        
    def get_users_rating(self, user):
        """Gets the specified user's rating for the flowgram."""
        if not user.is_authenticated():
            return -1
        rating = Rating.objects.filter(flowgram=self, user=user)
        if len(rating) > 0:
            return float(rating[0].value) / 2
        else:
            return -1
        
    def publish(self, public):
        if self.published:
            log.error("Tried publish already-published flowgram %s" % (self.id))
        self.published = True
        self.public = public
        if public:
            self.published_at = datetime.now()
        self.save()

    def directory(self):
        from flowgram.localsettings import my_WOWKASTDIR 
        return "%s%s/%s/" % (my_WOWKASTDIR, self.owner.id, self.id)
    
    def delete(self):
        log.debug("deleting flowgram %s with owner %s" % (self.id, self.owner.id))
        
        profiles = UserProfile.objects.filter(working_flowgram_id=self.id)
        
        for p in profiles:
            log.debug("clearing working_flowgram_id of user %s profile %s" % (p.user.id, p.id))
            
            p.working_flowgram_id = ""
            p.save()
        #ReIndexGather.objects.save_re_index(1, 1, self.id)
        super(Flowgram, self).delete()
        
    def is_anonymous(self):
        return self.owner == ANONYMOUS_USER_OBJECT
        
    def save(self, *args, **kwargs):
        self.description = self.description[:1024]
        super(Flowgram, self).save(*args, **kwargs)
        #ReIndexGather.objects.save_re_index(1, 0, self.id)
        
        
class Page(ModelWithCaching, ModelWithRandomID):
    bypass_cache = models.Manager()
    
    #TODO: switch to using a 'deleted' bool instead
    # 'flowgram' is null iff the page is deleted
    flowgram = models.ForeignKey(Flowgram, null=True) 
    # 'owner' is non-null iff a page is deleted (to know who can readd)
    owner = models.ForeignKey(User, null=True) 
    # Deleted pages are special. The *only* thing you can do with them is re-add them.

    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(max_length=1024, blank=True)
    source_url = models.URLField(max_length=2048)
    duration = models.PositiveIntegerField(default=settings.DEFAULT_DURATION, null=True, blank=True) #audio duration
    position = models.PositiveSmallIntegerField(default=9999)
    audio_path = models.CharField(max_length=128, blank=True)
    thumb_path = models.CharField(max_length=128, blank=True)
    thumb_dir = models.CharField(max_length=128, blank=True)
    transition_type = models.PositiveIntegerField(default=0)
    fade_in = models.BooleanField(default=True)
    fade_out = models.BooleanField(default=True)
    is_custom = models.BooleanField(default=False)
    creation_source = models.CharField(max_length=128, blank=True)

    # TODO(andrew): write delHighlight so we can get rid of this:
    max_highlight_id_used = models.IntegerField(default=-1)

    def __unicode__(self):
        return ("%s (%s)" % (self.title, self.source_url))
    
    def thumb_url(self):
        return 'http://%s/%s_150_100.jpg' % \
                   (localsettings.S3_BUCKETS[localsettings.S3_BUCKET_THUMB], self.id)
        #return localsettings.my_URL_BASE+("api/getthumb/%s/" % (self.id))
    
    def get_type(self):
        lower_source_url = self.source_url.lower()
        
        type = 0
        if lower_source_url.endswith((".jpg", ".png", ".jpeg", ".bmp", ".gif", ".fimage")):
            type = 1
        
        return type
    
    def small_thumb_filename(self):
        return "%s_%d_%d.jpg" % (self.id, 150, 100)

    def get_loading_status(self):
        try:
            request = AddPageRequest.objects.get(page=self)
            return request.status_code
        except AddPageRequest.DoesNotExist:
            return StatusCode.DONE

    def save(self, *args, **kwargs):
        self.description = self.description[:1024]
        super(Page, self).save(*args, **kwargs)
        #ReIndexGather.objects.save_re_index(2, 0, self.id) 

    class Admin:
        list_display = ('flowgram', 'title', 'source_url')


class CustomPage(ModelWithCaching, ModelWithRandomID):
    page = models.ForeignKey(Page, null=True) 
    content = models.TextField(null=True)

    class Admin:
        list_display = ('page', 'content')
        

class UnboundPage(ModelWithRandomID):
    owner = models.ForeignKey(User, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return ("%s (%s)" % (self.title, self.source_url))
    class Admin:
        pass
        
class Comment(ModelWithCaching, ModelWithRandomID):
    owner = models.ForeignKey(User, null=True, blank=True)
    flowgram = models.ForeignKey(Flowgram)  
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=1024) 

    def __unicode__(self):
        return "%s comments on %s" % (self.owner_id, self.flowgram_id)
    class Admin:
        list_display = ('flowgram', 'owner', 'created_at')
    class Meta:
        ordering = ['created_at']

    def save(self):
        """Overrides the save method so that an ID can be manually generated."""
        new = not self.id

        super(Comment, self).save()

        if new: 
            # Increment flowgram comment count
            fg = self.flowgram
            fg.num_comments += 1
            fg.save(invalidate_cache=False)
            import mail
            mail.announce_new_comment(self)

class Tag(ModelWithCaching, ModelWithRandomID):
    name = models.CharField(max_length=64)
    flowgram = models.ForeignKey(Flowgram)
    adder = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s: %s" % (self.flowgram, self.name)
    class Admin:
        pass

class Regcode(models.Model):
    code = models.CharField(max_length=16, blank=True, unique=True)
    used = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, blank=True)
    sender = models.ForeignKey(User, null=True, blank=True, related_name="regcodes_sent")
    count = models.IntegerField(default = 1)
    
    def __unicode__(self):
        return self.code
    def save(self):
        new = (not self.id)
        if new and not self.code:
            import string, random
            code = list(string.uppercase)
            random.shuffle(code)
            self.code = ''.join(code[:7])
        super(Regcode, self).save()
    class Admin:
        list_display = ('code', 'used', 'user')

class Highlight(ModelWithCaching, ModelWithRandomID):
    name = models.IntegerField()
    page = models.ForeignKey(Page)
    time = models.IntegerField()
    class Admin:
        list_display = ('page', 'name', 'time')

class Audio(ModelWithCaching, ModelWithRandomID):
    page = models.ForeignKey(Page, null=True)
    time = models.IntegerField()
    duration = models.IntegerField()
    path = models.CharField(max_length=128, blank=True) 
    
    class Admin:
        pass

# TODO(westphal): Move avg rating calculations for flowgrams into rating save method.
class Rating(ModelWithRandomID):
    user = models.ForeignKey(User)
    flowgram = models.ForeignKey(Flowgram)
    value = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Admin:
        pass

class FlowgramPoll(models.Model):
    poll_short_name = models.CharField(max_length=30)
    poll_title = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    candidate_id_1 = models.CharField(max_length=255)
    candidate_id_2 = models.CharField(max_length=255)
    candidate_id_3 = models.CharField(max_length=255)
    votes_1 = models.IntegerField(default=0)
    votes_2 = models.IntegerField(default=0)
    votes_3 = models.IntegerField(default=0)
    poll_active = models.BooleanField(default=False)
    
    def total_votes(self):
        total_votes = self.votes_1 + self.votes_2 + self.votes_3
        return total_votes

    def percentage_1(self):
        if self.votes_1 == 0:
            return 0
        else:
            total_votes = self.votes_1 + self.votes_2 + self.votes_3
            percentage = Decimal(self.votes_1) / Decimal(total_votes) * 100
            TWOPLACES = Decimal(10)
            percentage = Decimal(percentage).quantize(TWOPLACES)
            return percentage
    
    def percentage_2(self):
        if self.votes_2 == 0:
            return 0
        else:
            total_votes = self.votes_1 + self.votes_2 + self.votes_3
            percentage = Decimal(self.votes_2) / Decimal(total_votes) * 100
            TWOPLACES = Decimal(10)
            percentage = Decimal(percentage).quantize(TWOPLACES)
            return percentage
    
    def percentage_3(self):
        if self.votes_3 == 0:
            return 0
        else:
            total_votes = self.votes_1 + self.votes_2 + self.votes_3
            percentage = Decimal(self.votes_3) / Decimal(total_votes) * 100
            TWOPLACES = Decimal(10)
            percentage = Decimal(percentage).quantize(TWOPLACES)
            return percentage

    def save(self):
        super(FlowgramPoll, self).save()

class FlowgramPress(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    link_date = models.DateField(blank=True, null=True)
    link_text = models.CharField(max_length=2048)
    link_url = models.URLField(blank=True, max_length=2048, verify_exists=False)
    lede_text = models.TextField(blank=True, max_length=4096)
    full_text = models.TextField(blank=True)
    press_category = models.CharField(max_length=1, blank=True, choices=PRESS_CATEGORY)

    def save(self):
        super(FlowgramPress, self).save()

class FlowgramRelated(models.Model):
    flowgram = models.ForeignKey(Flowgram)
    related = models.CharField(max_length=1023)
    timestamp = models.DateTimeField(auto_now_add=True)
    

class Enum(object): pass

# To add a featured area, add a row to "feat" with a short constant name, and a row to 
# FEATURED_AREAS below with the full name

# TODO(westphal): Rename this (at least capitalize it: Feat).
# TODO(westphal): This enum doesn't really make sense, why index from 0-9 manually (could just 
#                 directly index into an array).  What's the point of names like CATEGORY_BEST_1,
#                 when we could have an array?
feat = Enum()
feat.HOME = 0
feat.FEATURED_PAGE = 1
feat.CATEGORY_BEST_1 = 2
feat.CATEGORY_BEST_2 = 3
feat.CATEGORY_BEST_3 = 4
feat.CATEGORY_BEST_4 = 5
feat.CATEGORY_BEST_5 = 6
feat.CATEGORY_BEST_6 = 7
feat.CATEGORY_BEST_7 = 8
feat.CATEGORY_BEST_8 = 9

FEATURED_AREAS = (
    (feat.HOME, 'Home Page'), 
    (feat.FEATURED_PAGE, 'Featured Page'),
    (feat.CATEGORY_BEST_1, 'Best Instructional Flowgram'),
    (feat.CATEGORY_BEST_2, 'Best Blog Flowgram'),
    (feat.CATEGORY_BEST_3, 'Best Talking Slideshow'),
    (feat.CATEGORY_BEST_4, 'Best Web Roundup'),
    (feat.CATEGORY_BEST_5, 'Best Personal Message'),
    (feat.CATEGORY_BEST_6, 'Funniest Flowgram'),
    (feat.CATEGORY_BEST_7, 'Most Creative Use'),
    (feat.CATEGORY_BEST_8, 'Best Business Promotion')
)

FEATURED_CATEGORIES = [feat.CATEGORY_BEST_1,
                       feat.CATEGORY_BEST_2,
                       feat.CATEGORY_BEST_3,
                       feat.CATEGORY_BEST_4]

feat_fullname = dict(FEATURED_AREAS)

class Featured(models.Model):
    flowgram = models.ForeignKey(Flowgram)
    rank = models.FloatField()
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    area = models.IntegerField(choices=FEATURED_AREAS)

    class Admin:
        pass
    class Meta:
        ordering = ['rank']
        
class WhatsNew(models.Model):
    title = models.CharField(max_length=1024)
    # if the user input weight is 0, item will not show up
    weight = models.PositiveIntegerField(default = 1)
    embeddedHTML = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.title
    class Admin:
        list_display = ('title', 'weight', 'created_at')
        search_fields = ['title']
    class Meta:
        ordering = ['-weight']
        
class Tip(models.Model):
    title = models.CharField(max_length=1024)
    # if the user input weight is 0, item will not show up
    weight = models.PositiveIntegerField(default = 1)
    embeddedHTML = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.title
    class Admin:
        list_display = ('title', 'weight', 'created_at')
        search_fields = ['title']
    class Meta:
        ordering = ['-weight']

class Community_Content(models.Model):
    title = models.CharField(max_length=1024)
    # if the user input weight is 0, item will not show up
    weight = models.PositiveIntegerField(default = 1)
    embeddedHTML = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.title
    class Admin:
        list_display = ('title', 'weight', 'created_at')
        search_fields = ['title']
    class Meta:
        ordering = ['-weight']

class QuickLink(ModelWithCaching, ModelWithRandomID):
    name = models.CharField(max_length=64)
    url = models.CharField(max_length=255)

    class Admin:
        pass
    
    
##
# The StatusCode enum represents status codes that can be used for identifying the states of
# requests.
##
StatusCode = Enum()
StatusCode.UNPROCESSED = 0
StatusCode.PROCESSING = 1
StatusCode.DONE = 2
StatusCode.ERROR = 100

STATUS_CHOICES = [(StatusCode.UNPROCESSED, "Unprocessed"), 
                  (StatusCode.PROCESSING, "Processing"),
                  (StatusCode.DONE, "Done"),
                  (StatusCode.ERROR, "Error")]
                  
class QueuedJob(ModelWithRandomID):
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)
    status_code = models.IntegerField(default=StatusCode.UNPROCESSED, choices=STATUS_CHOICES)
    started_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    class Admin:
        pass
    class Meta:
        abstract = True

class ImportMediaRequest(QueuedJob):
    flowgram = models.ForeignKey(Flowgram, null=True)
    page = models.ForeignKey(Page, null=True)
    path = models.CharField(max_length=128)
    content_type = models.CharField(max_length=128)
    media_type = models.CharField(max_length=32)
    media_model_id = models.CharField(max_length=settings.ID_FIELD_LENGTH)

class AddPageRequest(QueuedJob):
    """ The AddPageRequest class represents a request to add a page by URL.
    The id field should be known by the client since a page ID isn't available
    until after the page is added to the Flowgram. The timestamp field is the
    time when the request was first made. The status_code field describes the
    state of processing. Valid status_codes for AddPageRequest are:
    UNPROCESSED, PROCESSING, DONE, and ERROR. UNPROCESSED and PROCESSING mean
    that no results are available but that there may be results in the future.
    PROCESSING also means that at least one attempt has started -- though it
    may not literally mean that processing is actually, currently taking
    place. ERROR means that enough errors have occurred and that no results
    will ever be produced (e.g. if max attempts is reached). The page field is
    the reference to the result created by successfully processing an add page
    request. """
    flowgram = models.ForeignKey(Flowgram)
    url = models.URLField(max_length=2048)
    page = models.ForeignKey(Page, null=True, blank=True)
    
TQ_TYPES = [(0, 'webpage'), (1, 'image')]
class ThumbQueue(QueuedJob):
    # TODO: change this to a QueuedJob
    page = models.ForeignKey(Page, unique=True)
    path = models.CharField(max_length=1024)
    type = models.IntegerField(default=0, choices=TQ_TYPES)

class GetCssRequest(QueuedJob):
    """ The GetCssRequest class represents a request to get a CSS file
    associated with a page. Before the CSS has been fetched one may use the
    url field to get the CSS file. After the CSS file has been fetched, the
    path field should contain valid data. In the case where the file could not
    be fetched (after retrying several times), one should continue to serve
    the HTML with the url field data. """
    page = models.ForeignKey(Page)
    url = models.URLField(max_length=2048)
    path = models.CharField(max_length=128, blank=True)

    def calculate_local_url(self):
        return "http://%s/css/%s/" % (localsettings.MASTER_DOMAIN_NAME, self.id)

    def calculate_path(self):
        return "%s%s.css" % (self.directory(), self.id)


class ExportToVideoRequest(QueuedJob):
    """ The ExportToVideoRequest class represents a request to encode a Flowgram. """
    flowgram = models.ForeignKey(Flowgram)
    use_highlight_popups = models.BooleanField(default=True)
    request_user = models.ForeignKey(User,null=True)
    request_email = models.CharField(max_length=128, blank=True)


class UploadToYouTubeRequest(QueuedJob):
    """ The UploadToYouTubeRequest class represents a request to upload an encoded Flowgram video to
        YouTube. """
    export_to_video_request = models.ForeignKey(ExportToVideoRequest)
    flowgram = models.ForeignKey(Flowgram)
    use_highlight_popups = models.BooleanField(default=True)
    token = models.CharField(max_length=255, blank=False)
    request_user = models.ForeignKey(User,null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1024, blank=True)
    keywords = models.TextField(max_length=1024, blank=True)
    category = models.CharField(max_length=128)
    private = models.BooleanField(default=False)


class SendEmailRequest(QueuedJob):
    fromAddress = models.CharField(max_length=128, blank=False)
    toAddress = models.CharField(max_length=128, blank=False)
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    altContent = models.TextField(blank=True)
    altContentType = models.CharField(max_length=64, blank=True)


class PptImportRequest(QueuedJob):
    flowgram = models.ForeignKey(Flowgram)
    filetype = models.CharField(max_length=64, blank=False)
    uploaded_to_s3 = models.BooleanField(default=False)
    
    def get_s3_key(self):
        return 'ppt/' + self.id + '.' + self.filetype

    def get_s3_url(self):
        return 'http://' + localsettings.S3_BUCKETS[localsettings.S3_BUCKET_UPLOAD] + '/' + self.get_s3_key()

    def save_ppt_to_s3(self, content):
        key = self.get_s3_key()
        s3.save_string_to_bucket(localsettings.S3_BUCKET_UPLOAD, key, content)
        self.uploaded_to_s3 = True
        self.save()

    def delete(self):
        # TODO: delete file from S3
        return super(PptImportRequest, self).delete()    

class EmailSubscriptionRequest(QueuedJob):
    should_subscribe = models.BooleanField()
    email_address =  models.CharField(max_length=100)

    def delete(self):
        return super(EmailSubscriptionRequest, self).delete()    

MEDIA_TYPES = [(0, "Image")]
MEDIA_TYPE_IMAGE = 0

class UploadedFile(ModelWithRandomID):
    #user = models.ForeignKey(User)
    #file = models.FileField(upload_to='user_files/', blank=True)
    #md5 = models.CharField(max_length=32)

    page = models.ForeignKey(Page)
    mimetype = models.CharField(max_length=200)    
    media_type = models.IntegerField(choices=MEDIA_TYPES)
    #original_filename = models.CharField(max_length=60)
    
    def get_absolute_url(self):
        if self.media_type == MEDIA_TYPE_IMAGE:
            return 'http://' + localsettings.S3_BUCKETS[localsettings.S3_BUCKET_UPLOAD] + '/' + self.id +'.fimage' #The .fimage extension is used to trigger the express thumbnail generator.     

    def set_file(self, content):
        if self.media_type == MEDIA_TYPE_IMAGE:
            s3.save_string_to_bucket(localsettings.S3_BUCKET_UPLOAD, self.id + '.fimage', content, content_type=self.mimetype)

    def delete(self):
        # TODO: delete file from S3
        return super(UploadedFile, self).delete()
    class Admin:
        pass


#ReIndexModelType = Enum()
#ReIndexModelType.FLOWGRAM = 1
#ReIndexModelType.PAGE = 2
#ReIndexModelType.USER = 3

#ReIndexActionType = Enum()
#ReIndexActionType.UPDATE = 0
#ReIndexActionType.DELETE = 1

#REINDEX_MODELTYPE = [(ReIndexModelType.FLOWGRAM, "Flowgram"), 
                  #(ReIndexModelType.PAGE, "Page"),
                  #(ReIndexModelType.USER, "Userprofile")]

#REINDEX_ACTIONTYPE = [(ReIndexActionType.UPDATE, "Update"), 
                      #(ReIndexActionType.DELETE, "Delete")]

#class ReIndexGatherManager(models.Manager):
    #def save_re_index(self, model_type, action_type, model_id):
        #now = datetime.now()
        #reindex = self.model(None, model_type, action_type, model_id, now)
        #reindex.save()
        #return reindex
        

#class ReIndexGather(models.Model):
    #reindex_model_type = models.IntegerField(choices=REINDEX_MODELTYPE)
    #reindex_action_type = models.IntegerField(choices=REINDEX_ACTIONTYPE)
    #id_from_external_source = models.CharField(max_length=255)
    #updated_time = models.DateTimeField()
    #objects = ReIndexGatherManager()

    
from flowgram.core.logging_models import *


    

# ============ NOTIFCATIONS & SUBSCRIPTIONS ==============
class RenderedNewsFeedCache(models.Model):
    user = models.ForeignKey(User)
    request_user = models.ForeignKey(User, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, blank=True, choices=RENDERED_NEWS_FEED_CACHE_TYPE_CHOICES)
    data = models.TextField(max_length=8192, blank=True)


class EmailDigestRecord(models.Model):
    user = models.ForeignKey(User, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class EventType(models.Model):
	eventCode = models.CharField(max_length=50, help_text="Code used across subscriptions/notifications, ex. 'FAVED'")
	icon_path = models.CharField(max_length=50, help_text="String used for Path/to/icon/for/event/type/")
	
	
	# META DATA
	class Meta:
		ordering = ['eventCode']
		verbose_name_plural = 'Event Types'
	
	class Admin:
		pass

	# METHODS
	def __unicode__(self):
		return self.eventCode

class UserHistory(models.Model):
	"""
	UserHistory Model
	"""	
	# FIELDS
	currentUser = models.ForeignKey(User)
	targetUser = models.ForeignKey(User)
	eventCode = models.CharField(max_length=128, blank=True)
	flowgramId = models.CharField(max_length=128, blank=True)
	thirdPersonPast = models.TextField(max_length=1024, blank=True)
	secondPersonPast = models.TextField(max_length=1024, blank=True)
	secondPersonPresent = models.TextField(max_length=1024, blank=True)	
	eventTime = models.DateTimeField(auto_now_add=True)
	eventActive = models.BooleanField(default=True)
		
	# METADATA
	class Meta:
		ordering = ['eventTime']
		verbose_name_plural = 'User History Entries'
	
	class Admin:
		pass
			
	# METHODS
	def __unicode__(self):
		return "%s Event for %s at %s" % (self.eventCode,self.currentUser,self.eventTime)


class Subscription(models.Model):
	"""
	Manages all subscription/unsubscription information from user to user. 
	"""
	# FIELDS
	user = models.ForeignKey(User) 
	subscriber = models.ForeignKey(User)
	date_subscribed = models.DateTimeField(auto_now_add=True)
	
	
	# META DATA
	class Meta:
		ordering = ['user']
		verbose_name_plural = 'User Subscriptions'	
	
	class Admin:
		pass

	# METHODS
	def __unicode__(self):
		return "%s is subscribed to %s" % (self.subscriber, self.user)


# === INACTIVE ===
class UserBroadcastFilter(models.Model):
	"""
	INACTIVE FOR V1
	Will Manage User preferences for each event type they want to broadcast. 
	True = Broadcast, False = Don't Send
	"""
	# FIELDS
	user = models.ForeignKey(User)
	eventType = models.ForeignKey('EventType')
	broadcastTo = models.BooleanField(default=True)

	# META DATA
	class Meta:
		ordering = ['user']
		verbose_name_plural = 'User Broadcast Filters'
	
	class Admin:
		pass

	# METHODS	
	def __unicode__(self):
		return "Broadcast Filter: %s %s = %s" % (self.user, self.eventType, self.broadcastTo)

	def _is_filtered(self, data):
		# V1: Always = True
		# V2: Check if eventType for user is t/f
		return True
		
	# PROPERTIES
	is_filtered = property(_is_filtered) 
	
# === INACTIVE ===
class UserListenerFilter(models.Model):
	"""	
	INACTIVE FOR V1
	Will Manage User preferences for each event type they want to listen for. 
	True = Listen, False = Ignore  
	"""
	# FIELDS
	user = models.ForeignKey(User)
	eventType = models.ForeignKey('EventType')
	listenFor = models.BooleanField(default=True)
	# META DATA
	class Meta:
		ordering = ['user']
		verbose_name_plural = 'User Listener Filters'
	class Admin:
		pass
	# METHODS
	def __unicode__(self):
		return "Listener Filter: %s %s = %s" % (self.user, self.eventType, self.listenFor)

	def _is_filtered(self, data):
		# V1: Always = True
		# V2: Check if eventType for user is t/f
		return True
		
	# PROPERTIES
	is_filtered = property(_is_filtered) 
    

class DashboardServiceRecord(models.Model):
    service_type = models.CharField(max_length=24, blank=True, choices=SERVICES_CHOICES)
    service_status = models.BooleanField(default=True)
    latest_checkedtime = models.DateTimeField(auto_now_add=True, blank=True)
    
    class Admin:
        pass
    