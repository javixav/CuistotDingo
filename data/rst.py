RST_FR = '''

\ 

\ 


Petit mémo pour écrire du Rst
=======================

Voici un bref résumé pour aider à la rédaction de document RST

\ 

============= ========================
**Résultat**	   **RSt code no**
============= ========================
` backtick``     échapper RST
\                backslash escape blank line
*italique*        `*italique*`
**gras**         `**gras**`
couleur_            `couleur_`
`mot a b`_       ` `mot a b`_`
1. Enum1          `1. Enumeration`
============= ========================

\ 

**Echappement**
\ 

Pour sauter une ligne entre du code rst, il faudrait::
 - sauter une ligne
 - écrire l'antislash suivie d'un espace
 - sauter une ligne

----


**Rétro-apostrophe**

Voilà un ``Rétro-apostrophe``                ````Rétro-apostrophe````

----

**Annotation**

:Salut: Cette annotation est très utile pour aligner la ligne suivante
        avec la ligne précédente, utlile pour les courtes descriptions
`:Salut: Cette annotation est une courte description`

----

**Section**

Titre suivi par les 4 de ces
caractères recommandés : `= - ` : . ' " ~ ^ _ * + #`_
alors la police sera automatiquement réduite


Section Titre1
---------------

Section Titre2
===============


En code RSt sans les retours à la ligne entre les deux :

`Section Titre1` 

`---------------`

`Section Titre2` 

`===============`


----


**Separateur**

Ceci est un séparateur composé de 4 caractères répétés comme ---- et séparé en haut comme en bas de retours à la ligne

----


**Paragraphe**

Juste le signe moins suivi par un espace pour aligner le texte suivant, peut avoir différentes indentations em fonction de l'espacement avant

- Ceci est le début d'un paragraphe dont le texte sera aligné même les lignes blanches

 - Ceci est un sous paragraphe.bLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLA

   - Un sous sou paragraph. bLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLA

- Paragraphe numéro 2. bLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLA

----

Ceci est un message d'alerte en couleur rouge

.. WARNING:: Rique d'avalanche.

`.. WARNING:: Rique d'avalanche.`

----

**Bloc de texte indenté**::
 
 écrire :: puis saut à la ligne
 Puis 1 espace à gauche
 on peut mettre un espace avant les deux :: si on veut pas de :

`**Bloc de texte indenté**::`

----

**Tableau**

+--------+-------+
|  A     |   B   |
+--------+-------+
|  1     |   2   |
+--------+-------+

`+--------+-------+`

`|  A     |   B   |`

`+--------+-------+`

`|  1     |   2   |`

`+--------+-------+`

autre exemple :

=============== ====
**ingrédients**  **poids**
=============== ====
aubergines       300g
carrottes        200g
oignon		 150g rapé
\		 200g brunoise
=============== ====

en code RST (enlever les backtick et les blank line)

`=============== ====`

`**ingrédients**  **poids**`

`=============== ====`

aubergines       300g

carrottes        200g

oignon		 150g rapé

`\		 200g brunoise`

`=============== ====`


----


'''

RST_EN = '''

\ 

\ 


Quick Help to write Rst
=======================

Here you'll find some tips to write Rst Documents

\ 

============= ========================
**Result**	   **RSt code no**
============= ========================
` backtick``     escape RST
\                backslash escape blank line
*italique*        `*italique*`
**bold**         `**bold**`
color_            `color_`
`word a b`_       ` `word a b`_`
1. Enum1          `1. Enumeration`
============= ========================

\ 

**Escape**
\ 

To skip a line between rst code, you need to::
 - skip a line
 - write the character backslash follow by a whitespace
 - skip a line

----


**Backquotes**

This is a ``Backquotes``                ````Backquotes````

----

**Field**

:Hello: This field has a short field name so aligning the field
        body with the first line is feasible.

`:Hello: This field has a short field name`

----

**Section**

Title followed by 4 of this
recommended characters : `= - ` : . ' " ~ ^ _ * + #`_
then it automatically reduce the police


Section Title1
---------------

Section Title2
===============


In RSt code without blank lines :

`Section Title1` 

`---------------`

`Section Title2` 

`===============`


----


**Separator**

This is a separator must be 4 repeated carac like ---- and separated up and down by blank lines    

----


**Paragraph**

Just minus  followed by a space for main and for nested space minus space

- This is the beginnig of paragraph the text will be alined to paragraph even blank lines


 - This is a sublist.bLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLA

   - This is a sub-sublist.bLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLA

- Second item bLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLAbLABLA

----

This is a warning message filled with red color

.. WARNING:: Don't play with fire.

`.. WARNING:: Don't play with fire.`

----

**Indented litteral block**::
 
 Needs :: then blank line
 Then White space at the left
 you can put a space before :: if you want no :

`**Indented litteral block**::`

----

**Tables**

+--------+-------+
|  A     |   B   |
+--------+-------+
|  1     |   2   |
+--------+-------+

`+--------+-------+`

`|  A     |   B   |`

`+--------+-------+`

`|  1     |   2   |`

`+--------+-------+`

another example :

=============== ====
**ingredients**  **weight**
=============== ====
eggplant         300g
carrot           200g
onion		 150g grated
\		 200g brunoise
=============== ====

in RST code (delete backtick and blank lines)

`=============== ====`

`**ingredients**  **weight**`

`=============== ====`

eggplant       300g

carrot        200g

onion		 150g grated

`\		 200g brunoise`

`=============== ====`


----


'''