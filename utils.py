from datetime import datetime


def timedel(from_time, latest_time="now"):
    from datetime import datetime
    format_string = "%Y-%m-%dT%H:%M:%SZ"

    latest_time = datetime.now() if latest_time=="now" else datetime.strptime(latest_time, format_string)

    difference = latest_time - from_time

    return difference.days if difference.days >= 0 else ValueError



def sort_date(date_list):  
    from datetime import datetime
    
    format_string = "%Y-%m-%dT%H:%M:%SZ"
    if type(date_list) is not list:
        return datetime.strptime(date_list, format_string)
    
    sorted_time = [
        datetime.strptime(i, format_string) for i in date_list
    ]
    sorted_time.sort()

    return sorted_time



def list_t_delta(lis):
    delt = []
    for i in range(len(lis)-1):
        delt.append((lis[i+1] - lis[i]).days)

    return delt



def sort_repo_bydate(repo_dict):
    t_list = [i["created_at"] for i in repo_dict.values()]
    t_list.sort()
    
    di = []
    for v in repo_dict.values():
        if v["created_at"] == t_list[0]:
            di.append(v["name"])
            t_list.pop(0)

    return di

