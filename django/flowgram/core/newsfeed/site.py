SHORT_SITE_MAX_ITEMS = 6
LONG_SITE_MAX_ITEMS = 100
  
def render_news_feed(request_user, user, type, show_items_after_timestamp=None):
	from flowgram.core.newsfeed import get_news_feed_items
	
	items = get_news_feed_items(request_user, user, show_items_after_timestamp)
	
	if not request_user == user:
	    items = items.exclude(eventCode='UNSUB')
	
	if type == 'S':
		# If a short list.
		items = items[:SHORT_SITE_MAX_ITEMS]
	elif type == 'L' or type == 'R':
		# If a long list or RSS.
		items = items[:LONG_SITE_MAX_ITEMS]
	
	output = []
	
	for item in items:
		if item.currentUser == request_user:
			message = item.secondPersonPresent
		elif item.targetUser == request_user:
			message = item.secondPersonPast
		else:
			message = item.thirdPersonPast
		messageFull = "<li><div>%s<div class=\"clearer\"></div></div></li>" % (message)
		output.append(messageFull)
	
	return ''.join(output)