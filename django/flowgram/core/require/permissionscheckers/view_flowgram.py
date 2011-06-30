def check(request, method_args, transformed_values):
    from flowgram.core import permissions

    return permissions.can_view(request.user, transformed_values['flowgram'])
