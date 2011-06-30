from django import template
from django.template import Variable
from flowgram.core.models import Favorite
from flowgram.core import log

register = template.Library()

class RatingNode(template.Node):
    def __init__(self, flowgram, user, editable):
        self.flowgram = Variable(flowgram)
        self.user = Variable(user)
        self.editable = editable
    def render(self, context):
        flowgram = self.flowgram.resolve(context)
        user = self.user.resolve(context)
        fgid = flowgram.id
        rating = flowgram.get_rating()
        user_rating = flowgram.get_users_rating(user) if user.is_authenticated() else -1
        js_editable = 'true' if (user.is_authenticated() and self.editable) else 'false'
        return "new StarRating('%s', %d, %d, %s).render($$('div.fg_rating-%s')[0]);" % \
               (fgid, rating, user_rating, js_editable, fgid)

def do_rating(parser, token):
    """The star-rating tag takes three arguments: the flowgram, the viewing user, and a boolean
    literal indicating whether the rating is editable from this view or not.
    """
    try:
        tag_name, flowgram, user, editable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
    if editable == 'True':
        editable = True
    elif editable == 'False':
        editable = False
    else:
        editable = editable.resolve(context)
        if editable != True and editable != False:
            raise template.TemplateSyntaxError, "%r third argument must evaluate to True or False" % token.contents.split()[0]
    return RatingNode(flowgram, user, editable)

register.tag('star-rating', do_rating)

class HeartNode(template.Node):
    def __init__(self, flowgram, user, editable):
        self.flowgram = Variable(flowgram)
        self.user = Variable(user)
        self.editable = editable            
            
    def render(self, context):
        flowgram = self.flowgram.resolve(context)
        user = self.user.resolve(context)
        isFavorite = 'false'
        try:
            if user.is_authenticated():
                Favorite.objects.get(owner=user, flowgram=flowgram)
                isFavorite = 'true'
        except Favorite.DoesNotExist:
            pass

        fgid = flowgram.id
        js_editable = 'true' if (user.is_authenticated() and self.editable) else 'false'
        return "new HeartRating('%s', %s, %s).render($$('div.fg_heart-%s')[0]);" % \
               (fgid, isFavorite, js_editable, fgid)
               
def heart_node_wrapper(parser, token):
    """The star-rating tag takes three arguments: the flowgram, the viewing user, and a boolean
    literal indicating whether the rating is editable from this view or not.
    """
    try:
        tag_name, flowgram, user, editable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
    if editable == 'True':
        editable = True
    elif editable == 'False':
        editable = False
    else:
        editable = editable.resolve(context)
        if editable != True and editable != False:
            raise template.TemplateSyntaxError, "%r third argument must evaluate to True or False" % token.contents.split()[0]
    return HeartNode(flowgram, user, editable)

register.tag('favorite-heart', heart_node_wrapper)

WIDGET_VERSION = "9.0.28"

class WidgetNode(template.Node):
    def __init__(self, flowgram, width, height, mode, linkurl, additional_params=None):
        self.flowgram = Variable(flowgram)
        self.width = width
        self.height = height
        self.mode = mode
        self.linkurl = linkurl
        self.additional_params = additional_params
        log.debug("Initializing WidgetNode with linkurl=%s" % self.linkurl)
    def render(self, context):
        flowgram = self.flowgram.resolve(context)
        fgid = flowgram.id
        thislink = self.linkurl
        if thislink == '/create/':
            thislink += '?homeWidgetID=%s' % fgid
            log.debug("WidgetNode appending homeWidgetID arg -- now %s" % (self.linkurl))
        else:
            log.debug("WidgetNode not appending homeWidgetID arg -- linkurl=%s" % self.linkurl)

        if self.additional_params:
            additional_params = ',' + ','.join(['%s: "%s"' % (key, self.additional_params[key]) \
                                                    for key in self.additional_params.keys()])
        else:
            additional_params = ''

        return 'swfobject.embedSWF("/widget/flexwidget.swf", \
               "alt_%s", "%d", "%d", "%s", "/flex/playerProductInstall.swf", \
               {fgid: "%s", linkurl: "%s"%s}, \
               {wmode: "%s", allowScriptAccess: "always"}, \
               {id: "fwidget_%s"});' % \
               (fgid, self.width, self.height, WIDGET_VERSION, fgid, thislink, additional_params, self.mode, fgid)

def do_widget(parser, token):
    try:
        params = token.split_contents()
        tag_name=params[0]
        flowgram=params[1]
        width=params[2]
        height=params[3]
        mode=params[4]
        linkurl=params[5]
        params = params[6:]
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires five arguments" % token.contents.split()[0]
    if not (mode[0] == mode[-1] and mode[0] in ('"', "'")): # doesn't handle case where len=1
        raise template.TemplateSyntaxError, "%r tag's mode argument should be in quotes" % tag_name
    mode = mode[1:-1]
    if not (linkurl[0] == linkurl[-1] and linkurl[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's linkurl argument should be in quotes" % tag_name
    linkurl = linkurl[1:-1]
    try:
        width = int(width)
        height = int(height)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag's width and height arguments should be integers" % tag_name
    
    additional_params = {}
    for param in params:
        additional_params[param] = 'true'
    
    return WidgetNode(flowgram, width, height, mode, linkurl, additional_params)

register.tag('widget', do_widget)

from flowgram.core import captcha
def recaptcha(parser, token):
    public_key = '6LdEdwIAAAAAANWt9aHMHAtCvd9wL--xrx_LKc6z';
    return captcha.displayhtml(public_key)

register.tag('captcha', recaptcha)