import hashlib


# Used to identify unique queries
def create_unique_hash(string):
    hash_str = hashlib.md5(string.encode()).hexdigest()

    return hash_str


def get_find_by_string_param(table_data_type=None, name=None):
    find_by_string = 'query'

    find_by_string = 'data' if table_data_type in ['not_found', 'requests'] else find_by_string
    find_by_string = 'table_name' if table_data_type in ['index_hit_rate'] else find_by_string

    if table_data_type == 'tables_size':
        find_by_string_names = {'mongo': 'ns', 'postgres': 'name', 'postgresql': 'name', 'mysql': 'full_name'}
        get_name = find_by_string_names.get(name)
        find_by_string = get_name if get_name != None else find_by_string

    return find_by_string


def sort_header(header_list=None):
    default_score = 0
    scores = {'ns': 2, 'data': 2, 'table': 1, 'database': 2, 'query': 3, 'op': 1, 'table_name': 1, 'db': 2}
    all_fields = []
    for i in header_list:
        get_score = scores.get(i, default_score)
        with_scores =  (i, get_score)
        all_fields.append(with_scores)

    all_fields.sort(key=lambda tup: tup[1], reverse=True)

    try:
        reorganized_header = [i[0] for i in all_fields]
    except:
        reorganized_header = None

    if reorganized_header:
        header_list = reorganized_header

    return header_list
