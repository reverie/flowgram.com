"""
iecc.py
by Andrew Badr

Given an original HTML file and a rendered HTML file, tries to create a new rendered HTML
file that includes the original Internet Explorer Conditional Comments in place of any text
that was created as a result of them being rendered.
"""

import sys, codecs, re 

def usage():
    print "Usage: iecc.py <original.html.file> <rendered.html.file> <input_codec>"
    sys.exit()

def read_file(filename):
    f = open(filename, 'rb')
    content = unicode(f.read(), sys.argv[3])
    f.close()
    return content

def main():
    if len(sys.argv) != 4:
        usage()
    orig_html = read_file(sys.argv[1])
    rendered_html = read_file(sys.argv[2])
    altered_html = fix_iecc(orig_html, rendered_html)
    f = codecs.open(sys.argv[2]+'.altered.html', 'wb', "utf-16")
    f.write(altered_html)
    f.close()

def fix_iecc(orig_html, rendered_html):
    first_dlh_end = orig_html.find("<![endif]-->")
    first_dlr_end = orig_html.find("<![endif]>")
    if first_dlh_end == -1 and first_dlr_end == -1:
        print "No IECCs found -- aborting"
        return rendered_html
    if first_dlr_end != -1:
        print "Warning! Use of downlevel-revealed IECC -- aborting"
        return rendered_html
    iecc_start = "<!--\[if [^\]]*\]>"
    iecc_end = "<!\[endif\]-->"
    start_re = re.compile(iecc_start)
    end_re = re.compile(iecc_end)
    starts = [m for m in start_re.finditer(orig_html)]
    ends = [m for m in end_re.finditer(orig_html)]
    print "Starts:", len(starts)
    print "Ends:", len(ends)
    pairs = zip(starts, ends)
    inner_blocks = []
    for start, end in pairs:
        inner_block = orig_html[start.end():end.start()]
        inner_blocks.append(inner_block)
    ccs = zip(starts, inner_blocks, ends)
    cc_has_style =  lambda cc: cc[1].find('.css')!=-1
    cc_has_js = lambda cc: cc[1].lower().find('<script') != -1
    print "There are", len(ccs), "conditional comments\n"
    if filter(cc_has_js,ccs):
        print "Warning! Mixed css and JS in a CC. -- aborting"
        return rendered_html
    replacement_text = []
    for (startm, insides, endm) in ccs:
        replacement_text.append(startm.group() + insides + endm.group())
    replaced = False
    replacement_text = ''.join(replacement_text)
    print "Replacement text:", replacement_text, "\n\n"
    for (startm, insides, endm) in ccs:
        print "Deleting instances of:", insides, '\n\n'
        insides_re_str = re.escape(insides)
        insides_re_str = insides_re_str.replace('"', '"?') #for IE weirdness
        insides_re = re.compile(insides_re_str, re.IGNORECASE | re.VERBOSE)
        if re.search(insides_re, rendered_html):
            print "Found!"
            if replaced:
                rendered_html = re.sub(insides_re, '', rendered_html)
            else:
                rendered_html = re.sub(insides_re, lambda x:replacement_text, rendered_html)
                replaced=True
    if not replaced:
        from flowgram.core.helpers import insert_in_head
        return insert_in_head(rendered_html, replacement_text)
    return rendered_html

if __name__ == '__main__':
    main()
