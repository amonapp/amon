# Copyright (c) 2009 Lobstertech, Inc.
# Licensed MIT
import types

def smart_unicode(s, encoding='utf-8', errors='strict'):
    if type(s) in (unicode, int, long, float, types.NoneType):
        return unicode(s)
    elif type(s) is str or hasattr(s, '__unicode__'):
        return unicode(s, encoding, errors)
    else:
        return unicode(str(s), encoding, errors)

def smart_str(s, encoding='utf-8', errors='strict', from_encoding='utf-8'):
    if type(s) in (int, long, float, types.NoneType):
        return str(s)
    elif type(s) is str:
        if encoding != from_encoding:
            return s.decode(from_encoding, errors).encode(encoding, errors)
        else:
            return s
    elif type(s) is unicode:
        return s.encode(encoding, errors)
    elif hasattr(s, '__str__'):
        return smart_str(str(s), encoding, errors, from_encoding)
    elif hasattr(s, '__unicode__'):
        return smart_str(unicode(s), encoding, errors, from_encoding)
    else:
        return smart_str(str(s), encoding, errors, from_encoding)
