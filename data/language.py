from data.rst import RST_FR, RST_EN

HELP_FR = '''
[b]_____________________________________________[/b]

Quelques infos sur l'application : c'est une application basique qui se veut minimaliste.\n
Dans le menu config, les champs input text doivent être validés par entrée.\n
Dans le menu Learn, ou Notes, tu pourras insérer du texte RST.\n
Pour le modifier il te suffira de double cliquer dessus.\n
Pour quitter le mode capture de photo, il suffit de double cliquer sur l'image.\n
Les recettes filtrées par ingrédients sont filtrées par rapport à la base de données complète.\n
Les données ont été reccueillie au fil des années, au fil des expériences culinaires, 
il se peut qu'il y ait des coquilles, que tu pourras modifier.
[b]_____________________________________________[/b]

Date: [b]janvier 2026[/b]
Developper: [b]Xavier Cattelain Lopez[/b]
Github: [b]javixav[/b]
Discord: [b]rabi lopez[/b]
Version: [b]24.0.0[/b]

'''

HELP_EN = '''
[b]_____________________________________________[/b]

Some information about the application: it's a basic, minimalist application.\n
In the settings menu, the input text fields must be validated by pressing Enter.\n 
In the Notes menu, you can insert restructured text. To edit it, simply double-click on it.\n
To exit capture picture, simply double-click on the screen.\n
Recipes filtered by ingredients are filtered within the complete database.\n
The original recipes dataset has been collected over the years, through culinary 
experiences, there may be some errors, which you can correct.
[b]_____________________________________________[/b]

Date: [b]january 2026[/b]
Developer: [b]Xavier Cattelain Lopez[/b]
Github: [b]javixav[/b]
Discord: [b]rabi lopez[/b]
Version: [b]24.0.0[/b]

'''



lang_fr = {"all_titles" : {"screen A": ["Recettes dispo","Avec 1 ingredient en +","Toutes les recettes","Par ingredient","Ajouter recette"],
              "screen B" : ["Mon stock", "Ajouter en swipant"],
              "screen C" : ["Mes notes"],
              "screen D" : ["Paramètres généraux", "Style et couleur","Position et taille", "Backup"]},
            "searchfield_hint_text" : ["Trouve ta recette", "Trouve ta note"],
            "navigation_titles" : ["Recettes", "Stock", "Notes", "Réglages"],
            "tooltip_text_appbar": ["Rechercher une recette", "Menu", "Réinitialiser","Rechercher notes", "Supprimer notes"],
            "rv_texfield": "rechercher ingrédient",
            "markup": ["Mes ", "recettes", " avec l'ingrédient", "Mon ", "stock", " d'ingrédients"],
            "a0":["Ingrédiens","Instructions","Astuces","Commentaires","Nombre de personnes","Saison","Source"],
            "config":["Hauteur proportionnelle appbar","Hauteur proportionnelle navigation", 
                      "Taille de la police navigation","Hauteur barre de tabulation",
                      "Marge intérieure des séparateurs","Style de police menu 3 points ",
                      "Style de police des Tiles","Position y icône édition des notes",
                      "Position x de l'icône déselectionner note","Position y de l'icône déselectionner note",
                      "Couleur de remplissage des notes inactives", "Restorer couleur de remplissage des notes inactives", 
                      "Couleur de remplissage des notes actives", "Restaurer couleur de remplissage des notes actives",
                      "Couleur arrière plan", "Langue", "Convertisseur", "Calendrier fruits et légumes", 
                      "Créer une sauvegarde des recettes", "Créer une sauvegarde des notes", 
                      "Créer une sauvegarde des ingrédients du frigo", "Remplacer fichier recettes","Remplacer fichier notes",
                      "Remplacer fichier ingrédients du frigo", "Remplacer tableur saison", "Section aide", "Section test",
                      "restaurer couleur", "calcul", "saison", "sauver recettes", "sauver notes","sauver ingrédients", "charger recettes", "charger notes",
                      "charger ingrédients", "charger saison", "aide", "test", 
                      "pour valider appuyer sur entrée","Taille des boutons ingrédients",
                      "Position y du champs recherche recette"],
            "speedbox": ["Zone de texte","Titre","Photo","Séparateur","Texte structuré"],
            "a5": ["Titre","Écrire le titre de la recette ici","Ingrédients","Ajouter ingrédient manquant ici :",
                    "Instructions", "Description de la recette ici","Astuces","Astuces pour réussir la recette",
                    "Commentaires","Commentaires sur la recette","Source","Source de la recette",
                    "Nombre de personnes","Recette pour ... personnes","Type de plat",
                    "entrée ou plat ou dessert ou condiment","sauvegarder",
                    "Une fois l'ingrédient écrit, cliquer sur le bouton plus à droite"],
            "dialog": ["Écris le titre du label", "Titre du label",
                        "Es-tu sûr de vouloir remplacer ta base de données de recettes ?",
                        "Es-tu sûr de vouloir remplacer ta base de données de notes ?",
                        "Es-tu sûr de vouloir remplacer ton stock d'ingrédients ?",
                        "Es-tu sûr de vouloir remplacer ta base de données de saison ?", 
                        "Ok", "Annuler",
                        "Les seules options possibles sont :",
                        "Ajouter un titre ci-dessous",
                        "Ce titre existe déjà !"],
            "toast": ["Il y a déjà une recette qui porte ce nom", 
                        "Certains champs obligatoires manquants",
                        "Il manque les ingrédients", 
                        "recette sauvegardée !",
                        "La camera a rencontré un problème, réessayer plus tard", 
                        "Erreur lors de la connexion à la caméra, essayer plus tard",
                        "Pas de capteurs disponibles, orientation portait par défaut",
                        "Ce n'est pas un fichier recette valide", 
                        "Ce fichier n'a pas l'architecture du fichier season.csv",
                        "Ce n'est pas un fichier note valide", 
                        "Ce n'est pas un fichier ingrédient valide",
                        "Échec de la suppression du fichier avec java",
                        "Le fichier a bien été supprimé avec python",
                        "Échec de la suppression du fichier avec java et python...",
                        "Couleur de remplissage par défault des notes inactives restaurée",
                        "Couleur de remplissage par défault des notes actives restaurée",
                        "Texte copié !" ],
            "help": ["Section aide", HELP_FR],
            "notes": ["Écrire ici"],
            "rst_help_text": RST_FR,
        }

lang_en = {"all_titles" : {"screen A": ["Recipes available","Adding just one ingredient","All the recipes","By ingredient","Add recipe"],
              "screen B" : ["My stock", "Add by swiping"],
              "screen C" : ["My notes"],
              "screen D" : ["General settings", "Style and color","Position and size", "Backup"]},
            "searchfield_hint_text" : ["Find your recipe", "Find your note"],
            "navigation_titles" : ["Recipes", "Stock", "Notes", "Settings"],
            "tooltip_text_appbar": ["Find a recipe", "Menu", "Reset","Find a note", "Delete notes"],
            "rv_texfield": "find ingredient",
            "markup": ["My ", "recipes", " with the ingredient", "My ", "ingredients", " stock"],
            "a0":["Ingredients","Instructions","Tips","Comments","Serves","Season","Source"],
            "config": ["Size hint appbar","Size hint y navigation","Font size navigation bar",
                       "Tabs bar all recipes height","Separator padding y","Font style menu 3 dots", 
                       "Tiles Font style", "Y position for item icon note edition", 
                       "X position for unselect notes cross", "Y position for unselect notes cross",
                       "Color for inactive Note background","Default color for inactive Note background",
                       "Color for active Note background", "Default color for active Note background",
                       "Default color for theme layout","Language","Calculation","Season calendar",
                       "Create backup for recipes input","Create backup for notes data input",
                       "Create backup for ingredient data input","Load recipes data","Load notes data",
                       "Load ingredient data","Load season data", "Help section", "Test section",
                       "restore color", "converter", "season","backup recipes","backup notes","backup fridge",
                       "load recipes","load notes","load ingredients","laod season","help","test", 
                       "press enter to validate", "Ingredient button font size",
                       "Y position for search text input"],

            "speedbox": ["Text area","Title","Picture","Separator","Structured text"],
            "a5": ["Title","Write the recipe title here","Ingredients","Add ingredient missing here :",
                    "Instructions", "Recipe's description here","Tips","Tips to succeed",
                    "Comments","Recipes comments","Source","Recipe's source",
                    "Servings","Recipe for ... people","Type of food",
                    "Starter or main course or dessert or condiment","save",
                    "Once the ingredient is written, press the + icon on the right"],
            "dialog": ["Write the label title", "Label title",
                        "Are you sure you want to replace your recipe database ?",
                        "Are you sure you want to replace your notes database ?",
                        "Are you sure you want to replace your ingredients stock database ?",
                        "Are you sure you want to replace your season file database ?", 
                        "Ok", "Cancel",
                        "Only available options are :",
                        "Add a title here",
                        "This title already exists !"],
            "toast": ["There is already a recipe sharing this title", "Some required fields missing",
                        "Ingredients required", "Recipe saved !",
                        "There was an issue with the camera, try later", "Error while connecting to camera, try later",
                        "No sensors availaible, default is portrait",
                        "This is not a valid recipe file", "This file has not the season.csv file architecture",
                        "This file is not a note file", "This is not a valid ingredients file",
                        "Fail to delete with java",
                        "Success to delete with python",
                        "Fail to delete with java and python...",
                        "Default Color for inactive Note background restored",
                        "Default Color for active Note background restored",
                        "Copied text !" ],
            "help": ["Help Section", HELP_EN],
            "notes": ["Write here"],
            "rst_help_text": RST_EN,
        }
