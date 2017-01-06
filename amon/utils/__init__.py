import random
import string


def generate_random_string(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class AmonStruct(object):
    pass