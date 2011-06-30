from flowgram.core.require.transformers import audio, flowgram_transformer, highlight, page, user
from flowgram.core.require.transformers import boolean_transformer, csl, float_transformer, \
                                                  int_transformer

class TransformError(Exception): pass

transform_funcs = {
    'aid': audio.from_id,
    'audio_id': audio.from_id,
    'fgid': flowgram_transformer.from_id,
    'flowgram_id': flowgram_transformer.from_id,
    'highlight_id': highlight.from_id,
    'page_id': page.from_id,
    'pid': page.from_id,
    'uid': user.from_id,
    'user': user.from_username,
    'username': user.from_username,
    'user_id': user.from_id,
    
    'boolean': boolean_transformer.from_string,
    'csl': csl.from_string,
    'float': float_transformer.from_string,
    'int': int_transformer.from_string,
}
