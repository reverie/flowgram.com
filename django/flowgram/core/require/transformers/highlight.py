def from_id(request, id):
    from flowgram.core import models
    from flowgram.core.require.transformers import TransformError

    if not id:
        return ('highlight', None)

    try:
        return ('highlight', models.Highlight.objects.get(id=id))
    except models.Highlight.DoesNotExist:
        raise TransformError('Highlight with ID "%s" does not exist.' % id)
