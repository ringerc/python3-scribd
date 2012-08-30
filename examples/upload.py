"""
Example: upload.py

Uploading a text file to scribd.com and removing it afterwards.
"""

import time
import logging
import tempfile

import scribd


# Set your API key and secret here.
API_KEY = ''
API_SECRET = ''

# Uncomment to enable scribd package debugging.
#logging.basicConfig(level=logging.DEBUG)

last_bytes_sent = 0
def progress(bytes_sent, bytes_total):
    print("%s of %s (%s%%)" % (bytes_sent, bytes_total, bytes_sent*100/bytes_total))

def main():
    # Configure the Scribd API.
    scribd.config(API_KEY, API_SECRET)

    try:
        # Upload the document from a file.
        print 'Uploading a document...'
        
        # Note that the default API user object is used.
        doc = scribd.api_user.upload(
            open('test.txt','rb'),
            progress_callback=progress,
            req_buffer = tempfile.TemporaryFile()
            )
        print 'Done (doc_id=%s, access_key=%s).' % (doc.id, doc.access_key)
        
        # Poll API until conversion is complete.
        while doc.get_conversion_status() != 'DONE':
            print 'Document conversion is processing...'
            # Sleep to prevent a runaway loop that will block the script.
            time.sleep(2)
        print 'Document conversion is complete.'
        
        # Edit various document options.
        # (Note that the options may also be changed during the conversion)
        doc.title = 'This is a test document!'
        doc.description = "I'm testing out the Scribd API!"
        doc.access = 'private'
        doc.language = 'en'
        doc.license = 'c'
        doc.tags = 'test,api'
        doc.show_ads = 'true'
        # Commit all above changes.
        doc.save()
        
        # Delete the uploaded document.
        print 'Deleting the document...'
        doc.delete()
        
        print 'Done (doc_id=%s).' % doc.id

    except scribd.ResponseError, err:
        print 'Scribd failed: code=%d, error=%s' % (err.errno, err.strerror)

if __name__ == '__main__':
    main()
