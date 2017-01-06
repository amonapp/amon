import random

base_colors = [
"#4B97DE",
"#1fb25a",
"#a489d8", 
"#F2832A",
'#8dc48b',
'#15b5c1',
"#ffbc14"]

colors = []
for i in range(0, 5):
    for color in base_colors:
        colors.append(color)

def select_colors(index, type=None, random_color=None):
    if random_color:
        selected_color = random.choice(colors)
    else:
        selected_color = colors[index]
        
    result = {"color": selected_color}
    
    return  result

# def hex_to_rgb(value, opacity=1):
#     value = value.lstrip('#')
#     lv = len(value)
#     return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

# def rgb_to_hex(rgb):
#     return '#%02x%02x%02x' % rgb


def chart_type(type=None):
    
    if type in ['memory','disk']:
        chart_type = 'area' 
    else:
        chart_type = 'line'

    return chart_type

def get_disk_unit(server=None):
    unit = 'MB'

    try:
        distro = server.get('distro', {})
        name = distro.get('name', '')
    except:
        name = "linux"
    
    if 'windows' in name.lower():
        unit = 'GB'


    return unit