from django.urls import reverse
from django.conf import settings
from django import template
from django.utils.encoding import smart_str


register = template.Library()

import re
kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")


class URLNode(template.Node):
    def __init__(self, view_name, args, kwargs):
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs

    def render(self, context):
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        url = reverse(self.view_name, kwargs=kwargs)
    
        domain_url = settings.HOST
        if domain_url.endswith('/'):
            domain_url = domain_url[:-1]

        _url = "{base}{url}".format(base=domain_url, url=url)

        return _url


def base_url(parser, token):
    bits = token.split_contents()
    view_name = bits[1]

    view_name = view_name.strip('\'"') 
    
    args = []
    kwargs = {}
    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise template.TemplateSyntaxError("Malformed arguments to url tag")
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))
        
    return URLNode(view_name, args, kwargs)

register.tag('base_url', base_url)

