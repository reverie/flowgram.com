from django.http import HttpResponseRedirect

from flowgram.core import controller, models
from flowgram.core import helpers
from flowgram.core.require import require
from django.contrib.auth.decorators import login_required

@login_required
@require('GET', ['subscribe_to_username'])
def create_subscription(request, subscribe_to_username):
    url = '/%s/' % subscribe_to_username

    subscribe_to_user = models.User.objects.get(username=subscribe_to_username)

    try:
        # If the subscription alredy exists, do nothing.
        
        models.Subscription.objects.get(user=subscribe_to_user, subscriber=request.user)
    except models.Subscription.DoesNotExist:
        # If the subscription does not alredy exist.
        
        models.Subscription.objects.create(user=subscribe_to_user, subscriber=request.user)

        # UserHistory.
        controller.store_subscription_event(
            {'user': request.user,
             'target_user': subscribe_to_user,
             'eventCode': 'SUB'})

        helpers.add_good_message(request,
                                 'You successfully subscribed to %s.' % subscribe_to_username)

    return HttpResponseRedirect(url)    
    
@login_required
@require('GET', ['subscribed_to_username'])
def remove_subscription(request, subscribed_to_username):
    url = '/subscriptions/'

    subscribed_user = models.User.objects.get(username=subscribed_to_username)
    models.Subscription.objects.filter(user=subscribed_user, subscriber=request.user).delete()        

    # UserHistory.
    controller.store_subscription_event(
        {'user': request.user,
         'target_user': subscribed_user,
         'eventCode': 'UNSUB'})

    helpers.add_good_message(request,
                             'You successfully unsubscribed from %s.' % subscribed_to_username)

    return HttpResponseRedirect(url)
