def can_edit(user, model_object):
    from flowgram.core import models
    
    if user.is_superuser or user == model_object.owner:
        return True

    if isinstance(model_object, models.Flowgram):
        return model_object.is_anonymous()
    elif isinstance(model_object, models.Page):
        return model_object.flowgram and can_edit(user, model_object.flowgram)

    return False


def can_view(user, model_object):
    return True
