"""
Handles posting of HTTP multipart/form-data requests.

Based on code posted by Wade Leftwich on:
http://code.activestate.com/recipes/146306/

with modifications to use HTTPConnection class by Chris Hoke

and final touches by me, Arkadiusz Wahlig.

File buffer and progress reporting added by Craig Ringer
"""

import sys
import http.client
import mimetypes
import io
from random import randrange

# How many bytes are copied at once between file-like objects
copy_block_size = 8192
# How many bytes are sent to an uploading connection at once
upload_block_size = copy_block_size


def post_multipart(host, selector, fields=(), headers=None, port=None, req_buffer=None, progress_callback=None):
    """Posts a multipart/form-data request to an HTTP host/port.
    
    Parameters:
      host
        HTTP host name.
      selector
        HTTP request path.
      fields
        POST fields. A sequence of (name, value) tuples where "name" is the
        field name and "value" may be either a string or a (data, name)
        tuple in which case the "data" will be sent as a file of name "name".
        For (data,name) tuples the data part must be a string or a file-like
        object in binary mode, like an io.BytesIO or a file("fn", "r+b")
      headers
        A mapping of additional HTTP headers.
      port
        TCP/IP port. Defaults to 80.
      req_buffer:
        A seekable, writable and readable file-like object to store the
        encoded request in while it is being uploaded. If None (default)
        a StringIO object will be created to store the data. You may
        want to pass a tempfile if you're doing a large upload.
      progress_callback:
        A callable object that takes two integer arguments, the
        number of bytes sent so far and the total bytes to send
        respectively. If None, no callback is invoked. If the
        callback throws any exception then the upload will be aborted.
        
    Returns:
        A httplib.HTTPResponse object.
    """
    boundary = '----------%s--%s----------' % (randrange(sys.maxsize), randrange(sys.maxsize))
    if req_buffer is None:
        req_buffer = io.BytesIO()
    if headers is None:
        headers = {}
    buffer_size = encode_multipart_formdata(fields, boundary, req_buffer)
    # Send the request
    h = http.client.HTTPConnection(host, port)
    try:
        headers['Content-Type'] = 'multipart/form-data; boundary=%s' % boundary
        headers['Content-Length'] = buffer_size
        h.request('POST', selector, body=req_buffer, headers=headers)
    except Exception as ex:
        h.close()
        raise
    return h.getresponse()

def copy_to_buffer(outfile, data):
    """Copy `data' to the writable file-like object `outfile'.
    `data' may its self be a file-like object, or it may be a string
    or byte buffer."""
    if hasattr(data, 'read'):
        # Treat as file-like object and copy between buffers
        buf = data.read(copy_block_size)
        while buf:
            outfile.write(buf)
            buf = data.read(copy_block_size)
    else:
        outfile.write(data)

def encode_multipart_formdata(fields, boundary, req_buffer):
    req_buffer.seek(0)
    boundary = boundary.encode("ascii")
    for key, value in fields:
        req_buffer.write(b'--' + boundary + b'\r\n')
        if isinstance(value, tuple): # file
            data, name = value
            ctype = mimetypes.guess_type(name)[0] or 'application/octet-stream'
            req_buffer.write(('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, name)).encode("utf-8"))
            req_buffer.write(('Content-Type: %s\r\n' % ctype).encode("utf-8"))
            req_buffer.write(b'\r\n')
            copy_to_buffer(req_buffer, data)
        elif isinstance(value, str): # str
            req_buffer.write(('Content-Disposition: form-data; name="%s"\r\n' % key).encode("utf-8"))
            req_buffer.write(b'\r\n')
            req_buffer.write(value.encode("utf-8"))
        else:
            raise TypeError('value must be a tuple or str, not %s' % type(value).__name__)
        req_buffer.write(b'\r\n')
    req_buffer.write(b'--' + boundary + b'--\r\n')
    req_buffer.flush()
    buffer_size = req_buffer.tell()
    req_buffer.truncate()
    req_buffer.seek(0)
    return buffer_size
