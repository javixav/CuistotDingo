from unidecode import unidecode
from difflib import SequenceMatcher


def home_made(mydico,txt,n):
    ''' Matches the txt input in mydico to return n items based on spelling, 
    jelly jaro can be used also. Here mydico needs to be in the format : {key : recipe dic} '''
    
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

        for word in input:
            if word in title_unidecode:
                r+= len(word)/len(title_unidecode)

        # added so it values the first occurence for recipes mostly
        if input[0] ==  title_unidecode_list[0]:
            r+=0.25     
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
