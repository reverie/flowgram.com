def from_id(request, id):
    from flowgram.core import models
    from flowgram.core.require.transformers import TransformError

    if not id:
        return ('flowgram', None)

    try:
        return ('flowgram', models.Flowgram.objects.get(id=id))
    except models.Flowgram.DoesNotExist:
        raise TransformError('Flowgram with ID "%s" does not exist.' % id)
