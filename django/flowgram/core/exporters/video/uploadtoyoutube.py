import gdata.youtube
import gdata.youtube.service

from flowgram import localsettings

DEVELOPER_KEY = 'AI39si7hpdbg97Di7RRNWChZcrcTK2LjZSK5Ak8A4iRGJggDTXx_1tQMy4VWXzBotspgr9h-UethNmxtsMEvXEtnaWynOsgmJQ'
CLIENT_ID = 'ytapi-Flowgram-Flowgram-gscn1nve-0'

def get_auth_sub_url(export_to_video_request_id):
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.developer_key = DEVELOPER_KEY
    yt_service.client_id = CLIENT_ID

    return yt_service.GenerateAuthSubURL(
        '%sexport/youtube/%s/2/' % (localsettings.my_URL_BASE, export_to_video_request_id),
        'http://gdata.youtube.com',
        True,
        True)

def upgrade_single_use_token_to_session_token(token):
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.developer_key = DEVELOPER_KEY
    yt_service.client_id = CLIENT_ID

    yt_service.SetAuthSubToken(token)
    yt_service.UpgradeToSessionToken()


def upload(token, video_file_location, flowgram, title, description, keywords, category, private):
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.developer_key = DEVELOPER_KEY
    yt_service.client_id = CLIENT_ID
    yt_service.SetAuthSubToken(token)

    if keywords.find('flowgram') < 0:
        if keywords:
            keywords += ', '
        keywords += 'flowgram'

    # Prepare a media group object to hold our video's meta-data.
    media_group = gdata.media.Group(
        title=gdata.media.Title(text=title),
        description=gdata.media.Description(description_type='plain',
                                            text=description) if description else None,
        keywords=gdata.media.Keywords(text=keywords),
        category=gdata.media.Category(
            text=category,
            scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
            label=category),
        player=None,
        private=gdata.media.Private() if private else None
    )

    # Prepare a geo.where object to hold the geographical location of where the video was recorded.
    where = gdata.geo.Where()
    where.set_location((37.770668, -122.403188))

    # Create the gdata.youtube.YouTubeVideoEntry to be uploaded.
    video_entry = gdata.youtube.YouTubeVideoEntry(media=media_group, geo=where)

    new_entry = yt_service.InsertVideoEntry(video_entry, video_file_location)
