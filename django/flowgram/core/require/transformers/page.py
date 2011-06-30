def from_id(request, id):
    from flowgram.core import models
    from flowgram.core.require.transformers import TransformError

    if not id:
        return ('page', None)

    try:
        return ('page', models.Page.objects.get(id=id))
    except models.Page.DoesNotExist:
        raise TransformError('Page with ID "%s" does not exist.' % id)
