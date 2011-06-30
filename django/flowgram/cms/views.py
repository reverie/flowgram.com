from flowgram.core.helpers import req_render_to_response
from flowgram.cms.models import CmsPage

def show_cms_page(request, id):
    page = CmsPage.objects.get(id=id)
    return req_render_to_response(request, 'base/cms_base.html', {
        'page': page,
    })
