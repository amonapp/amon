import random


def generate_haiku_name():

    adjs = [
        "autumn", "hidden", "bitter", "misty", "silent", "empty", "dry", "dark",
        "summer", "icy", "delicate", "quiet", "white", "cool", "spring", "winter",
        "patient", "twilight", "dawn", "crimson", "wispy", "weathered", "blue",
        "billowing", "broken", "cold", "damp", "falling", "frosty", "green",
        "long", "late", "lingering", "bold", "little", "morning", "muddy", "old",
        "red", "rough", "still", "small", "sparkling", "throbbing", "shy",
        "wandering", "withered", "wild", "black", "young", "holy", "solitary",
        "fragrant", "aged", "snowy", "proud", "floral", "restless", "divine",
        "polished", "ancient", "purple", "lively", "nameless", "teal", "charming",
        "lush", "tropical", "stunning", "thriving", "fluffy", "gentle", "enigmatic"
    ]

    nouns = [
            "waterfall", "river", "breeze", "moon", "rain", "wind", "sea", "morning",
            "snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter",
            "forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook",
            "butterfly", "bush", "dew", "dust", "field", "fire", "flower", "firefly",
            "feather", "grass", "haze", "mountain", "night", "pond", "darkness",
            "snowflake", "silence", "sound", "sky", "shape", "surf", "thunder",
            "violet", "water", "wildflower", "wave", "water", "resonance", "sun",
            "wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper",
            "frog", "smoke", "star"
    ]

    adj = random.choice(adjs)
    noun = random.choice(nouns)
    rand_num = '{0:04}'.format(random.randint(1000, 10000))


    haiku_name = "{0}-{1}-{2}".format(adj, noun, rand_num)

    return haiku_name
