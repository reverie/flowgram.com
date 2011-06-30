def from_id(request, id):
    from flowgram.core import models
    from flowgram.core.require.transformers import TransformError

    if not id:
        return ('audio', None)

    try:
        return ('audio', models.Audio.objects.get(id=id))
    except models.Audio.DoesNotExist:
        raise TransformError('Audio with ID "%s" does not exist.' % id)
