from flowgram import localsettings
from flowgram.core import controller, log, models
from flowgram.core.require import require


@require('POST', ['flowgram_id'], ['login'])
def add_favorite(request, flowgram):
	try:
		models.Favorite.objects.get(owner=request.user, flowgram=flowgram)
	except:
		# If the specified Flowgram is not already a favorite, add it.
		models.Favorite.objects.create(owner=request.user, flowgram=flowgram)
		controller.record_stat(request, 'add_favorite_website', '0', flowgram.id)

		# UserHistory: FG_FAVED
		if localsettings.FEATURE['notify_fw']:
			try: 
				controller.store_fgfaved_event({
                    'current_user': request.user,
                    'fg_id': flowgram.id,
                    'eventCode': 'FG_FAVED'})
			except:
				log.debug("In api/views.py, attempted to send FG_FAVED event to controller.py/store_fgfaved_event -- FAILED")


@require('POST', ['flowgram_id'], ['login'])
def remove_favorite(request, flowgram):
    try:
        models.Favorite.objects.get(owner=request.user, flowgram=flowgram).delete()
        controller.record_stat(request, 'remove_favorite_website', '0', flowgram.id)
    except:
        # Ignoring Flowgrams that were not already favorites.
        pass
