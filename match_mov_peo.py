import difflib
import pandas as pd

def match_things(key_word, name, num, rate):
    li_mov = load_enti_list('mov')
    li_peo = load_enti_list('peo')
    if name == '电影':
        simi = difflib.get_close_matches(key_word, li_mov, num, cutoff=rate)
    if name == '人物':
        simi = difflib.get_close_matches(key_word, li_peo, num, cutoff=rate)
    simi.append('')
    return pd.DataFrame({name:simi})

def load_enti_list(name):#读取实体文件
        f = open(r'./data/word_dic/'+name+'.txt','r', encoding='utf-8')
        return f.read().splitlines()