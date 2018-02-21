import random
import string

def random_id_generator(size=32, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))