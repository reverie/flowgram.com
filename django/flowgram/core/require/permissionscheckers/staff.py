from flowgram.core import log


def check(request, method_args, transformed_values):
    authorized = request.user.is_authenticated() and request.user.is_staff
    if not authorized:
        log.sec_req(request, "Tried to access FG press admin page")
    return authorized
