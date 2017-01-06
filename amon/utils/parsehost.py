from urllib.parse import urlparse


class AmonStruct(object):
    pass


def parsehost(host=None):
    parsed_url = urlparse(host)
    result = AmonStruct()

    result.hostname = parsed_url.hostname if parsed_url.hostname != None else parsed_url.path

    
    result.scheme = 'http' if parsed_url.scheme == '' else parsed_url.scheme
    result.port = 80 if parsed_url.port == None else parsed_url.port

    if result.scheme == 'https' and parsed_url.port == None:
        result.port = 443

    result.host = "{scheme}://{hostname}".format(
        scheme=result.scheme,
        hostname=result.hostname
    )

    

    return result