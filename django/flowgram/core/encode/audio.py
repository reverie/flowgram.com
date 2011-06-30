def to_dict(audio):
    return {
        'id': audio.id,

        'duration': audio.duration,
        'time': audio.time,
    }
