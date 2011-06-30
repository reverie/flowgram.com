"""
the implementation of flowgram gatherer 
"""

import HyperEstraier
import urllib2, re, os, sys, time, shutil

from os import path

from flowgram import localsettings
from flowgram.core.models import Page, Flowgram, Tag

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

db_path = localsettings.HYPER_ESTRAIER_DB_PATH + "_" + str(time.time())

print("db_path = %s\n" % db_path)

# open the database
db = HyperEstraier.Database()
db.open(db_path, HyperEstraier.Database.DBWRITER | HyperEstraier.Database.DBCREAT)

dir=localsettings.my_WOWKASTDIR

matchstr = re.compile(r'''<.*?>''', re.DOTALL | re.MULTILINE)

users = User.objects.all()

for u in users:
    user = HyperEstraier.Document()
    user.add_attr('@flowgram_type' , 'user')
    user.add_attr('@title' , str(u.username))
    user.add_attr('@uri' , str(u.id))
    user.add_text((u.username).encode('utf-8', 'ignore'))
    db.put_doc(user, HyperEstraier.Database.PDCLEAN )
    
fgs = Flowgram.objects.all()
for fg in fgs:
    try:
        flowgram = HyperEstraier.Document()
        flowgram.add_attr('@flowgram_type' , 'flowgram')
        flowgram.add_attr('@flowgram_id', str(fg.id))
        flowgram.add_attr('@owner_id', str(fg.owner_id))
        flowgram.add_attr('@weight', str(fg.views))
        user = get_object_or_404(User, pk=fg.owner_id)
        flowgram.add_attr('@owner_name', (user.username).encode('utf-8', 'ignore'))
        flowgram.add_attr('@title', "%s" % ((fg.title).encode('utf-8', 'ignore') or "") )
    
        # start to pull out pages from a particular flowgram
        flowgram_path = dir + str(fg.owner_id) + '/' + str(fg.id)
        flowgram.add_attr('@uri', flowgram_path)
        
        # add flowgram description, title, tags, username in text
        flowgram.add_text("%s" % ((fg.description).encode('utf-8', 'ignore') or "") )
        flowgram.add_text("%s" % ((fg.title).encode('utf-8', 'ignore') or ""))
        
        for tag in Tag.objects.filter(flowgram=fg):
            flowgram.add_text("%s" % (tag.name).encode('utf-8', 'ignore'))
        
        flowgram.add_text("%s" % (user.username).encode('utf-8', 'ignore'))
             
        pages = os.listdir(flowgram_path)
        for onepage in pages:
            flowgram.add_text(str(onepage))

            if not str(onepage).endswith('_hl.html'):
                flowgram_page = HyperEstraier.Document()
                flowgram_page.add_attr('@flowgram_type' , 'page')
                flowgram_page_path = flowgram_path + '/' + str(onepage)
                flowgram_page.add_attr('@uri' , str(flowgram_page_path) )
                flowgram_page.add_attr('@title' , str(onepage) )
                flowgram_page.add_attr('@flowgram_id', str(fg.id))
                flowgram_page.add_attr('@weight', '0')
            
                # read the page content from files based on the id
                try:
                    f = open(flowgram_page_path, 'r')
                    onepage_content=f.read()
                    f.close()
                    onepage_content = matchstr.sub('', onepage_content).replace('\n', '')
                    flowgram_page.add_text(onepage_content)
                except IOError:
                    print "error from reading the file (io error):" + flowgram_page_path
                    pass
                except OSError:
                    print "error from reading the file (os error):" + flowgram_page_path
                    pass
                db.put_doc(flowgram_page, HyperEstraier.Database.PDCLEAN)
        db.put_doc(flowgram, HyperEstraier.Database.PDCLEAN)
    except :
        print sys.exc_info()
        print "flowgram with an id of: " + str(fg.id) + " does not exist" +" path is :%s " + str(dir + str(fg.owner_id) + '/' + str(fg.id))

print("\n")

temp_db_path = localsettings.HYPER_ESTRAIER_DB_PATH + "_temp"

if path.islink(temp_db_path):
    os.remove(temp_db_path)

os.symlink(db_path, temp_db_path)
os.rename(temp_db_path, localsettings.HYPER_ESTRAIER_DB_PATH)

db_base_dir = path.dirname(localsettings.HYPER_ESTRAIER_DB_PATH)
dirs = os.listdir(db_base_dir)

cur_time = time.time()
print("cur_time = %d\n" % cur_time)

for dir in dirs:
    if not dir.startswith("casket_"):
        continue
    
    dir = db_base_dir + "/" + dir
    atime = path.getatime(dir)
    delta_atime = cur_time - atime
    
    print("access time of %s = %d delta_atime = %d" % (dir, atime, delta_atime))
    
    if delta_atime > 60 * 60: # access time more than 1 hour ago
        print("deleting %s with delta_atime = %d" % (dir, delta_atime))
        shutil.rmtree(dir)
