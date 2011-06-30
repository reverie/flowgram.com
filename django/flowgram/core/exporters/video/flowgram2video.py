from math import ceil, sqrt
import os, re, sys, traceback, urllib2

from flowgram.core.exporters.video.video_renderer import VideoRenderer
from flowgram.core.models import Audio, Flowgram, Highlight, Page
from flowgram import localsettings


THUMB_HORIZONTAL_RESOLUTION = 800
THUMB_VERTICAL_RESOLUTION = 600

INNER_TAG_REGEX = re.compile(r'<[^>]*>')
OUT_OF_BOUNDS_CHARS_REGEX = re.compile(r'[^\x00-\x7F]')
REPEATED_SPACES_REGEX = re.compile(r'\s+')
SPACES_REGEX = re.compile(r'\s+')

WORDS_PER_MINUTE = 200
MILLIS_PER_WORD = 60000.0 / WORDS_PER_MINUTE


class Flowgram2Video:
    flowgram = None
    horizontal_resolution = None
    mosaic_size = [0, 0]
    pages = None
    storage_dir = None
    thumbs = None
    use_highlight_popups = None
    vertical_resolution = None


    def create_build_reusable_layers_code(self, output):
        print 'create_build_reusable_layers_code'
        
        thumb_ids = self.thumbs.keys()
        num_thumbs = len(thumb_ids)
        print num_thumbs, ' (b) ', thumb_ids
        
        if num_thumbs > 0:
            num_pages_per_row = int(ceil(sqrt(num_thumbs)))
            print '(c) %d' % num_pages_per_row
            print '(c.1)-%d' % len(self.pages)
            print '(c.2)-%d' % ceil(float(len(self.pages)))
            num_rows = int(ceil(float(num_thumbs) / num_pages_per_row))
        else:
            num_pages_per_row = 0
            num_rows = 0

        self.mosaic_size = (num_pages_per_row * THUMB_HORIZONTAL_RESOLUTION,
                            num_rows * THUMB_VERTICAL_RESOLUTION)

        # Building the mosaic.
        print 'Building the mosaic'
        output.append('<build-layer id="mosaic" width="%d" height="%d">' % \
                          self.mosaic_size)
        
        thumb_index = 0
        for row_index in range(num_rows):
            for col_index in range(num_pages_per_row):
                if thumb_index < num_thumbs:
                    output.append('<translate x="%d" y="%d"><draw-image id="thumb_%s" /></translate>' % \
                                      (THUMB_HORIZONTAL_RESOLUTION * col_index,
                                       THUMB_VERTICAL_RESOLUTION * row_index,
                                       self.pages.get(id=thumb_ids[thumb_index]).id))
                    thumb_index += 1
        
        output.append('</build-layer>')

        # Building the title/author label overlay.
        print 'Building the title/author label overlay'
        output.append('<build-layer id="mosaicTitleAndAuthor">')

        title = OUT_OF_BOUNDS_CHARS_REGEX.sub('', self.flowgram.title)

        # Title shadow.
        output.append('<translate x="%d" y="%d">' % (int(0.0625 * self.horizontal_resolution) + 1,
                                                     int(0.0833 * self.vertical_resolution) + 1))
        output.append('<draw-text text="%s" horizontalAlign="center" verticalAlign="bottom" color="#FFFFFF" scaleToFit="true" wrap="true" fontSize="100" minimumFontSize="10" width="%d" height="%d" />' % \
                          (title,
                           int(0.875 * self.horizontal_resolution),
                           int(0.5542 * self.vertical_resolution)))
        output.append('</translate>')

        # Title.
        output.append('<translate x="%d" y="%d">' % (int(0.0625 * self.horizontal_resolution),
                                                     int(0.0833 * self.vertical_resolution)))
        output.append('<draw-text text="%s" horizontalAlign="center" verticalAlign="bottom" color="#000000" scaleToFit="true" wrap="true" fontSize="100" minimumFontSize="10" width="%d" height="%d" />' % \
                          (title,
                           int(0.875 * self.horizontal_resolution),
                           int(0.5542 * self.vertical_resolution)))
        output.append('</translate>')

        # Author info shadow.
        output.append('<translate x="%d" y="%d">' % (int(0.0625 * self.horizontal_resolution) + 1,
                                                     int(0.6375 * self.vertical_resolution) + 1))
        output.append('<draw-text text="%s" horizontalAlign="center" verticalAlign="middle" color="#FFFFFF" scaleToFit="true" minimumFontSize="10" width="%d" height="%d" />' % \
                          ('a Flowgram by ' + self.flowgram.owner.username,
                           int(0.875 * self.horizontal_resolution),
                           int(0.2792 * self.vertical_resolution)))
        output.append('</translate>')

        # Author info.
        output.append('<translate x="%d" y="%d">' % (int(0.0625 * self.horizontal_resolution),
                                                     int(0.6375 * self.vertical_resolution)))
        output.append('<draw-text text="%s" horizontalAlign="center" verticalAlign="middle" color="#000000" scaleToFit="true" minimumFontSize="10" width="%d" height="%d" />' % \
                          ('a Flowgram by ' + self.flowgram.owner.username,
                           int(0.875 * self.horizontal_resolution),
                           int(0.2792 * self.vertical_resolution)))
        output.append('</translate>')

        output.append('</build-layer>')


    def create_frames_code(self, output):
        print 'create_frames_code'

        scale = min(float(self.horizontal_resolution) / self.mosaic_size[0] if self.mosaic_size[0] > 0 else 0,
                    float(self.vertical_resolution) / self.mosaic_size[1] if self.mosaic_size[1] > 0 else 0)
        x_offset = int((self.horizontal_resolution - scale * self.mosaic_size[0]) / 2)
        y_offset = int((self.vertical_resolution - scale * self.mosaic_size[1]) / 2)

        output.append('<frame duration="00:00:01.000" animate="a1=float(0.0 @ 00:00:00.000 .. 1.0 @ 00:00:00.250); a2=float(0.0 @ 00:00:00.250 .. 1.0 @ 00:00:01.000);">')
        output.append('<scale x="%f" y="%f"><draw-image id="missing_thumb" /></scale>' % \
                          (float(self.horizontal_resolution) / 640,
                           float(self.vertical_resolution) / 480))
        output.append('<filter alpha="{{a1}}">')
        output.append('<scale x="%f" y="%f"><translate x="%d" y="%d"><filter alpha="0.75"><draw-image id="mosaic" /></filter></translate></scale>' % \
                          (scale, scale, x_offset, y_offset))
        output.append('<filter alpha="{{a2}}"><draw-image id="mosaicTitleAndAuthor" /></filter>')
        output.append('</filter>')
        output.append('</frame>')

        output.append('<frame duration="00:00:02.000">')
        output.append('<scale x="%f" y="%f"><draw-image id="missing_thumb" /></scale>' % \
                          (float(self.horizontal_resolution) / 640,
                           float(self.vertical_resolution) / 480))
        output.append('<scale x="%f" y="%f"><translate x="%d" y="%d"><filter alpha="0.75"><draw-image id="mosaic" /></filter></translate></scale>' % \
                          (scale, scale, x_offset, y_offset))
        output.append('<draw-image id="mosaicTitleAndAuthor" />')
        output.append('</frame>')

        total_pages_duration = 0

        for page in self.pages:
            page_audio = Audio.objects.filter(page=page)
            if self.use_highlight_popups:
                page_highlights = Highlight.objects.filter(page=page).exclude(name=-1).order_by('time')
            else:
                page_highlights = []
            num_page_highlights = len(page_highlights)
            
            print("page id=%s has %d HLs" % (page.id, num_page_highlights))

            # Using the page duration except where pages do not have audio or highlights.
            used_duration = 0
            page_duration = page.duration
            print 'duration #0 %d' % page.duration
            duration = page_duration
            if page_duration == 10000 and not len(page_audio) and not num_page_highlights:
                # If using the default page duration without audio or highlights on the page,
                # shorten the duration.
                
                print 'duration #1'
                duration = 3000
            elif num_page_highlights:
                # 250 milliseconds is the fade in time for the frame.
                print 'duration #2'
                duration = max(250, page_highlights[0].time)
            
            if len(page_audio) or num_page_highlights:
                page_duration = page_highlights[num_page_highlights - 1].time + 2000 \
                                    if num_page_highlights \
                                    else 0
                print 'duration #3: %d' % page_duration
                for audio in page_audio:
                    page_duration = max(page_duration, audio.time + audio.duration)
                print 'duration #4: %d' % page_duration
                if not num_page_highlights:
                    duration = page_duration
                print 'duration #5: %d' % page_duration
            
            print 'page_duration: %d' % page_duration
            
            output.append('<frame audio-only="true" duration="00:00:00.000">')
            for audio in page_audio:
                (content_type, file_contents) = \
                    load_file_with_url('http://%s/%s.flv' %
                                           (localsettings.S3_BUCKETS[localsettings.S3_BUCKET_AUDIO],
                                            audio.id))
                filename = '%saudio_%s.flv' % (self.storage_dir, audio.id)
                save_file(file_contents, filename)
                output.append('<audio src="%s" start-at="%s" duration="%s" />' % \
                                  (filename,
                                   duration_string_from_millis(audio.time),
                                   duration_string_from_millis(audio.duration)))
            output.append('</frame>')

            output.append('<frame duration="00:00:00.250" animate="a1=float(0.0 @ 00:00:00.000 .. 1.0 @ 00:00:00.250);">')
            output.append('<draw-image id="last_frame_image" />')
            output.append('<filter alpha="{{a1}}"><scale x="%f" y="%f"><draw-image id="thumb_%s" /></scale></filter>' % \
                              (float(self.horizontal_resolution) / THUMB_HORIZONTAL_RESOLUTION,
                               float(self.vertical_resolution) / THUMB_VERTICAL_RESOLUTION,
                               page.id))
            output.append('</frame>')
            used_duration += 250

            show_duration = duration - 250
            output.append('<frame duration="%s">' % duration_string_from_millis(show_duration))
            output.append('<scale x="%f" y="%f"><draw-image id="thumb_%s" /></scale>' % \
                              (float(self.horizontal_resolution) / THUMB_HORIZONTAL_RESOLUTION,
                               float(self.vertical_resolution) / THUMB_VERTICAL_RESOLUTION,
                               page.id))
            output.append('</frame>')
            used_duration += show_duration

            (content_type, file_contents) = \
                load_file_with_url('%sapi/getpage/%s/hl/' % (localsettings.my_URL_BASE, page.id))
                    
            for highlight_index in range(num_page_highlights):
                highlight = page_highlights[highlight_index]

                text = extract_text_for_highlight(highlight, file_contents)
                print("highlight_index=%d len(text)=%d" % (highlight_index, len(text)))

                same_time_highlights_index = highlight_index + 1
                while same_time_highlights_index < num_page_highlights:
                    same_time_highlight = page_highlights[same_time_highlights_index]
                    if same_time_highlight.time - highlight.time < 1000:
                        # If within one second of the current highlight, use this highlight at the
                        # same time.

                        text += ' -- ' + \
                                extract_text_for_highlight(same_time_highlight, file_contents)
                        highlight_index += 1
                        
                        print("highlight_index=%d len(text)=%d" % (highlight_index, len(text)))
                    else:
                        break
                    same_time_highlights_index += 1

                text = REPEATED_SPACES_REGEX.sub(' ', text.strip())
                words = SPACES_REGEX.split(text)
                num_words = len(words)

                if num_words > 20:
                    num_words = 20
                    text = ' '.join(words[0:20]) + '...'
                elif num_words <= 1 and len(text) <= 2:
                    num_words = 0
                    text = ''
                    print("SKIPPING HL num_words=%d len(text)=%d" % (num_words, len(text)))

                highlight_frame_duration = int(ceil(MILLIS_PER_WORD * num_words)) + 1000
                if highlight_index + 1 < num_page_highlights:
                    # If there is a highlight following this highlight.

                    next_highlight = page_highlights[highlight_index + 1]
                    highlight_frame_duration = min(highlight_frame_duration,
                                                   next_highlight.time - highlight.time)

                if text:
                    print("INSERTING HL")
                    
                    # If more than one words were selected or at least five characters, assume the
                    # highlight is legitimate (and not for the sole purpose of scrolling in the
                    # document).
                    output.append('<build-layer id="text_layer">')
                    output.append('<scale x="%f" y="%f"><draw-image id="text_overlay" /></scale>' % \
                                      (float(self.horizontal_resolution) / 640,
                                       float(self.vertical_resolution) / 480))
                    output.append('<translate x="%d" y="%d">' % \
                                      (int(0.0625 * self.horizontal_resolution),
                                       int(0.7083 * self.vertical_resolution)))
                    output.append('<draw-text text="%s" horizontalAlign="center" verticalAlign="middle" color="#000000" scaleToFit="true" wrap="true" fontSize="100" minimumFontSize="10" width="%d" height="%d" />' % \
                                      (text,
                                       int(0.875 * self.horizontal_resolution),
                                       int(0.2083 * self.vertical_resolution)))
                    output.append('</translate>')
                    output.append('</build-layer>')

                output.append('<frame duration="00:00:00.250" animate="a=float(0.0 @ 00:00:00.000 .. 1.0 @ 00:00:00.250);">')
                output.append('<scale x="%f" y="%f"><draw-image id="thumb_%s" /></scale>' % \
                                  (float(self.horizontal_resolution) / THUMB_HORIZONTAL_RESOLUTION,
                                   float(self.vertical_resolution) / THUMB_VERTICAL_RESOLUTION,
                                   page.id))

                if text:
                    output.append('<filter alpha="{{a}}"><draw-image id="text_layer" /></filter>')

                output.append('</frame>')
                used_duration += 250

                if highlight_frame_duration - 500 > 0:
                    show_highlight_duration = highlight_frame_duration - 500
                    output.append('<frame duration="%s">' % \
                                      duration_string_from_millis(show_highlight_duration))
                    output.append('<scale x="%f" y="%f"><draw-image id="thumb_%s" /></scale>' % \
                                      (float(self.horizontal_resolution) / THUMB_HORIZONTAL_RESOLUTION,
                                       float(self.vertical_resolution) / THUMB_VERTICAL_RESOLUTION,
                                       page.id))
                    
                    if text:
                        output.append('<draw-image id="text_layer" />')

                    output.append('</frame>')
                    used_duration += show_highlight_duration

                output.append('<frame duration="00:00:00.250" animate="a=float(1.0 @ 00:00:00.000 .. 0.0 @ 00:00:00.250);">')
                output.append('<scale x="%f" y="%f"><draw-image id="thumb_%s" /></scale>' % \
                                  (float(self.horizontal_resolution) / THUMB_HORIZONTAL_RESOLUTION,
                                   float(self.vertical_resolution) / THUMB_VERTICAL_RESOLUTION,
                                   page.id))

                if text:
                    output.append('<filter alpha="{{a}}"><draw-image id="text_layer" /></filter>')

                output.append('</frame>')
                used_duration += 250

                if page_duration > used_duration:
                    next_duration = page_highlights[highlight_index + 1].time - used_duration if \
                        highlight_index + 1 < num_page_highlights else \
                        page_duration - used_duration
                        
                    if next_duration > 0:
                        output.append('<frame duration="%s">' % \
                                          duration_string_from_millis(next_duration))
                        output.append('<scale x="%f" y="%f"><draw-image id="thumb_%s" /></scale>' % \
                                          (float(self.horizontal_resolution) / THUMB_HORIZONTAL_RESOLUTION,
                                           float(self.vertical_resolution) / THUMB_VERTICAL_RESOLUTION,
                                           page.id))
                        output.append('</frame>')
                        used_duration += next_duration

            total_pages_duration += used_duration

        background_audio = self.flowgram.background_audio
        if background_audio:
            output.append('<frame audio-only="true" duration="00:00:00.000">')
            (content_type, file_contents) = \
                load_file_with_url('http://%s/%s.flv' %
                                       (localsettings.S3_BUCKETS[localsettings.S3_BUCKET_AUDIO],
                                        background_audio.id))
            filename = '%saudio_%s.flv' % (self.storage_dir, background_audio.id)
            save_file(file_contents, filename)
            while total_pages_duration > 0:
                print '<audio src="%s" start-at="%s" duration="%s" volume="%d" />' % \
                                  (filename,
                                   '-%s' % duration_string_from_millis(total_pages_duration),
                                   duration_string_from_millis(
                                       background_audio.duration \
                                           if total_pages_duration > background_audio.duration \
                                           else total_pages_duration),
                                   self.flowgram.background_audio_volume)
                output.append('<audio src="%s" start-at="%s" duration="%s" volume="%d" />' % \
                                  (filename,
                                   '-%s' % duration_string_from_millis(total_pages_duration),
                                   duration_string_from_millis(
                                       background_audio.duration \
                                           if total_pages_duration > background_audio.duration \
                                           else total_pages_duration),
                                   self.flowgram.background_audio_volume))
                if not self.flowgram.background_audio_loop:
                    total_pages_duration = 0
                else:
                    total_pages_duration -= background_audio.duration
            output.append('</frame>')


    def create_load_thumbnails_code(self, output):
        print 'create_load_thumbnails_code'
        
        output.append('<load-image id="text_overlay" src="%s%s" />' % \
                          (localsettings.my_BASE_DIR,
                           'flowgram/core/exporters/video/textOverlay.png'))
        output.append('<load-image id="missing_thumb" src="%s%s" />' % \
                          (localsettings.my_BASE_DIR,
                           'flowgram/core/exporters/video/missingThumb.png'))
        for page in self.pages:
            if self.thumbs.has_key(page.id):
                src = self.thumbs[page.id]
                output.append('<load-image id="thumb_%s" src="%s" />' % (page.id, src))
            else:
                output.append('<build-layer id="thumb_%s" width="%d" height="%d"><scale x="%f" y="%f"><draw-image id="missing_thumb" /></scale></build-layer>' % \
                                    (page.id,
                                     THUMB_HORIZONTAL_RESOLUTION,
                                     THUMB_VERTICAL_RESOLUTION,
                                     THUMB_HORIZONTAL_RESOLUTION / 640.0,
                                     THUMB_VERTICAL_RESOLUTION / 480.0))


    def load_thumbs(self):
        print 'load_thumbs'
        
        output = {}
        for page in self.pages:
            try:
                (content_type, file_contents) = load_file_with_url(
                    '%sapi/getthumbbydims/%s/%d/%d/' % (localsettings.my_URL_BASE,
                                                        page.id,
                                                        THUMB_HORIZONTAL_RESOLUTION,
                                                        THUMB_VERTICAL_RESOLUTION))
                extension = 'png'
                if content_type.endswith('jpg') or content_type.endswith('jpeg'):
                    extension = 'jpg'

                filename = '%sthumb_%s.%s' % (self.storage_dir, page.id, extension)
                save_file(file_contents, filename)
                output[page.id] = filename
            except:
                pass

        self.thumbs = output


    def run(self, flowgram_id, horizontal_resolution, vertical_resolution, storage_dir, use_highlight_popups):
        print 'run'

        self.horizontal_resolution = horizontal_resolution
        self.vertical_resolution = vertical_resolution
        self.storage_dir = storage_dir
        self.use_highlight_popups = use_highlight_popups

        self.flowgram = Flowgram.objects.get(id=flowgram_id)
        self.pages = Page.objects.filter(flowgram=self.flowgram).order_by('position')

        output = ['<render-video width="',
                  str(self.horizontal_resolution),
                  '" height="',
                  str(self.vertical_resolution),
                  '">']

        self.load_thumbs()
        
        self.create_load_thumbnails_code(output)
        self.create_build_reusable_layers_code(output)
        self.create_frames_code(output)

        output.append('</render-video>')

        save_file(''.join(output), '%srender_video.xml' % storage_dir)
        VideoRenderer().run('render_video.xml', storage_dir)


def duration_string_from_millis(millis):
    #print 'duration_string_from_millis'
        
    hours = millis / 3600000
    millis %= 3600000
    
    mins = millis / 60000
    millis %= 60000
    
    secs = millis / 1000
    millis %= 1000

    return '%02d:%02d:%02d.%03d' % (hours, mins, secs, millis)


def extract_text_for_highlight(highlight, file_contents):
    print 'extract_text_for_highlight (%s)' % (highlight.name)
    
    output = []

    start_tag = '"wkhl_span_%d' % highlight.name
    offset = file_contents.find(start_tag, 0)

    while offset > 0:
        offset = file_contents.find('>', offset + len(start_tag))
        if offset < 0:
            # Error case - mismatched span tags.
            break

        offset += 1

        text_start_offset = offset
        
        depth = 1
        while depth > 0:
            closing_span_offset = file_contents.find('</span>', offset)
            #print 'closing_span_offset: %d' % closing_span_offset
            opening_span_offset = file_contents.find('<span', offset)
            #print 'opening_span_offset: %d' % opening_span_offset

            if closing_span_offset < 0 and opening_span_offset < 0:
                # Error case - mismatched span tags.
                return ''.join(output)

            if closing_span_offset >= 0 and \
                    (opening_span_offset < 0 or closing_span_offset < opening_span_offset):
                depth -= 1
                if depth == 0:
                    text_end_offset = closing_span_offset
                    text = file_contents[text_start_offset:text_end_offset]
                    text = INNER_TAG_REGEX.sub('', text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                    text = OUT_OF_BOUNDS_CHARS_REGEX.sub('', text)
                    output.append(text)
                offset = closing_span_offset + 7
            elif opening_span_offset >= 0:
                depth += 1
                offset = opening_span_offset + 5
                
        offset = file_contents.find(start_tag, offset)

    return ' '.join(output)


def load_file_with_url(url):
    print 'load_file_with_url %s' % url
    
    opener = urllib2.build_opener()
    
    url_reader = None
    try:
        try:
            url_reader = opener.open(url)
        except (ValueError, urllib2.URLError):
            raise Exception('Unable to load file with URL %s' % url)
        
        # Handles redirects
        new_url = url_reader.geturl()

        if new_url != url:
            return load_file_with_url(new_url)
        
        return (url_reader.info()['content-type'], url_reader.read())
    finally:
        if url_reader:
            url_reader.close()
        opener.close()


def save_file(content, filename):
    print 'save_file'
    
    file_handle = open(filename, 'wb')
    file_handle.write(content)
    file_handle.close()


#try:
#    use_highlight_popups = sys.argv[5] == 'use-highlight-popups'
#
#    print 'Running with parameters:'
#    print 'Flowgram ID: %s' % sys.argv[1]
#    print 'Width: %s' % int(sys.argv[2])
#    print 'Height: %s' % int(sys.argv[3])
#    print 'Storage Directory: %s' % sys.argv[4]
#    print 'Generate Highlight Popups: %s' % \
#              ('true' if use_highlight_popups else 'false')
#    Flowgram2Video().run(sys.argv[1],
#                         int(sys.argv[2]),
#                         int(sys.argv[3]),
#                         sys.argv[4],
#                         use_highlight_popups)
#except:
#    traceback.print_exc(file=sys.stdout)
