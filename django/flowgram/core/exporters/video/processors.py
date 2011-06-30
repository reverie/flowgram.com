import copy, os, shutil
from math import cos, pi, sin
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from xml.dom import Node

from flowgram.core.exporters.video.helpers import AUDIO_SPS, VIDEO_FPS
from flowgram.core.exporters.video.helpers import add_audio, cget, check_tag, cpop, cpush, cset, \
                                                  get_transformed_point, get_transformed_scale, \
                                                  get_transformed_rotation, save_audio, \
                                                  setup_animation_values
from flowgram import localsettings


def check_if_fits(draw, text, font_file, font_size, wrap, width, height):
    font = ImageFont.truetype(font_file, font_size)
    size = draw.textsize(text, font=font)

    if size[0] <= width and size[1] <= height:
        return True
    
    # If the area, height is too big, or not wrapping and the width is too big, return false right
    # away.
    if size[0] * size[1] > width * height or size[1] > height or (not wrap and size[0] > width):
        return False
    
    (fits, wrapped_text) = wrap_text(draw, text, font, width, height)

    return fits


def draw_image(context, image):
    #print 'draw_image'
    size = image.size

    layer_image = cget(context, 'layer_image')

    transformation = cget(context, 'transformation')

    point = get_transformed_point((0, 0), transformation)
    scale = get_transformed_scale((1, 1), transformation)
    # rotation support
    #rads = get_transformed_rotation(0, transformation)

    width = size[0] * scale[0]
    height = size[1] * scale[1]
    image = image.resize((int(round(width)), int(round(height))), Image.BICUBIC)

    # rotation support
    #angle = rads * 180 / pi
    #image = image.rotate(angle, Image.BICUBIC, True)

    x = point[0]
    y = point[1]

    # rotation support
    #normalized_angle = angle % 360
    #if normalized_angle <= 90:
    #    y -= width * sin(rads)
    #elif normalized_angle <= 180:
    #    x -= width * -cos(rads)
    #    y -= rotated_image.size[1]
    #elif normalized_angle <= 270:
    #    x -= rotated_image.size[0]
    #    y -= height * -sin(rads - 3 * pi / 2)
    #else:
    #    x -= height * -sin(rads)

    x = int(round(x))
    y = int(round(y))

    image = image.crop((0,
                        0,
                        min(image.size[0], layer_image.size[0] - x),
                        min(image.size[1], layer_image.size[1] - y)))
    image.load() # TRYING THIS

    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    layer_image.paste(image, (x, y), image)


def process_audio(video_renderer, tag, context):
    #print 'process_audio'
    (tag, attribs) = check_tag(context,
                               tag,
                               'audio',
                               {'src': 'string',
                                'start-at': 'audio-timestamp',
                                'duration': 'audio-duration'},
                               {'volume': 'int=100'})
    frame_number = cget(context, 'frame_number')
    start_at = attribs['start-at'] + int(float(frame_number[0]) / VIDEO_FPS * AUDIO_SPS)
    add_audio(video_renderer,
              attribs['src'],
              cget(context, 'audio_samples'),
              start_at,
              attribs['duration'],
              attribs['volume'])
    
    return context


def process_build_layer(video_renderer, tag, context):
    #print 'process_build_layer'
    (tag, attribs) = check_tag(context,
                               tag,
                               'build-layer',
                               {'id': 'string'},
                               {'width': 'int',
                                'height': 'int'})
    width = attribs.get('width', cget(context, 'layer_width'))
    height = attribs.get('height', cget(context, 'layer_height'))

    cpush(context)

    layer_image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    cset(context, 'layer_image', layer_image)
    cset(context, 'layer_width', width)
    cset(context, 'layer_height', height)

    context = process_child_tags(video_renderer, tag, context)

    cpop(context)

    cset(context, attribs['id'], layer_image)

    return context


def process_child_tags(video_renderer, tag, context):
    #print 'process_child_tags'
    for child_tag in tag.childNodes:
        if child_tag.nodeType == Node.ELEMENT_NODE:
            context = processing_functions[child_tag.tagName](video_renderer, child_tag, context)
    return context


def process_draw_image(video_renderer, tag, context):
    #print 'process_draw_image'
    (tag, attribs) = check_tag(context,
                               tag,
                               'draw-image',
                               {'id': 'string'})
    #print 'process_draw_image %s' % attribs['id']
    image = cget(context, attribs['id'])

    draw_image(context, image)

    return context


def process_draw_rect(video_renderer, tag, context):
    #print 'process_draw_rect'
    (tag, attribs) = check_tag(context,
                               tag,
                               'draw-rect',
                               {'color': 'color',
                                'width': 'int',
                                'height': 'int'})
    width = attribs.get('width', cget(context, 'layer_width'))
    height = attribs.get('height', cget(context, 'layer_height'))
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))

    image.paste(attribs['color'], [0, 0, width, height])

    draw_image(context, image)
    
    return context

def process_draw_text(video_renderer, tag, context):
    #print 'process_draw_text'
    (tag, attribs) = check_tag(context,
                               tag,
                               'draw-text',
                               {'text': 'string'},
                               {'color': 'color=#000000',
                                'width': 'int',
                                'height': 'int',
                                'horizontalAlign': 'string=left',
                                'verticalAlign': 'string=middle',
                                'scaleToFit': 'boolean=false',
                                'wrap': 'boolean=true',
                                'fontFile': 'string',
                                'fontSize': 'int=18',
                                'minimumFontSize': 'int=10'})
    text = attribs['text']
    
    width = attribs.get('width', cget(context, 'layer_width'))
    height = attribs.get('height', cget(context, 'layer_height'))
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))

    draw = ImageDraw.Draw(image)

    color = attribs['color']
    font_file = attribs.get('fontFile', localsettings.VIDEO['default_font_file'])
    font_size = attribs['fontSize']
    wrap = attribs['wrap']
    horizontal_align = attribs['horizontalAlign']
    vertical_align = attribs['verticalAlign']

    if attribs['scaleToFit']:
        while font_size > attribs['minimumFontSize'] and \
              not check_if_fits(draw, text, font_file, font_size, wrap, width, height):
            font_size -= 1

    font = ImageFont.truetype(font_file, font_size)
    (fits, wrapped_text) = wrap_text(draw, text, font, width, height)

    if len(wrapped_text):
        # Computing the vertical offset.
        vertical_offset = 0
        if vertical_align != 'top':
            size = draw.textsize(wrapped_text[0], font)
            if vertical_align == 'middle':
                vertical_offset = (height - size[1] * len(wrapped_text)) / 2
            elif vertical_align == 'bottom':
                vertical_offset = height - size[1] * len(wrapped_text)

        # Drawing each line.
        for line in wrapped_text:
            # Computing the horizontal offset.
            horizontal_offset = 0
            size = draw.textsize(line, font)
            
            if horizontal_align != 'left':
                if horizontal_align == 'center':
                    horizontal_offset = (width - size[0]) / 2
                elif horizontal_align == 'right':
                    horizontal_offset = width - size[0]
            
            draw.text((horizontal_offset, vertical_offset), line, fill=color, font=font)
            
            vertical_offset += size[1]

    #del draw

    draw_image(context, image)
    
    return context


def process_filter(video_renderer, tag, context):
    #return context
    #print 'process_filter'
    (tag, attribs) = check_tag(context,
                               tag,
                               'filter',
                               None,
                               {'alpha': 'float=1.0',
                                'blur': 'int=0'})
    cpush(context)

    filter_image = Image.new('RGBA', (cget(context, 'layer_width'), cget(context, 'layer_height')))
    cset(context, 'layer_image', filter_image)

    context = process_child_tags(video_renderer, tag, context)

    if attribs['alpha'] < 1.0:
        alpha_image = Image.new('RGBA', (cget(context, 'layer_width'), cget(context, 'layer_height')))
        alpha_image = Image.blend(alpha_image, filter_image, attribs['alpha'])
        filter_image = alpha_image

    if attribs['blur'] > 0:
        for blur_index in range(attribs['blur']):
            filter_image = filter_image.filter(ImageFilter.BLUR)

    cpop(context)

    cpush(context)

    cset(context, 'transformation', [])
    draw_image(context, filter_image)
    cpop(context)
    
    return context


def process_frame(video_renderer, tag, context):
    #print 'process_frame'
    (tag, attribs) = check_tag(context,
                               tag,
                               'frame',
                               {'duration': 'duration'},
                               {'animate': 'string',
                                'audio-only': 'boolean=false'})
    if attribs.has_key('animate'):
        complete_frame_image = None

        for frame_index in range(attribs['duration']):
            # This frame is declared outside the cpush/cpop block because the next frame may wish to
            # access this data.
            frame_image = Image.new('RGBA',
                                    (cget(context, 'layer_width'), cget(context, 'layer_height')))
            complete_frame_image = frame_image
            cset(context, 'layer_image', frame_image)

            cpush(context)

            cset(context, 'animated_frame_index', frame_index)
            setup_animation_values(context, attribs['animate'])

            frame_number = cget(context, 'frame_number')

            context = process_child_tags(video_renderer, tag, context)

            # frame_image.convert("RGB").save('%sframe_%05d.png' % (video_renderer.storage_dir, frame_number[0]))
            # gobaudd
            frame_image.save('%sframe_%05d.png' % (video_renderer.storage_dir, frame_number[0]))
            
            frame_number[0] += 1

            cpop(context)

        if complete_frame_image and not attribs['audio-only']:
            cset(context, 'last_frame_image', complete_frame_image)
    else:
        # Optimized rendering for when animations are not set.
    
        # This frame is declared outside the cpush/cpop block because the next frame may wish to
        # access this data.
        frame_image = Image.new('RGBA',
                                (cget(context, 'layer_width'), cget(context, 'layer_height')))
        cset(context, 'layer_image', frame_image)

        cpush(context)

        frame_number = cget(context, 'frame_number')

        context = process_child_tags(video_renderer, tag, context)

        if not attribs['audio-only']:
            first_frame_filename = '%sframe_%05d.png' % (video_renderer.storage_dir, frame_number[0])
            
            # frame_image.convert("RGB").save(first_frame_filename)
            # gobaudd        
            frame_image.save(first_frame_filename)
            
            frame_number[0] += 1
            for frame_index in range(1, attribs['duration']):
                duplicate_frame_filename = '%sframe_%05d.png' % (video_renderer.storage_dir,
                                                                 frame_number[0])
                shutil.copyfile(first_frame_filename, duplicate_frame_filename)
                frame_number[0] += 1

        cpop(context)

        if not attribs['audio-only']:
            cset(context, 'last_frame_image', frame_image)

    return context


def process_load_image(video_renderer, tag, context):
    #print 'process_load_image'
    (tag, attribs) = check_tag(context,
                               tag,
                               'load-image',
                               {'id': 'string',
                                'src': 'string'})

    image = Image.open(attribs['src'])
    #print 'image: %s' % str(image)
    cset(context, attribs['id'], image)

    return context


def process_render_video(video_renderer, tag, context):
    #print 'process_render_video'
    (tag, attribs) = check_tag(context,
                               tag,
                               'render-video',
                               {'width': 'int',
                                'height': 'int'})

    cpush(context)

    context.append({'layer_width': attribs['width'],
                    'layer_height': attribs['height'],
                    'frame_number': [0],
                    'audio_samples': [],
                    'transformation': []})

    process_child_tags(video_renderer, tag, context)

    save_audio(cget(context, 'audio_samples'),
               '%saudiotrack.wav' % video_renderer.storage_dir)
    
    if localsettings.VIDEO['ffmpeg_path'] != "":
        os.system('%s -i %saudiotrack.wav -r %d -i %sframe_%%05d.png -acodec wmav2 -vcodec wmv2 -s %dx%d %svideo.wmv' %
                      (localsettings.VIDEO['ffmpeg_path'],
                       video_renderer.storage_dir,
                       VIDEO_FPS,
                       video_renderer.storage_dir,
                       attribs['width'],
                       attribs['height'],
                       video_renderer.storage_dir))

    cpop(context)

    return context


def process_rotate(video_renderer, tag, context):
    #print 'process_rotate'
    raise Exception('rotate is not yet supported.')
    # rotation support
    #(tag, attribs) = check_tag(context,
    #                           tag,
    #                           'rotate',
    #                           {'angle': 'float'})
    #
    #transformation = cget(context, 'transformation')
    #
    #rads = attribs['angle'] * pi / 180
    #transformation.append(('rotate', rads))
    #
    #context = process_child_tags(video_renderer, tag, context)
    #
    #transformation.pop()
    #
    #return context

    
def process_scale(video_renderer, tag, context):
    #print 'process_scale'
    (tag, attribs) = check_tag(context,
                               tag,
                               'scale',
                               None,
                               {'x': 'float',
                                'y': 'float'})

    transformation = cget(context, 'transformation')

    x = attribs.get('x', 1.0)
    y = attribs.get('y', 1.0)
    transformation.append(('scale', x, y))

    context = process_child_tags(video_renderer, tag, context)

    transformation.pop()
        
    return context


def process_translate(video_renderer, tag, context):
    #print 'process_translate'
    (tag, attribs) = check_tag(context,
                               tag,
                               'translate',
                               None,
                               {'x': 'int',
                                'y': 'int'})

    transformation = cget(context, 'transformation')

    x = attribs.get('x', 0)
    y = attribs.get('y', 0)
    transformation.append(('translate', x, y))

    context = process_child_tags(video_renderer, tag, context)

    transformation.pop()

    return context


def wrap_text(draw, text, font, width, height):
    #print 'wrap_text'
    words = text.split(' ')
    num_words = len(words)
    used_words = 0
    used_height = 0

    fits = True

    wrapped_text = []

    while used_words < num_words:
        first_word_on_line = words[used_words]
        used_words += 1

        line = [first_word_on_line]

        size = draw.textsize(first_word_on_line, font=font)
        used_width = size[0]
        used_height += size[1]

        if used_width > width or used_height > height:
            fits = False
        else:
            if used_words < num_words:
                next_word = ' ' + words[used_words]
                size = draw.textsize(next_word, font=font)
                
                while used_words < num_words and used_width + size[0] < width:
                    used_width += size[0]
                    used_words += 1
                    line.append(next_word)

                    if used_words < num_words:
                        next_word = ' ' + words[used_words]
                        size = draw.textsize(next_word, font=font)
        
        wrapped_text.append(''.join(line))

    return (fits, wrapped_text)


processing_functions = {'audio': process_audio,
                        'build-layer': process_build_layer,
                        'draw-image': process_draw_image,
                        'draw-rect': process_draw_rect,
                        'draw-text': process_draw_text,
                        'filter': process_filter,
                        'frame': process_frame,
                        'load-image': process_load_image,
                        'render-video': process_render_video,
                        'rotate': process_rotate,
                        'scale': process_scale,
                        'translate': process_translate}
