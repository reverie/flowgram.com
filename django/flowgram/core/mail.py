import re

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.template import loader, Context
from django.contrib.auth.decorators import login_required
from flowgram.queueprocessors.sendemailrequestprocessor import add_to_mail_queue

from flowgram.core.helpers import go_back
from flowgram.core.helpers import add_good_message, add_bad_message, go_back
from flowgram.core.models import Flowgram
from flowgram.localsettings import my_URL_BASE as URL_BASE 
from flowgram.localsettings import FEATURE
from flowgram.core import log

DEFAULT_SENDER = "Flowgram.com"
FEEDBACK_RECIPIENT = "feedback@flowgram.com"

def email_user(recipient, subject, text, sender=DEFAULT_SENDER):
    """Emails a user. If you call email_user, it is your responsibility to try/except"""
    if isinstance(sender, User):
        sender = "\"%s @ Flowgram\" <%s>" % (sender.username, sender.email)
    log.debug("send_mail from email_user to %s" % sender)
    add_to_mail_queue(sender, recipient.email, subject, text)
    
def password_reset_hash(user, day=None):
    """Generates the password reset hash for a user and a given day."""
    import md5
    from datetime import date
    from flowgram.localsettings import SECRET_KEY
    if day == None:
        day = date.today()
    key = (user.username + SECRET_KEY + str(day))
    hash = md5.md5(key).hexdigest()
    return hash
    
def validate_password_reset_hash(u, key):
    """Validates a user's password reset hash by checking if it was created within the last 2 days."""
    key_valid = False
    from datetime import date, timedelta
    yesterday = date.today() - timedelta(1)
    if key == password_reset_hash(u):
        key_valid = True
    if key == password_reset_hash(u, yesterday):
        key_valid = True
    return key_valid
        
def reset_password(u):
    """Generates and sends a password-reset email for the user."""
    #Calculate secret URL:
    hash = password_reset_hash(u)
    url = URL_BASE + ("newpassword/?user=%s&key=%s" % (u.username, hash))

    #render and send the email:
    subject = "Your Flowgram.com account"
    t = loader.get_template('emails/reset_password.txt')
    c = Context({
        'recipient': u,
        'url': url,
    })
    text = t.render(c)
    try:
        email_user(u, subject, text)
    except:
        log.trace()
        return False
    return True

def randname(length=8):
    import string
    import random
    import datetime
    random.seed(datetime.datetime.now())
    d = [random.choice(string.letters) for x in range(length)]
    return "".join(d)
    
def toolbar_share(request, w, recipients, message, from_name = '', from_email = '', cc_self = 'false', subject = '', template = 'share'):
    from flowgram.core.models import ShareLink
    if request.user.is_anonymous():
        sender = None
        senderName = from_name
        if senderName == '':
            senderName = 'Someone'
        senderEmail = from_email
    else:
        sender = request.user
        senderName = sender.username
        senderEmail = sender.email

    # Filters email addresses when they're given like "Some Name" <email@address.com>
    emailPattern = re.compile('(?:"[^"]*"\s+)?<([^>]+)>')
    recipients = emailPattern.sub(r'\1', recipients)

    # Adding sender email to recipients list if cc self is enabled.
    if cc_self == 'true' and senderEmail != '':
        recipients += ',' + senderEmail

    successes = []
    failures = []
    for recipient in recipients.split(','):
        recipient = recipient.strip()
        name = randname()
        
        #create ShareLink object
        sl = ShareLink.objects.create(name=name, flowgram=w, sender=sender, recipient=recipient)
        
        #send ascii user email
        if(subject == ''):
            subject = "%s (shared Flowgram from %s)" % (w.title, senderName)
            
        t = loader.get_template("emails/%s.txt" % template)
        h = loader.get_template("emails/%s.html" % template)
        
        if template == "talking_email":
            thumbs_list = w.page_set.all()[1:4]
        else:
            thumbs_list = w.page_set.all()[:3]
            
        
        c = Context({
            #'recipient': recipient,
            'sender': sender,
            'url': sl.url(),
            'message': message,
            'w': w,
            'owner': w.owner,
            'title': w.title,
            'from_name': from_name,
            'senderName': senderName,
            'thumbs_list': thumbs_list,
            'thumbs_list_length': len(thumbs_list)
        })
        text = t.render(c)
        html = h.render(c)
        
        # increment share_email counter
        w.share_emails += 1
        w.save()
        
        try:
            add_to_mail_queue(senderEmail, recipient, subject, text, html, 'text/html')
        except:
            failures.append(recipient)
        else:
            successes.append(recipient)
    return (successes, failures)


from django.template import Context
from django.template.loader import get_template
from flowgram.core.models import Regcode
def send_invitations(user, invitees, personal_message=""):
    sender_email = user.email
    subject = "%s has invited you try Flowgram.com" % sender_email
    t = get_template('emails/invite.txt')
    use_regcode = FEATURE['use_regcode']
    successes = []
    failures = []
    for email in invitees:
        r = Regcode.objects.create(sender=user)
        c = Context({
            'user' : user,
            'regcode': r.code,
            'use_regcode': use_regcode,
            'to': email,
            'URL_BASE' : URL_BASE,
            'personal_message' : personal_message
            })
        body = t.render(c)
        try:
            log.debug("send_mail from send_invitations to " + email)
            add_to_mail_queue(sender_email, email, subject, body)
            successes.append(email)
        except:
            failures.append(email)
    return successes, failures
            
def announce_flag(request, flowgram):
    flagger = request.user.username or request.META['REMOTE_ADDR']
    subect = "%s FLAGGED by %s" % (flowgram.title, flagger)
    sender = DEFAULT_SENDER
    text = "See the flagged flowgram at %s" % flowgram.url()
    recipients = ['watchdog@flowgram.com']
    try:
        log.debug("send_mail from announce_flag to " + 'watchdog@flowgram.com')
        for recipient in recipients:
            add_to_mail_queue(sender, recipient, subject, text)
    except:
        log.error("Failure in announce_flag:")
        log.trace()

def announce_new_flowgram(flowgram):
    creator = flowgram.owner
    url = flowgram.full_url()
    log.debug("announce_new_flowgram")    
    for profile in creator.subscribers.all():
        subject = "%s (Flowgram.com)" % (flowgram)
        text = "%s's latest Flowgram was published to the web at %s." % (creator, url)
        try:
            email_user(profile.user, subject, text)
        except:
            log.error("announce_feed_message failed to email user " + profile.username)
    if creator.get_profile().subscribed_to_self:
        subject = "\"%s\" -- your latest Flowgram has been posted!" % (flowgram.title)
        text = "Your latest Flowgram, %s, was published to the web at %s." %(flowgram.title, url)
        try:
            email_user(creator, subject, text)
        except:
            log.error("announce_feed_message failed to email user " + profile.username)
            
def announce_new_comment(comment):
    flowgram = comment.flowgram
    url = flowgram.full_url()
    subscribers = []#list(flowgram.subscribers.all())
    p = flowgram.owner.get_profile()
    if p.subscribed_to_own_fgs:
        subscribers.append(p)
    
    # new code in this block -- chris
    # for profile in subscribers:
    #         if profile == comment.owner:
    #             continue
    #         subject = "%s has a new comment (Flowgram.com)" % (flowgram)
    #         text = "The user \"%s\" added a comment to %s. Check it out at %s" % (comment.owner, flowgram.title, url)
    #         try:
    #             if profile == flowgram.owner and profile.user.get_profile().subscribed_to_own_fgs == True:
    #                 email_user(profile.user, subject, text)
    #             elif profile.user.get_profile().subscribe_fg_on_comment == True:
    #                 email_user(profile.user, subject, text)
    #         except:
    #             log.error("announce_new_comment failed to email user " + profile.user.username)
    
    # original code in this block -- chris        
    # for profile in subscribers:
    #         if profile == comment.owner:
    #             continue
    #         subject = "%s has a new comment (Flowgram.com)" % (flowgram)
    #         text = "The user \"%s\" added a comment to %s. Check it out at %s" % (comment.owner, flowgram.title, url)
    #         try:
    #             email_user(profile.user, subject, text)
    #         except:
    #             log.error("announce_new_comment failed to email user " + profile.user.username)        
    
    # this is sending an email to everyone who comments on any flowgram, but there is currently no opt-out which is highly irritating.  for now i am setting it to only email the flowgram owner, below is the fix -- chris 07/07/08
    # david has turned off flowgram_subscriptions in models.py because it was breaking the admin view.  However, this will now break any of the above code.  we will need to find another way to send emails to users who comment on Flowgrams they do not own. -- chris 07/08/08
    subject = "%s has a new comment (Flowgram.com)" % (flowgram)
    text = "The user \"%s\" added a comment to %s. Check it out at %s" % (comment.owner, flowgram.title, url)
    try:
        email_user(flowgram.owner, subject, text)
    except:
        log.error("announce_new_comment failed to email user " + flowgram.owner.username)

def announce_feedback(feedback):
    sender = DEFAULT_SENDER
    recipients = [FEEDBACK_RECIPIENT]
    subject = ""
    text = "URL: %s\nEmail: %s\nSystem info:\n%s\nComments: %s\n" % (feedback.url, feedback.email, feedback.sys_info, feedback.comments)
    try:
        log.debug("send_mail from announce_feedback to " + FEEDBACK_RECIPIENT)
        for recipient in recipients:
            add_to_mail_queue(sender, recipient, subject, text)
    except:
        log.error("Failure in announce_feedback:")
        log.trace()

def welcome_user(user):
    subject = "Welcome to Flowgram.com!"
    t = loader.get_template('emails/welcome_user.txt')
    c = Context({
        'recipient' : user,
        'homepage_url' : URL_BASE,
        'make_url': URL_BASE + 'create/',
        'browse_url': URL_BASE + 'browse/featured/',
        'profile_url': URL_BASE + str(user),
    })
    text = t.render(c)
    try:
        email_user(user, subject, text)
    except:
        log.error("welcome_user failed to email user " + user.username)
        
def toolbar_done(flowgram, creater):
    subject = "A link to your Flowgram \"" + flowgram.title + "\""
    embed_code_array = ['<object width="400" height="300"><param name="movie" value="',
                URL_BASE, 
                'widget/flexwidget.swf?id=',
                str(flowgram.id),
                '&hasLinks=',
                'false',
                '"><param name="flashVars" value="id=',
                str(flowgram.id),
                '"><param name="allowScriptAccess" value="always"><param name="allowNetworking" value="all"><embed src="',
                URL_BASE, 
                'widget/flexwidget.swf?id=',
                str(flowgram.id),
                '&hasLinks=',
                'false',
                '" width="400" height="300" FlashVars="id=',
                str(flowgram.id),
                '" allowScriptAccess="always" allowNetworking="all"></embed></object>']
    
    embed_code = "".join(embed_code_array)
    t = loader.get_template('emails/toolbar_done.html')
    c = Context({
        'recipient': creater.username,
        'flowgram_url': URL_BASE + 'p/' + str(flowgram.id),
        'embed_code': embed_code,
        'edit_link': URL_BASE + 'fg/' + str(flowgram.id),
        'contact_us': URL_BASE + 'about_us/contact_us/',
    })
    html = t.render(c)
    try:
        email_user_html(creater, subject, html, 'notreply@flowgram.com')
    except:
        log.error("toobar_done failed to email creater " + creater.username)

def email_user_html(recipient, subject, html, sender=DEFAULT_SENDER):
    """Emails a user. If you call email_user, it is your responsibility to try/except"""
    if isinstance(sender, User):
        sender = "\"%s @ Flowgram\" <%s>" % (sender.username, sender.email)
    log.debug("send_mail from email_user to %s" % sender)
    add_to_mail_queue(sender, recipient.email, subject, '', html, 'text/html')