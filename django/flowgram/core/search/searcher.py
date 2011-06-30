#!/usr/bin/env python
# vim: fileencoding=utf-8
import sys

from flowgram.core.models import Page, Flowgram, Tag, FlowgramRelated
from flowgram import localsettings
from flowgram.localsettings import FEATURE
from string import punctuation

from django.shortcuts import get_object_or_404


non_search_words = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                    'an','as' ,'at','by','he','his','me','or','us','who','and','for','her','him','if','it','its','nor','of',
                    'our','she','the','to','via','we','you','all','any','but','few','in','off','on','own','so','up','yet','them','they']

def get_attr(hy_id, attr):
    import HyperEstraier
    db = HyperEstraier.Database()
    db.open(localsettings.HYPER_ESTRAIER_DB_PATH, HyperEstraier.Database.DBREADER)
    hy_doc = db.get_doc(hy_id, 0)
    return hy_doc.attr(attr)
    
def search(searchphrase):
    import HyperEstraier
    db = HyperEstraier.Database()
    db.open(localsettings.HYPER_ESTRAIER_DB_PATH, HyperEstraier.Database.DBREADER)
    cond = HyperEstraier.Condition()
    cond.set_phrase(searchphrase)
    result = db.search(cond, 0)
    return result


def main():
    import HyperEstraier
    # parse command line options
    if sys.argv[1] == '1' :
        print '000'
        import re
        # update the FlowgramRelated table
        print '00'
        non_alpha_digit_charaters = re.compile(r'[a-zA-Z]+')
        print '0'
        fgs = Flowgram.objects.all()
        print '1'
        for flowgram in fgs:
            print '2'
            tags = Tag.objects.filter(flowgram=flowgram)
            searchphrase_list = [tag.name for tag in tags] + non_alpha_digit_charaters.findall(flowgram.title)
            searchphrase_list = [word for word in searchphrase_list if word not in non_search_words and word not in punctuation]
            searchphrase = ''
            for i in range(0, len(searchphrase_list)):
                if i < len(searchphrase_list) -1:
                    searchphrase += searchphrase_list[i] + ' OR '
                else:
                    searchphrase += searchphrase_list[i]
            related_flowgrams = []
            print 'use hyperestraier, the searchphrase is: '+ searchphrase
            he_documents = search(searchphrase)
            for he_doc in he_documents:
                if get_attr(he_doc, '@flowgram_type')=='flowgram':
                    one_flowgram = get_object_or_404(Flowgram, pk=str(get_attr(he_doc, '@flowgram_id')))
                    if not one_flowgram.id == flowgram.id and one_flowgram.public == True:
                        related_flowgrams.append(one_flowgram.id)
                        print 'chose: ' + one_flowgram.title
            related_flowgrams = related_flowgrams[:10]
            related_flowgrams_string = ";".join(related_flowgrams)
            FlowgramRelated.objects.create(flowgram=flowgram, related=related_flowgrams_string)
        
        #cache_key = "cached_sets:get_related"
        #return set_from_cache(cache_key, related_flowgrams[:10])
    
    if sys.argv[1] == 0:
        # just show result on the screen
        search_phrase=sys.argv[1:]
        searchphrase = ' '.join(search_phrase)
        print "Your Search Query is: " + searchphrase
        # open the database
        db = HyperEstraier.Database()
        db.open(localsettings.HYPER_ESTRAIER_DB_PATH, HyperEstraier.Database.DBREADER)
        cond = HyperEstraier.Condition()
        cond.set_phrase(searchphrase)
        #cond.set_order('@weight NUMD')
        # get the result of search
        result = db.search(cond, 0)
        # for each document in result
        print "length of founded results is:  " + str(len(result))
        #first = True
        #for i in result:
            #if first:
                #doc = db.get_doc(i, 0)
            #first = False
        #try:
            #doc = db.get_doc(i, 0)
            # display attributes
            #for attr_name in doc.attr_names():
                #print "%s    : %s" % (attr_name, doc.attr(attr_name))
            
            #if doc.attr('@flowgram_type')=='flowgram':
                #print doc.attr('@weight')
               #print doc.attr('@flowgram_id')
                #print doc.cat_texts()
            #print "========================"
        #except:
            #print "result %s document not found" % (str(i))

if __name__=="__main__":
    main()
