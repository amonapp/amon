from django import template
register = template.Library()

@register.filter("mongo_id")
def mongo_id(value):
    try:
        mongo_id = str(value['_id'])
    except:
        mongo_id = "doesnotexist"

    return mongo_id
    


@register.filter("to_str")
def to_str(value):
    
    return str(value)