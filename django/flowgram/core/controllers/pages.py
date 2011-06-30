# TODO(westphal): Rename fix.
# TODO(westphal): Move controller contents into controllers submodules.
from flowgram.core import controller, fix, helpers, log, models

def add_page(user, url, html, title):
    # Modifying the HTML to add a base tag, etc.
    (html, url) = fix.process_page(html, url)
    
    # Creating and saving the page.
    page = models.Page.objects.create(title=title, source_url=url)
    html = helpers.cache_css_files(page, html)

    (flowgram, is_new) = controller.get_working_flowgram(user)
    if is_new:
        log.action('Created new working Flowgram with ID %s as a result of calling get_working_flowgram in add_page.' % \
                       flowgram.id)
    page = controller.create_page_to_flowgram(flowgram, page, html)
        
    # Removing the user's 'just_published' attribute.
    profile = user.get_profile()
    profile.just_published = False
    profile.save()

    return (flowgram, page)
