#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

# target script

import sys
import os


def run(bk):
    print ("Entered Target Script run() routine")

    epubversion = "2.0"
    if bk.launcher_version() >= 20160102:
        epubversion = bk.epub_version()

    lastid = None

    # Examples of using the Iterators
    
    # all xhtml/html files
    print("\nExercising: bk.text_iter()")
    for (id, href) in bk.text_iter():
        print(id, href)
        lastid = id

    # all style sheets
    print("\nExercising: bk.css_iter()")
    for (id, href) in bk.css_iter():
        print(id, href)

    # all images
    print("\nExercising: bk.image_iter()")
    for (id, href, mime) in bk.image_iter():
        print(id, href, mime)

    # all fonts
    print("\nExercising: bk.font_iter()")
    for (id, href, mime) in bk.font_iter():
        print(id, href, mime)

    # all files in the OPF manifest
    print("\nExercising: bk.manifest_iter()")
    for (id, href, mime) in bk.manifest_iter():
        print(id, href, mime)
    
    # all files in the OPF spine in spine order
    print("\nExercising: bk.spine_iter()")
    for (id, linear, href) in bk.spine_iter():
        print(id, linear, href)

    # all elements of the OPF guide
    print("\nExercising: bk.guide_iter()")
    for (type, title, href, id) in bk.guide_iter():
        print(type, title, href, id)

    # all audio and video files
    print("\nExercising: bk.media_iter()")
    for (id, href, mime) in bk.media_iter():
        print(id, href, mime)

    # all other ebook files not in the manifest
    print("\nExercising: bk.other_iter()")
    for book_href in bk.other_iter():
        print(book_href)

    # all files selected in the BookBrowser
    print("\nExercising: bk.selected_iter()")
    for (id_type, id) in bk.selected_iter():
        if id_type == "manifest":
            href = bk.id_to_href(id, ow=None)
            mime = bk.id_to_mime(id, ow=None)
            print(id_type, id, href, mime)
        else:
            print(id_type, id)

    # all files in the manifest in an epub3
    print("\nExercising: bk.manifest_epub3_iter()")
    for (id, href, mtype, props, fall, over) in bk.manifest_epub3_iter():
        print(id, href, mtype, props, fall, over)

    # all files in the spine in an epub3
    print("\nExercising: bk.spine_epub3_iter()")
    for (idref, linear, props, href) in bk.spine_epub3_iter():
        print(idref, linear, props, href)

    # Example of hunspell spell checker
    print("\nExercising: the hunspell spell checker")
    dic_dirs = bk.get_dictionary_dirs();
    afffile = None
    dicfile = None
    for adir in dic_dirs:
        afile = os.path.join(adir, "en_US.aff")
        dfile = os.path.join(adir, "en_US.dic")
        if os.path.exists(afile) and os.path.exists(dfile):
            afffile = afile
            dicfile = dfile
            break
    if bk.hspell is not None and afffile is not None and dicfile is not None:
        bk.hspell.loadDictionary(afffile, dicfile)
        checklist =  ["hello", "goodbye", "don't", "junkj", "misteak", "failed-and"]
        for word in checklist:
            res = bk.hspell.check(word)
            if res != 1:
                print(word, "incorrect", bk.hspell.suggest(word))
            else:
                print(word, "correct")    
        bk.hspell.cleanUp()

    # examples for using the bs4/gumbo parser to process xhtml
    print("\nExercising: the gumbo bs4 adapter")
    import sigil_gumbo_bs4_adapter as gumbo_bs4
    samp = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" 
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en-US">
<head><title>testing & entities</title></head>
<body>
  <p class="first second">this&nbsp;is&#160;the&#xa0;<i><b>copyright</i></b> symbol "&copy;"</p>
  <p xmlns:xlink="http://www.w3.org/xlink" class="second" xlink:href="http://www.ggogle.com">this used to test atribute namespaces</p>
</body>
</html>
"""
    soup = gumbo_bs4.parse(samp)
    for node in soup.find_all(attrs={'class':'second'}):
        print(node)

    # Example of reading a non-manifest book file
    print("\nExercising: reading a non-manifest book file")
    stuff = bk.readotherfile('META-INF/container.xml')
    print(stuff)
    
    # Example of reading a file with a specific OPF manifest id
    print("\nExercising: reading a specific OPF manifest id")
    stuff = bk.readfile(lastid)
    if stuff is not None:
        print("Read a file")

    # Example of writing to a file specified by the manifest id
    print("\nExercising: writing to a specific OPF manifest id")
    bk.writefile(lastid, stuff)
    if lastid in bk._w.modified.keys():
        print("Wrote a file")
    
    # Example of adding your own file to the manifest
    print("\nExercising: adding your own file to the manifest")
    data = '<?xml version="1.0" encoding="utf-8"?>\n'
    if epubversion.startswith("3"):
        data += '<!DOCTYPE html>\n'
    else:
        data += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" '
        data += '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'
    data += '<html xmlns="http://www.w3.org/1999/xhtml">\n'
    data += '<head>\n<title>Hello World</title>\n</head>\n'
    data += '<body>\n'
    data += '<p>Hello ... I was Created by a Plugin</p>\n'
    data += '</body>\n'
    data += '</html>\n'
    basename = "my_test.html"
    mt = "application/xhtml+xml"
    uid1 = 'add1'
    bk.addfile(uid1, basename, data, mt)
    if uid1 in bk._w.id_to_mime.keys():
        print("Successfully added a file")
    
    # example of adding it to the end of the spine
    #bk.spine_insert_before(-1, uid1, "yes")
    new_spine = bk.getspine()
    new_spine.append((uid1,"yes"))
    bk.setspine(new_spine)
    # all files in the OPF spine in spine order
    print("\nChecking if added to the spine")
    for (id, linear, href) in bk.spine_iter():
        print(id, linear, href)


    # Examples of Using the Convenience Functions
    print("\nExercising: basename to id mapping")
    bid = bk.basename_to_id(basename)
    if bid == uid1:
        print("Successfully mapped a bassename to its manifest id")

    # Example of creating another file, adding it and then deleting it
    print("\nExercising: creating file, adding it and then deleting it")
    data = '<html>\n<head>\n<title>Hello2</title>\n</head>\n<body><p>Hello World2</p>\n</body>\n</html>\n'
    basename = "my_test2.html"
    uid2 = 'add2'
    bk.addfile(uid2, basename, data)
    if uid2 in bk._w.added :
        print("Added a second file")
    bk.deletefile(uid2)
    if uid2 not in bk._w.added:
        print("Deleted the just added file")

    
    # Example of using the provided stream based QuickParser to parse metadataxml to look for cover id
    print("\nExercising: QuickParser to pase metadataxml to look for cover id")
    print(bk.getmetadataxml())
    ps = bk.qp
    ps.setContent(bk.getmetadataxml())
    res = []
    coverid = None
    # parse the metadataxml, store away cover_id and rebuild it
    for text, tagprefix, tagname, tagtype, tagattr in ps.parse_iter():
        # print tagprefix, tagname, tagtype, tagattr
        if text is not None:
            # print text
            res.append(text)
        else:
            # print tagprefix, tagname, tagtype, tagattr
            if tagname == "meta" and tagattr.get("name",'') == "cover":
                coverid = tagattr["content"]
            res.append(ps.tag_info_to_xml(tagname, tagtype, tagattr))
    print("".join(res))

    # More Examples of using the convenience mapping functions
    print("\nExercising: Mapping of manifest id to file information")
    print("coverid is: ", coverid, bk.id_to_href(coverid), bk.id_to_mime(coverid))

    # Example of copying entire book to your own new directory
    # bk.copy_book_contents_to("/Users/kbhend/Desktop/book_copy")
    
    # Setting the proper Return value is important.
    # 0 - means success
    # anything else means failure
    return 0
 
 
 
def main():
    print("I reached main when I should not have\n")
    return -1
    
if __name__ == "__main__":
    sys.exit(main())

