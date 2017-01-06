def check_data_for_period(data_dict):

    total = data_dict.get('total', 0)
    if total > 0:
        return True
    else:
        return False