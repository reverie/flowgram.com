from math import cos, sin
import re, struct, os

from flowgram import localsettings

AUDIO_SPS = 22050
COLOR_REGEX = re.compile(r'^#([0-9a-fA-F]{6})$')
DURATION_REGEX = re.compile(r'^(-?)(\d{2}):(\d{2}):(\d{2}).(\d{3})$')
STATEMENT_REGEX = re.compile(r'^\s*([a-zA-Z][a-zA-Z0-9]*)\s*=\s*([a-zA-Z][a-zA-Z0-9]*)(?:\s*:\s*([a-zA-Z][a-zA-Z0-9]*))?\s*\(\s*([^@\s]*)\s*@\s*(\d{2}:\d{2}:\d{2}\.\d{3})\s*..\s*([^@\s]*)\s*@\s*(\d{2}:\d{2}:\d{2}\.\d{3})\s*\)\s*$')
VARIABLE_REFERENCE_REGEX = re.compile(r'\{\{\s*([a-zA-Z][a-zA-Z0-9]*)\s*\}\}')
VIDEO_FPS = 15


def add_audio(video_renderer, src, samples, start_at, duration, volume):
    volume_percent = volume / 100.0

    if localsettings.VIDEO['ffmpeg_path'] == "":
        return

    # Adding 0s up through the end of this clip.
    samples.extend([0] * (start_at + duration - len(samples)))

    # Converting to supported format (files might have .wav.wav extention, but that is ok).
    new_src = '%s.wav' % src
    os.system('%s -i %s -ar %d -ac 1 -y %s' % (localsettings.VIDEO['ffmpeg_path'], src, AUDIO_SPS, new_src))
    src = new_src

    # Reading WAVE file header.
    file_handle = open('%s' % src, 'rb')
    if file_handle.read(4) != 'RIFF':
        raise Exception('Wave file format expected (missing RIFF header).')
    (chunk_size,) = struct.unpack('i', file_handle.read(4))
    if file_handle.read(4) != 'WAVE':
        raise Exception('Wave file format expected (missing WAVE header).')
    if file_handle.read(4) != 'fmt ':
        raise Exception('Wave file format expected (expected "fmt " sub-chunk header).')
    # Sub-chunk 1 size.
    file_handle.read(4)
    (format,) = struct.unpack('h', file_handle.read(2))
    if format != 1:
        raise Exception('Only PCM encoding is supported at this time.')
    (num_channels,) = struct.unpack('h', file_handle.read(2))
    if num_channels != 1:
        raise Exception('Only mono audio is supported at this time.')
    (sample_rate,) = struct.unpack('i', file_handle.read(4))
    if sample_rate != AUDIO_SPS:
        raise Exception('Only %d Hz files are supported at this time.' % AUDIO_SPS)
    # Byte rate.
    file_handle.read(4)
    # Block-align.
    file_handle.read(2)
    (bits_per_sample,) = struct.unpack('h', file_handle.read(2))
    if bits_per_sample != 16:
        raise Exception('Only 16-bit files are supported at this time.')

    # Reading samples.
    if file_handle.read(4) != 'data':
        raise Exception('Wave file format expected (expected "data" sub-chunk header).')
    (sub_chunk_2_size,) = struct.unpack('i', file_handle.read(4))
    for sample_index in range(sub_chunk_2_size / 2):
        if sample_index >= duration:
            break

        (sample,) = struct.unpack('h', file_handle.read(2))
        samples[sample_index + start_at] += sample * volume_percent

    file_handle.close()


def cget(context, name):
    for level in reversed(context):
        if level.has_key(name):
            return level.get(name)
    raise Exception('No value found for %s in context.' % name)


def check_attribute(context, tag, attribute_name, attribute_type):
    attribute = tag.getAttribute(attribute_name)
    
    return get_value_of(context, attribute, attribute_type)


def check_tag(context, tag, type, required_attribs=None, optional_attribs=None):
    if tag.tagName != type:
        raise Exception('Tag type %s not allowed, expected %s.' % (tag.tagName, type))

    attribs = {}

    if required_attribs:
        for attribute_name in required_attribs:
            if not tag.hasAttribute(attribute_name):
                raise Exception('Attribute %s is required.' % attribute_name)

            attribute_type = required_attribs.get(attribute_name)
            attribs[attribute_name] = check_attribute(context, tag, attribute_name, attribute_type)

    if optional_attribs:
        for attribute_name in optional_attribs:
            if not tag.hasAttribute(attribute_name):
                optional_attrib = optional_attribs.get(attribute_name)
                if optional_attrib.find('=') >= 0:
                    (attribute_type, default_value) = optional_attrib.split('=', 2)
                    attribs[attribute_name] = get_value_of(context, default_value, attribute_type)
                continue

            optional_attrib = optional_attribs.get(attribute_name)
            if optional_attrib.find('=') >= 0:
                (attribute_type, default_value) = optional_attribs.get(attribute_name).split('=', 2)
            else:
                attribute_type = optional_attribs.get(attribute_name)

            attribs[attribute_name] = check_attribute(context, tag, attribute_name, attribute_type)

    return (tag, attribs)


def cpop(context):
    context.pop()
    

def cpush(context):
    context.append({})


def cset(context, name, value):
    context[-1][name] = value


def get_transformed_point(point, transformation):
    point_matrix = [point[0], 0.0, 0.0,
                    point[1], 0.0, 0.0,
                    0.0, 0.0, 0.0]

    for operation in transformation:
        if operation[0] == 'translate':
            x = operation[1]
            y = operation[2]
            point_matrix = matrix_add([x, 0, 0,
                                       y, 0, 0,
                                       0, 0, 0], point_matrix)
        elif operation[0] == 'scale':
            x = operation[1]
            y = operation[2]
            point_matrix = matrix_mult([x, 0, 0,
                                        0, y, 0,
                                        0, 0, 1], point_matrix)
        elif operation[0] == 'rotate':
            rads = operation[1]
            point_matrix = matrix_mult([cos(rads), -sin(rads), 0,
                                        sin(rads), cos(rads), 0,
                                        0, 0, 1], point_matrix)

    return (point_matrix[0], point_matrix[3])


def get_transformed_rotation(rads, transformation):
    for operation in transformation:
        if operation[0] == 'rotate':
            rads += operation[1]

    # debug
    from math import pi
    
    return rads


def get_transformed_scale(scale, transformation):
    new_scale = [scale[0], scale[1]]

    for operation in transformation:
        if operation[0] == 'scale':
            new_scale[0] *= operation[1]
            new_scale[1] *= operation[2]

    return new_scale


def get_value_of(context, value, type):
    match = VARIABLE_REFERENCE_REGEX.search(value)
    while match:
        value = value.replace(match.group(0), str(cget(context, match.group(1))))
        match = VARIABLE_REFERENCE_REGEX.search(value)

    try:
        if type == 'boolean':
            if value == 'true':
                return True
            elif value == 'false':
                return False
            else:
                raise Exception()
        elif type == 'color':
            match = COLOR_REGEX.match(value)
            if not match:
                raise Exception()
            hex_value = match.group(1)
            red = hex_value[0:2]
            green = hex_value[2:4]
            blue = hex_value[4:6]
            print 'color: ', (int(red, 16), int(green, 16), int(blue, 16))
            return (int(red, 16), int(green, 16), int(blue, 16))
        elif type == 'duration' or type == 'timestamp':
            match = DURATION_REGEX.match(value)
            if not match:
                raise Exception()
            return (-1 if match.group(1) else 1) * int(round((int(match.group(2)) * 3600 +\
                              int(match.group(3)) * 60 +\
                              int(match.group(4)) +\
                              int(match.group(5)) / 1000.0) * VIDEO_FPS))
        elif type == 'audio-duration' or type == 'audio-timestamp':
            match = DURATION_REGEX.match(value)
            if not match:
                raise Exception()
            return (-1 if match.group(1) else 1) * int(round((int(match.group(2)) * 3600 +\
                              int(match.group(3)) * 60 +\
                              int(match.group(4)) +\
                              int(match.group(5)) / 1000.0) * AUDIO_SPS))
        elif type == 'int':
            return int(value)
        elif type == 'float':
            return float(value)
    except:
        raise Exception('Value %s not allowed, %s expected.' % (value, type))

    return value


def interpolate(type, interpolation_type, start_value, end_value, progress, duration):
    if duration == 0:
        return end_value

    if type == 'float':
        if interpolation_type == 'linear':
            return (end_value - start_value) * (float(progress) / duration) + start_value
    if type == 'int':
        if interpolation_type == 'linear':
            return int((end_value - start_value) * (float(progress) / duration) + start_value)


def matrix_add(lhs, rhs):
    output = []
    for index in range(len(lhs)):
        output.append(lhs[index] + rhs[index])
    return output


def matrix_mult(lhs, rhs):
    return [lhs[0] * rhs[0] + lhs[1] * rhs[3] + lhs[2] * rhs[6],
                lhs[0] * rhs[1] + lhs[1] * rhs[4] + lhs[2] * rhs[7],
                lhs[0] * rhs[2] + lhs[1] * rhs[5] + lhs[2] * rhs[8],
            lhs[3] * rhs[0] + lhs[4] * rhs[3] + lhs[5] * rhs[6],
                lhs[3] * rhs[1] + lhs[4] * rhs[4] + lhs[5] * rhs[7],
                lhs[3] * rhs[2] + lhs[4] * rhs[5] + lhs[5] * rhs[8],
            lhs[6] * rhs[0] + lhs[7] * rhs[3] + lhs[8] * rhs[6],
                lhs[6] * rhs[1] + lhs[7] * rhs[4] + lhs[8] * rhs[7],
                lhs[6] * rhs[2] + lhs[7] * rhs[5] + lhs[8] * rhs[8]]


def save_audio(samples, filename):
    file_handle = open(filename, 'wb')

    num_sample_bytes = len(samples) * 2

    # Writing header.
    file_handle.write('RIFF')
    file_handle.write(struct.pack('i', 36 + num_sample_bytes))
    file_handle.write('WAVE')

    # Writing "fmt " sub-chunk.
    file_handle.write('fmt ')
    # Sub-chunk 1 size.
    file_handle.write(struct.pack('i', 16))
    # Format.
    file_handle.write(struct.pack('h', 1))
    # Number of channels.
    file_handle.write(struct.pack('h', 1))
    # Sample rate.
    file_handle.write(struct.pack('i', AUDIO_SPS))
    # Bytes per second.
    file_handle.write(struct.pack('i', AUDIO_SPS * 2))
    # Block align.
    file_handle.write(struct.pack('h', 2))
    # Bits per sample.
    file_handle.write(struct.pack('h', 16))

    # Writing "data" sub-chunk.
    file_handle.write('data')
    # Sub-chunk 2 size.
    file_handle.write(struct.pack('i', num_sample_bytes))

    for sample in samples:
        file_handle.write(struct.pack('h', min(32767, max(-32768, int(round(sample))))))

    file_handle.close()


def setup_animation_values(context, statements_string):
    animated_frame_index = cget(context, 'animated_frame_index')

    statements = statements_string.split(';')
    for statement in statements:
        match = STATEMENT_REGEX.match(statement)
        if match:
            variable_name = match.group(1)
            type = match.group(2)
            interpolation_type = match.group(3) or 'linear'
            start_value = match.group(4)
            start_time = match.group(5)
            end_value = match.group(6)
            end_time = match.group(7)

            start_value = get_value_of(context, start_value, type)
            start_frame = get_value_of(context, start_time, 'duration')
            end_value = get_value_of(context, end_value, type)
            end_frame = get_value_of(context, end_time, 'duration')
            if animated_frame_index >= start_frame and animated_frame_index <= end_frame:
                cset(context, variable_name, interpolate(type,
                                                         interpolation_type,
                                                         start_value,
                                                         end_value,
                                                         animated_frame_index - start_frame,
                                                         end_frame - start_frame))
            elif animated_frame_index < start_frame:
                # Setting a value for the variable if this is the first time the variable will be
                # set.
                try:
                    cget(context, variable_name)
                except:
                    cset(context, variable_name, start_value)
            elif animated_frame_index > end_frame:
                cset(context, variable_name, end_value)
