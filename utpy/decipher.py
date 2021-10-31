import requests
import re
from .dicts import decode_dict

# Read base.js ---------------------------------
def get_task_list(base_js_url):
    req = requests.get(base_js_url)
    content = req.content.decode()
    funcs = re.search(r'var \w+={(\w+:function\(a,b\){.*\n*.*\n*.*})};', content).groups()[0]
    funcs = funcs.replace('\n', '')
    funcs = funcs.split('},')
    func_dict= {}
    for f in funcs:
        if 'a.length' in f:
            func_name = f.split(':')[0]
            func_dict.update({
                    f'{func_name}': 'task_a'
                }) 
        elif 'splice' in f:
            func_name = f.split(':')[0]
            func_dict.update({
                    f'{func_name}': 'task_b'
                })
        elif 'reverse' in f:
            func_name = f.split(':')[0]
            func_dict.update({
                    f'{func_name}': 'task_c'
                })    
    tasks = re.search(r'a=a\.split\(\"\"\);(.*);return', content).groups()[0]
    tasks = tasks.split(';')
    task_list = []
    for t in tasks:
        b = int(re.search(r"(\d+)", t).groups()[0])
        for k in func_dict.keys():
            if f'.{k}' in t:
                task_list.append((func_dict[k], b))
    return task_list

# Translated js functions ------------------
def splice(list, index, num):
    for i in range(num):
        list[index + i] = ''
    while '' in list:
        list.remove('')
    return list

class Tasks:
    def task_a(a:list, b):
        c = a[0]
        a[0] = a[b % len(a)]
        a[b % len(a)] = c
        return a

    def task_b(a:list, b):
        splice(a, 0, b)

    def task_c(a:list):
        a.reverse()
        return a

def decode_sig(s: str, tsak_list: list):
    a = []
    for i in s:
        a.append(i)
    for t in tsak_list:
        if t[0] == 'task_a':
            Tasks.task_a(a, t[1])
        elif t[0] == 'task_b':
            Tasks.task_b(a, t[1])
        elif t[0] == 'task_c':
            Tasks.task_c(a)
    return ''.join(a)

# Decode signatureCipher ------------------
def decipher(signature, base_js_url):
    for value in decode_dict:
        signature = signature.replace(decode_dict[value], value)
    task_list = get_task_list(base_js_url)
    s = re.search(r'^s=(.*)&sp=sig', signature).groups()[0]
    pre_url = re.search(r'&url=(.*)', signature).groups()[0]
    sig = decode_sig(s, task_list)
    url = pre_url + '&sig=' + sig

    return url