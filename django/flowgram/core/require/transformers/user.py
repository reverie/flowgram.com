def from_id(request, id):
    from django.contrib.auth import models
    from flowgram.core.require.transformers import TransformError

    if not id:
        return ('user', None)

    try:
        return ('user', models.User.objects.get(id=id))
    except models.User.DoesNotExist:
        raise TransformError('User with ID "%s" does not exist.' % id)


def from_username(request, username):
    from django.contrib.auth import models
    from flowgram.core.require.transformers import TransformError

    if not username:
        return ('user', None)

    try:
        return ('user', models.User.objects.get(username=username))
    except models.User.DoesNotExist:
        raise TransformError('User with ID "%s" does not exist.' % username)
