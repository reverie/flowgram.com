# TODO(westphal): Move this into importers.

import flickrapi
import gdata.photos.service
import gdata.media
from django.http import HttpResponseRedirect, HttpResponse, Http404
from flowgram import localsettings
from flowgram.core import controller, encode
from flowgram.core.models import Page
from flowgram.core.require import require
from flowgram.facebook import minifb
from flowgram.core.response import data_response
from picasaweb import gd_client

FACEBOOK_API_SECRET_MINIFB = minifb.FacebookSecret(localsettings.FACEBOOK_API_SECRET)
PER_PAGE_RESULT = 40

@require('GET', ['enc=json', 'service'])
def get_album_info(request, enc, service):
    if service == 'flickr':
        flickr_token = request.session.get('flickr_token', None)

        f = flickrapi.FlickrAPI(localsettings.FLICKR_API_KEY,
                                localsettings.FLICKR_API_SECRET,
                                token=flickr_token,
                                store_token=False)

        #photosets = f.photosets_getList().photosets[0].photoset
        photosets = f.photosets_getList().find('photosets').findall('photoset')   
        albums = []

        for photoset in photosets:
            albums.append({'id': photoset.attrib['id'], 'title': photoset.find('title').text})

        return data_response.create(enc, 'ok', albums)
    elif service == 'facebook':
        facebook_token = request.session.get('facebook_token', None)
    
        albums = minifb.call('facebook.photos.getAlbums',
                             localsettings.FACEBOOK_API_KEY,
                             FACEBOOK_API_SECRET_MINIFB,
                             session_key=facebook_token)

        output = []
        
        for album in albums:
            output.append({'id': str(album['aid']), 'title': album['name']})
        
        return data_response.create(enc, 'ok', output)
    elif service == 'picasaweb':
        gd_client.auth_token = request.session['picasaweb_token']   
        
        albums = gd_client.GetUserFeed()
        output = []

        for album in albums.entry:
            output.append({'id': album.id.text, 'title': album.title.text})
        
        return data_response.create(enc, 'ok', output)

    raise Http404


@require('GET', ['enc=json', 'service', 'album_id'])
def get_photos_for_album(request, enc, service, album_id):
    if service == 'flickr':
        flickr_token = request.session.get('flickr_token', None)

        f = flickrapi.FlickrAPI(localsettings.FLICKR_API_KEY,
                                localsettings.FLICKR_API_SECRET,
                                token=flickr_token,
                                store_token=False)
        
        #photos = f.photosets_getPhotos(photoset_id=album_id).photoset[0].photo
        photos = f.photosets_getPhotos(photoset_id=album_id).find('photoset').findall('photo')    
        output = []

        for photo in photos:
            #photo_id = photo['id']
            photo_id = photo.attrib['id']
            info = f.photos_getInfo(photo_id=photo_id)
            thumbnail_url = ''.join(['http://farm',
                                     photo.attrib['farm'],
                                     '.static.flickr.com/',
                                     photo.attrib['server'],
                                     '/',
                                     photo_id,
                                     '_',
                                     photo.attrib['secret'],
                                     '_t.jpg']);
            output.append({'id': photo_id,
                           'title': info.find('photo').find('title').text,
                           'thumbnail_url': thumbnail_url})

        return data_response.create(enc, 'ok', output)
    elif service == 'facebook':
        facebook_token = request.session.get('facebook_token', None)
    
        photos = minifb.call('facebook.photos.get',
                             localsettings.FACEBOOK_API_KEY,
                             FACEBOOK_API_SECRET_MINIFB,
                             session_key=facebook_token,
                             aid=album_id)

        output = []
        
        for photo in photos:
            output.append({'id': str(photo['pid']),
                           'title': photo['caption'],
                           'thumbnail_url': photo['src_small']})
        
        return data_response.create(enc, 'ok', output)
    elif service == 'picasaweb':
        gd_client.auth_token = request.session['picasaweb_token']
        album_id = album_id[album_id.index('albumid/')+8:]
        photos = gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' %('default', album_id))
        output = []
        for photo in photos.entry:
            output.append({'id': photo.gphoto_id.text,
                           'title': photo.title.text,
                           'thumbnail_url': photo.media.thumbnail[0].url
                           })
        return data_response.create(enc, 'ok', output)

    raise Http404

@require('GET', ['enc=json', 'service', 'query', 'page:int'])
def get_photos_for_search(request, enc, service, query, page):
    if service == 'flickr':
        flickr_token = request.session.get('flickr_token', None)
        
        f = flickrapi.FlickrAPI(localsettings.FLICKR_API_KEY,
                                localsettings.FLICKR_API_SECRET,
                                token=flickr_token,
                                store_token=False)
        
        photos = f.photos_search(text=query, per_page=PER_PAGE_RESULT, page=page).find('photos').findall('photo')
        
        output = []
        
        for photo in photos:
            photo_id = photo.attrib['id']
            info = f.photos_getInfo(photo_id=photo_id)
            thumbnail_url = ''.join(['http://farm',
                                     photo.attrib['farm'],
                                     '.static.flickr.com/',
                                     photo.attrib['server'],
                                     '/',
                                     photo_id,
                                     '_',
                                     photo.attrib['secret'],
                                     '_t.jpg']);
            output.append({'id': photo_id,
                           'title': info.find('photo').find('title').text,
                           'thumbnail_url': thumbnail_url})
        
        return data_response.create(enc, 'ok', output)
    elif service == 'picasaweb':
        gd_client.auth_token = request.session['picasaweb_token']
        query = query.replace(' ', '+')
        photos = gd_client.GetFeed('/data/feed/api/all?q=%s&max-results=%d&start-index=%d' %(query, PER_PAGE_RESULT, PER_PAGE_RESULT*(page-1)+1))
        
        output = []
        for photo in photos.entry:
            output.append({'id': photo.gphoto_id.text,
                           'title': photo.title.text,
                           'thumbnail_url': photo.media.thumbnail[0].url
                           })
        return data_response.create(enc, 'ok', output)
        
    raise Http404


@require('POST',
         ['enc=json', 'service', 'flowgram_id', 'album_id', 'photo_ids:csl'],
         ['edit_flowgram'])
def import_photos_with_ids_in_album(request, enc, service, flowgram, album_id, photo_ids):
    if service == 'flickr':
        flickr_token = request.session.get('flickr_token', None)

        f = flickrapi.FlickrAPI(localsettings.FLICKR_API_KEY,
                                localsettings.FLICKR_API_SECRET,
                                token=flickr_token,
                                store_token=False)

        photos = f.photosets_getPhotos(photoset_id=album_id).find('photoset').findall('photo')
    
        output = []

        for photo in photos:
            photo_id = photo.attrib['id']
            if photo_id in photo_ids:
                info = f.photos_getInfo(photo_id=photo_id)
                
                photo_url = ''.join(['http://farm',
                                     photo.attrib['farm'],
                                     '.static.flickr.com/',
                                     photo.attrib['server'],
                                     '/',
                                     photo_id,
                                     '_',
                                     photo.attrib['secret'],
                                     '.jpg']);
                
                title = info.find('photo').find('title').text
                
                html = '<html><head><title>%s</title>' \
                            '<style>@import url("/media/css/photo_importers.css");</style>' \
                        '</head><body><img src="%s" /></body></html>' % (title, photo_url)

                page = Page(title=title, source_url=photo_url)
                page = controller.create_page_to_flowgram(flowgram, page, html)

                output.append(encode.page.to_dict(page))

        return data_response.create(enc, 'ok', output)
    elif service == 'facebook':
        facebook_token = request.session.get('facebook_token', None)
    
        photos = minifb.call('facebook.photos.get',
                             localsettings.FACEBOOK_API_KEY,
                             FACEBOOK_API_SECRET_MINIFB,
                             session_key=facebook_token,
                             aid=album_id)

        output = []
        
        for photo in photos:
            photo_id = str(photo['pid'])
            if photo_id in photo_ids:
                photo_url = photo['src_big']
                title = photo['caption']
            
                html = '<html><head><title>%s</title>' \
                            '<style>@import url("/media/css/photo_importers.css");</style>' \
                        '</head><body><img src="%s" /></body></html>' % (title, photo_url)

                page = Page(title=title, source_url=photo_url)
                page = controller.create_page_to_flowgram(flowgram, page, html)

                output.append(encode.page.to_dict(page))
        
        return data_response.create(enc, 'ok', output)
    elif service == 'picasaweb':
        gd_client.auth_token = request.session['picasaweb_token']
        album_id = album_id[album_id.index('albumid/')+8:]
        photos = gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' %('default', album_id))
        
        output = []
        
        for photo in photos.entry:
            photo_id = photo.gphoto_id.text
            if photo_id in photo_ids:
                photo_url = (photo.media.thumbnail[2].url).replace('/s288/','/s576/')#photo.media.content[0].url
                title = photo.title.text
                
                html = '<html><head><title>%s</title>' \
                            '<style>@import url("/media/css/photo_importers.css");</style>' \
                        '</head><body><img src="%s" /></body></html>' % (title, photo_url)
                        
                page = Page(title=title, source_url=photo_url)
                page = controller.create_page_to_flowgram(flowgram, page, html)
                
                output.append(encode.page.to_dict(page))
        return data_response.create(enc, 'ok', output)

    raise Http404
    
    
@require('POST',
         ['enc=json', 'service', 'flowgram_id', 'photo_ids'],
         ['edit_flowgram'])
def import_photos_with_ids_in_searchresult(request, enc, service, flowgram, photo_ids):
    if service == 'flickr':
        flickr_token = request.session.get('flickr_token', None)
        
        f = flickrapi.FlickrAPI(localsettings.FLICKR_API_KEY,
                                localsettings.FLICKR_API_SECRET,
                                token=flickr_token,
                                store_token=False)
        photos = eval(photo_ids)
        output = []
        # if there is only one photo need to be imported
        if type(photos) == type([]):  
            photo_id = photos[0]
            photo_url = photos[1].replace('_t.jpg', '.jpg')
            title = unicode(photos[2], 'utf-8')
            
            html = '<html><head><title>%s</title>' \
                            '<style>@import url("/media/css/photo_importers.css");</style>' \
                        '</head><body><img src="%s" /></body></html>' % (title, photo_url)
            page = Page(title=title, source_url=photo_url)
            page = controller.create_page_to_flowgram(flowgram, page, html)
            output.append(encode.page.to_dict(page))   
        # if there are more than one photo
        else:
            for (photo_id, photo_url, title) in photos:
                title = unicode(title, 'utf-8')
                photo_url = photo_url.replace('_t.jpg', '.jpg')  
                html = '<html><head><title>%s</title>' \
                            '<style>@import url("/media/css/photo_importers.css");</style>' \
                        '</head><body><img src="%s" /></body></html>' % (title, photo_url)
                page = Page(title=title, source_url=photo_url)
                page = controller.create_page_to_flowgram(flowgram, page, html)
                output.append(encode.page.to_dict(page))
        return data_response.create(enc, 'ok', output)
    if service == 'picasaweb':
        photos = eval(photo_ids)
        output = []
        # if there is only one photo need to be imported
        if type(photos) == type([]):  
            photo_id = photos[0]
            photo_url = photos[1].replace('/s72/', '/s512/')
            title = unicode(photos[2], 'utf-8')
            html = '<html><head><title>%s</title>' \
                            '<style>@import url("/media/css/photo_importers.css");</style>' \
                        '</head><body><img src="%s" /></body></html>' % (title, photo_url)
            page = Page(title=title, source_url=photo_url)
            page = controller.create_page_to_flowgram(flowgram, page, html)
            output.append(encode.page.to_dict(page))        
        # if there are more than one photo 
        else:
            for (photo_id, photo_url, title) in photos:
                title = unicode(title, 'utf-8')
                photo_url = photo_url.replace('/s72/', '/s512/')
                html = '<html><head><title>%s</title>' \
                            '<style>@import url("/media/css/photo_importers.css");</style>' \
                        '</head><body><img src="%s" /></body></html>' % (title, photo_url)
            
                page = Page(title=title, source_url=photo_url)
                page = controller.create_page_to_flowgram(flowgram, page, html)
                output.append(encode.page.to_dict(page))
        return data_response.create(enc, 'ok', output)
    raise Http404

@require('GET', ['service'])
def login(request, service):
    if service == 'flickr':
        f = flickrapi.FlickrAPI(localsettings.FLICKR_API_KEY,
                                localsettings.FLICKR_API_SECRET,
                                token=None,
                                store_token=False)

        return HttpResponseRedirect(f.web_login_url(perms='read'))
    elif service == 'facebook':
        return HttpResponseRedirect(
            'http://www.facebook.com/login.php?api_key=%s&v=1.0' % localsettings.FACEBOOK_API_KEY)
    elif service == 'picasaweb':
        next = '%spicasaweb/callback/' % (localsettings.my_URL_BASE)
        scope = 'http://picasaweb.google.com/data/'
        secure = False
        session = True
        gd_client = gdata.photos.service.PhotosService()
        return HttpResponseRedirect(gd_client.GenerateAuthSubURL(next, scope, secure, session))
    raise Http404
