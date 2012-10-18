"""
Example: scribdc.py

Uploading a text file to scribd.com and removing it afterwards.

Contributed by massimo.dipierro.
"""

import time
import scribd
import optparse
import urllib


def main():
    usage = """Usage:
    - to upload a file in scribd
    python scridbc.py -K <api key> -S <api secret> -i <input filename> -t <title>
    - to delete an existing file
    python scridbc.py -K <api key> -S <api secret> -c <doc_id> -d
    - to convert any file (doc,xls,ppt,etc.) to pdf
    python scridbc.py -K <api key> -S <api secret> -i <input filename> -p <output> -d
    - to convert any file (doc,xls,ppt,etc.) to txt
    python scridbc.py -K <api key> -S <api secret> -i <input filename> -x <output> -d
    """

    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-K", "--key", dest='key',default='',
                      help="the API KEY (required)")
    parser.add_option("-S", "--secret", dest='secret',default='',
                      help="the API SECRET (required)")
    parser.add_option("-c", "--code", dest="code",
                      help="document code")    
    parser.add_option("-i", "--input", dest="input",default=None,
                      help="input filename to upload")
    parser.add_option("-t", "--title", dest="title",default='',
                      help="document title")
    parser.add_option("-l", "--license", dest="license",default='c',
                      help="document license")
    parser.add_option("-L", "--language", dest="language",default='en',
                      help="document language")
    parser.add_option("-D", "--description", dest="description",default='',
                      help="file with document description")
    parser.add_option("-m", "--mode", dest="mode",default='public',
                      help="public or private")
    parser.add_option("-g", "--tags", dest="tags",default='',
                      help="comma separated tags")
    parser.add_option("-p", "--pdf", dest="pdf",default=None,
                      help="output pdf filename")
    parser.add_option("-x", "--txt", dest="txt",default=None,
                      help="output txt filename")    
    parser.add_option("-d", "--delete",
                      action="store_true", dest="delete", default=False,
                      help="delete the document")    
    parser.add_option("-a", "--ads", dest='ads',default='on',
                      help="ads on or off")
    (options, args) = parser.parse_args()    

    # Configure the Scribd API.
    scribd.config(scribd_settings.API_KEY, scribd_settings.API_SECRET)

    try:
        if options.input:
            # Upload the document from a file.
            print 'Uploading a document...'
            
            # Note that the default API user object is used.
            doc = scribd.api_user.upload(open(options.input,'rb'))
            print 'Done (doc_id=%s, access_key=%s).' % (doc.id, doc.access_key)
            
            # Poll API until conversion is complete.
            n=2
            while doc.get_conversion_status() != 'DONE':
                print 'Document conversion is processing... (retrying in %ssecs)' % n
                # Sleep to prevent a runaway loop that will block the script.
                time.sleep(n)
                n *= 2
            print 'Document conversion is complete.'
        
            # Edit various document options.
            # (Note that the options may also be changed during the conversion)
            doc.title = options.title or options.input
            if options.description and os.path.exists(options.description):
                doc.description = open(options.description,'r').read()
            else:
                doc.description = ''
            doc.access = options.mode
            doc.language = options.language
            doc.license = options.license
            doc.tags = options.tags
            doc.show_ads = 'true' if options.ads=='on' else 'false'
            # Commit all above changes.
            doc.save()
            doc.get_download_url(doc_type='pdf')
            print 'Document uploaded (doc_id=%s).' % doc.id
        elif options.code:
            doc = scribd.api_user.get(options.code)            
            print 'Document found (doc_id=%s).' % doc.id
        else:
            print 'Invalid arguments'
            return
        pdf = doc.get_download_url(doc_type='pdf')
        print 'PDF URL: '+pdf
        if options.pdf:
            open(options.pdf,'wb').write(urllib.urlopen(pdf).read())
            print 'PDF file retrieved'
        txt = doc.get_download_url(doc_type='txt')
        print 'TXT URL: '+txt
        if options.txt:
            open(options.txt,'wb').write(urllib.urlopen(txt).read())
            print 'TXT file retrieved'
        if options.delete:
            doc.delete()
            print 'Document deleted (doc_id=%s).' % doc.id

    except scribd.ResponseError, err:
        print 'Scribd failed: code=%d, error=%s' % (err.errno, err.strerror)


if __name__ == '__main__':
    main()
