def to_dict(comment):
    from django.utils.timesince import timesince
    from flowgram.core import avatar
    from flowgram.core.templatetags.filters import chop_at
    return {
        'id': comment.id,
        'ownerAvatar': avatar.get_url(comment.owner.get_profile(), 32),
        'ownerUsername': comment.owner.username,
        'ownerUrl': comment.owner.get_profile().url(),
        'timeAgo': chop_at(timesince(comment.created_at), ","),
        'text': comment.text
    }
