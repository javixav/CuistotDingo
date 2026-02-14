from json import dumps as json_dumps
from kivy.logger import Logger

def save_config(config_input):
    # $deplace
    ''' Be carefull with that, because json specification 
    make boolean in lower case (javascript spec) you need to make the change 
    when you are in string type. '''

    my_bool = config_input["ingredient_max_calcul"]

    json_config_input = json_dumps(config_input, ensure_ascii=False, indent= 4)
    if my_bool:
        json_config_input = json_config_input.replace('"ingredient_max_calcul": true', '"ingredient_max_calcul": True')
    else:
        json_config_input = json_config_input.replace('"ingredient_max_calcul": false', '"ingredient_max_calcul": False')

    with open('config.py', 'w',encoding='utf-8') as f:
        f.write("config_input = " + str(json_config_input))

def ingredient_max_calcul(config_input, recipes):
    # $deplace
    ''' Calculate max number smart tile each time a recipee is added. And save this to config file. '''

    if not config_input["ingredient_max_calcul"]:
        maxi = 0; ingredient = ''
        for key in recipes[3].keys():
            n = len(recipes[3][key])
            if n> maxi:
                maxi = n
                ingredient = key

        config_input["max_ingredient"] = maxi
        config_input["ingredient_max_calcul"] = True

        save_config(config_input)
    else: 
        maxi = config_input["max_ingredient"]
    return maxi

def log(msg):
    Logger.info(msg)

def log_warning(msg):
    Logger.warning(msg)