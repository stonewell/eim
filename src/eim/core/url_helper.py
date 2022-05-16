import urllib.request
import ssl

hdr = {
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}


def open_url(url, timeout=30, extra_headers={}, disable_ssl_check=False):
  local_headers = {}
  local_headers.update(hdr)

  if extra_headers is not None:
    local_headers.update(extra_headers)

  ctx = ssl.create_default_context()

  if disable_ssl_check:
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

  opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
  urllib.request.install_opener(opener)

  req = urllib.request.Request(url, headers=local_headers)

  return urllib.request.urlopen(req, timeout=timeout, context=ctx)
