import sys, traceback
from xml.dom import minidom

from flowgram.core.exporters.video.processors import process_render_video


class VideoRenderer:
    filename = None
    storage_dir = None

    def run(self, filename, storage_dir):
        self.filename = filename
        self.storage_dir = storage_dir

        try:
            document = minidom.parse('%s%s' % (storage_dir, filename))
        except Exception, e:
            print 'There was a problem parsing the XML in the specified file: %s' % str(e)
            return
        
        print 'processing... %s' % str(document.firstChild)
        process_render_video(self, document.firstChild, [])


#try:
#    VideoRenderer().run(sys.argv[1], sys.argv[2])
#except:
#    traceback.print_exc(file=sys.stdout)
