#/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/
#   This script is meant to get recipes from input ingredient 
#   and input recipes. See the Readme file for more information 
#/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/**/

#-------------------------------------------------------------------------------------------------------------------------------------------------
#cuisine part 1 : Algo pour afficher les recettes compatibles avec les ingrédients frigo et vaisselier
#-------------------------------------------------------------------------------------------------------------------------------------------------
import time# Pour connaitre la durée d'execution
import csv 
import os
import sys
import json
# from core.input_recettes import recettes
# from core.input_frigo import mydico_frigo
from importlib import reload

# import subprocess
PATH_FILES = os.path.dirname(__file__)

def get_recipes():
    
    a=time.perf_counter()
    # ........................................................
    # Ouverture d'un fichier en *lecture*:
    # Python n'accepte que les doubles\\ // pour les chemins
    # ........................................................
    # added to dynamically reload recipes from app
    
    from core import input_recettes as recettes_reloaded
    recettes_reloaded  = reload(recettes_reloaded)
    global recettes 
    recettes = recettes_reloaded.recettes

    from core import input_frigo as input_frigo_to_reload
    mydico_frigo_reloaded  = reload(input_frigo_to_reload)
    global mydico_frigo 
    mydico_frigo = mydico_frigo_reloaded.mydico_frigo


    nb_recettes = len(recettes['recipes'])

    #.........................................................................
    # Création de data de saison
    # ...............................................................................

    csv_file = open(os.path.join(PATH_FILES,"saison.csv"), newline='', encoding ='utf-8')
    tab_saison = csv.reader(csv_file)
    index_du_mois=time.localtime()[1]-1
    tab_saison_mois=[i[index_du_mois] for i in tab_saison]
    list_legume_fruit=['betterave','carotte','celeri','champignon','chou','chou de bruxelles','chou fleur','courge','cresson','endive','epinard','mache','navet','oignon','panais','poireau','potiron','salsifis','topinambour','citron','clementine','kiwi','mandarine','orange','poire','pomme','pamplemousse','radis','asperge','fenouil','rhubarbe','artichaut','concombre','courgette','laitue','petit pois','fraise','aubergine','blette','haricot vert','poivron','tomate','abricot','cassis','cerise','framboise','groseille','melon','ail','mais','figue','myrtille','nectarine','prune','mirabelle','mure','quetsche','brocoli','noisette','noix','raisin','reine claude','celeri branche','echalotte','chataigne','coing']#liste des légumes_fruit sur toute l'année qui servira de premier filtre
    
    # ...............................................................................
    # Création d'une liste frigo contenant les ingrédients frigo séparés par un espace
    # ...............................................................................

    output = {} ; output_1_ing = {}

    for key in recettes["recipes"].keys():
        j=0;k=0;ing_manquant='';string_saison='Recette de saison'
        str_pas_de_saison='';ing_pas_de_saison='';recette = recettes["recipes"][key]
        ingredients = recette["ingredients"];nb_ing=len(ingredients)
        for j in range(nb_ing):
            if ingredients[j] in mydico_frigo["ingredients"]:
                k+=1
            else:
                ing_manquant = ingredients[j]
            if ingredients[j] in list_legume_fruit:
                if ingredients[j] not in tab_saison_mois:
                    string_saison = '';ing_pas_de_saison += ingredients[j]+','
                    str_pas_de_saison = 'Recette pas de saison : '

        recette["saison"] = string_saison + str_pas_de_saison + ing_pas_de_saison.rstrip(',')

        if k==nb_ing:
            output[key] = recette
        elif k==(nb_ing-1):
            # recette["ingredient_manquant"] = ing_manquant
            output_1_ing[key] = recette

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    #   This script is meant to verify the input_recettes file, verify 
    #   if the ingredient are correctly spelled. The output is ingredient_verif
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    dico_ing = {};tab_ingredient = []

    for key in recettes['recipes'].keys():
        for ingredient in recettes['recipes'][key]["ingredients"]:
            dico_ing[ingredient] = {"title": str(ingredient)} # added to factorize home_made method

    for key in dico_ing.keys():
        tab_ingredient.append(key)

    list_ing = sorted(tab_ingredient)
    ingredient_verif = open(os.path.join(PATH_FILES, "ingredient_verif.txt") ,'w',encoding ='utf-8')

    #Ecriture de la liste de tous les ingrédients et création d'un dico ayant les ingrédients en clé
    betterave = {}
    ALL_RECIPES = recettes['recipes']

    for ing in list_ing:
        bett = {}
        ingredient_verif.write(ing+'\n')
        for key in ALL_RECIPES.keys():
            if ing in ALL_RECIPES[key]['ingredients']:
                bett[key] = ALL_RECIPES[key]
        betterave[ing] = bett

    # .................................................
    # Fermeture du programme
    # .................................................

    csv_file.close()
    ingredient_verif.close()
    return (output, output_1_ing, ALL_RECIPES, betterave, dico_ing)

recipes = get_recipes()

'''
# architecture du dictionnaire recipes
# 0: recette du frigo
# 1: recette 1 ing en +
# 2: toutes les recettes {'1' : {'key':'1', 'title' : 'Salade ....'}}
# 3: dico qui liste tous les ingredients et leurs recette
# 4: idem 3 mais sans les recettes

'''