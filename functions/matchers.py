from unidecode import unidecode
from difflib import SequenceMatcher


def home_made(mydico, txt, n):
    ''' Matches the txt input in mydico to return n items based on spelling, 
    jelly jaro can be used also. Here mydico needs to be in the format : {key : recipe dic} '''
    # check if len recipes is long enought
    
    sorted = []
    sorted_filter = []
    output = {}
    txt = unidecode(txt)
    input = txt.lower().replace('-',' ').split(' ')
    
    for key in mydico.keys():
        r = 0
        # this was added to allow several dictionnaries note data and recipe
        if mydico[key].get("title"): 
            title = mydico[key]['title'].lower()
            title_unidecode = unidecode(title)
        else:
            title_unidecode = key.lower()
        
        title_unidecode_list = title_unidecode.split(' ')
        if input[0] in title_unidecode_list:
            r+= 0.5
        if len(input) > 1:
            for word in input[1:]:
                if word in title_unidecode:
                    r+= len(word)/(len(title_unidecode)*2)
        sorted.append([key,r])
    
    sorted.sort(key=lambda col: col[1], reverse=True)

    for i in range(n):
        key = sorted[i][0]
        sorted_filter.append(key)
        output[key] = mydico[key]

    return output

def DiffSequenceMatcher(mydico, str1, n):
    output = {}
    sorted = []
    for key in mydico.keys():
        str2 = mydico[key]['title'].lower()
        r= SequenceMatcher(None, str1, str2).ratio()
        sorted.append([key,r])
    sorted.sort(key=lambda col: col[1],reverse=True)

    for i in range(n):
        key = sorted[i][0]
        output[key] = mydico[key]

    return output