#kivy 2.3.1
#kivymd 1.2.0
# Tested on Android Api 29
# Buildozer Api to use 33

# requirements=python3, kivy==2.3.1, kivymd==1.2.0, pillow, materialyoucolor, asynckivy, filetype, docutils, camera4kivy, androidstorage4kivy, gestures4kivy, unidecode

'''##################################################################################
                                Import Modules
##################################################################################'''

#internal and core modules
from android_permissions import AndroidPermissions
from config import config_input
from core.InMyFridge import recipes, get_recipes
from core.input_frigo import mydico_frigo
from core.input_recettes import recettes
from data.note_data import note_data, note_index
from functions.utils import save_config, ingredient_max_calcul, log, log_warning
from data.language import lang_en, lang_fr
from data.codes  import CODE_INGREDIENTS, CODE_RECIPES, CODE_NOTES
from functions.foreground import hex_to_rgba, rgba_to_hex
from functions.matchers import home_made, DiffSequenceMatcher
import docutils

#kivy library
from kivy.utils import platform
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color
from kivy.graphics.transformation import Matrix
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, \
                            StringProperty,BooleanProperty, \
                            ColorProperty,ListProperty, \
                            DictProperty
from kivy.resources import resource_add_path
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.rst import RstDocument
from kivy.uix.scatter import ScatterPlane
from kivy.weakproxy import WeakProxy

# kivymd library
from kivymd.app import MDApp
from kivymd.font_definitions import theme_font_styles
from kivymd.toast import toast
from kivymd.uix.behaviors import TouchBehavior, CommonElevationBehavior, RotateBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton,MDRaisedButton,MDRectangleFlatIconButton,MDFillRoundFlatButton,MDRectangleFlatButton
from kivymd.uix.button.button import (MDFlatButton,
                                      MDFloatingActionButton)
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.imagelist import MDSmartTile
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.segmentedcontrol.segmentedcontrol import MDSegmentedControl
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

#exteral libraries
if platform == "android":
    from android.storage import app_storage_path, primary_external_storage_path  # app_storage_path : /data/user/0/org.test.appname/files/
    from android import mActivity, api_version, autoclass, cast
    from androidstorage4kivy import SharedStorage, Chooser
    from camera4kivy.preview_camerax import PreviewCameraX
if platform in ["win","macos","linux","unknown"]:
    from camera4kivy.preview_kivycamera import PreviewKivyCamera as CameraPreview
from camera4kivy import Preview
from datetime import datetime
from difflib import SequenceMatcher
from functools import partial
from importlib import reload
from json import loads as json_loads , dumps as json_dumps, JSONDecodeError as json_JSONDecodeError
from math import log as logar
from os import replace, mkdir, remove, makedirs
from os.path import join, basename, exists, isfile, dirname, abspath
from PIL import Image
from shutil import copyfile
from traceback import format_exc as traceback_format_exc
from unidecode import unidecode

'''##################################################################################
                                Set Variables and functions
##################################################################################'''

if platform == "android":
    
    BiblioJava4Android = autoclass("org.kivy.library.BiblioJava4Android")
    DeviceOrientation = autoclass("org.kivy.orientation.DeviceOrientation")
    Environment = autoclass('android.os.Environment')
    MediaStoreMediaColumns = autoclass('android.provider.MediaStore$MediaColumns')
    MediaStoreFiles = autoclass('android.provider.MediaStore$Files')

    appname = SharedStorage().get_app_title()
    context = mActivity.getApplicationContext()
    library = BiblioJava4Android()
    ROOT_FOLDER = Environment.getExternalStorageDirectory().getAbsolutePath() # /storage/emulated/0
    DIR_APP_PRIVATE = join(app_storage_path(), "app")
    DIR_RECIPES_PRIVATE = join(app_storage_path(), "app", "images","recipes")
    DIR_NOTES_PRIVATE = join(app_storage_path(), "app", "images","notes")

Window.softinput_mode = "below_target"  # specifies the soft keyboard presence, here invisible
max_ingredient = ingredient_max_calcul(config_input, recipes)
source_image_default = join("images","CuistotDingo.png")
basename_image_default = "CuistotDingo.png"

'''##################################################################################
                                Class Root
##################################################################################'''

class RootLayout(MDBoxLayout):
    pass

'''##################################################################################
                                Classes TopAppBar
##################################################################################'''

class MyMDTopAppBar(MDTopAppBar): # see if kv post can be factorized
    current_nav_screen = "screen A"
    last_nav_screen = "screen A"
    titles = ListProperty()
    app = ObjectProperty()
    unselect_note_icon_x = NumericProperty()
    unselect_note_icon_y = NumericProperty()
    search_textfield_y = NumericProperty()
    unselect_note_icon = ObjectProperty()

    def on_kv_post(self,w):
        self.app = MDApp.get_running_app()
        self.titles = self.app.current_lang["all_titles"][self.current_nav_screen]
        self.title = self.titles[0]
        self.create_appbar()
        Clock.schedule_once(self.place_appbar_widget, 0)

    def create_appbar(self):
        self.menu_items = [
                {     
                    "viewclass": "ItemMenu", #can be Item
                    "height": dp(42), #dp(54)
                    "on_release": lambda x=i: self.item_menu(x),
                    "index": i,
                } for i in range(len(self.titles))
        ]

        for i in range(len(self.titles)):
            self.menu_items[i]["text"] = f"[b]{self.titles[i]}[/b]" # can also change [size=16]

        self.menu = MDDropdownMenu(
                items= self.menu_items,
                width= dp(150), 
                md_bg_color=self.theme_cls.primary_light,
                )
        self.last_nav_screen = self.current_nav_screen

    def place_appbar_widget(self, dt):
        ''' 
        This code was added to make the positon of the cross unselect note button 
        be related to the position of the current appbar title. 
        Scheduled because the position of label_title is set after kv post.
        '''
        wigets_in_appbar = CuistotDingoApp.get_widgets(self, 'MDBoxLayout')
        box = wigets_in_appbar[3]

        # place icon search_textfield and unselect note icon
        if platform in ["android","ios"]:
            
            if config_input["searchfield_icon_changed_android"] == "false": # if user has not changed yet manually the y position : 
                self.search_textfield_y = self.ids.label_title.pos[1]
            else:
                self.search_textfield_y = config_input["search_textfield_y_android"]

            if config_input["unselect_note_icon_changed_android"] == "false":
                self.unselect_note_icon_x = self.ids.label_title.padding[0] + 25                
                self.unselect_note_icon_y = self.ids.label_title.center_y - 12 # we need to change here because of screen differences, why we don't know exactly
            else:
                self.unselect_note_icon_x = config_input["unselect_note_icon_x_android"]
                self.unselect_note_icon_y = config_input["unselect_note_icon_y_android"]       
        else:
            self.unselect_note_icon_x = self.ids.label_title.padding[0] + 25
            self.search_textfield_y = self.ids.label_title.pos[1]
            self.unselect_note_icon_y = self.ids.label_title.pos[1] - 2

        self.unselect_note_icon = UnselectNoteIcon(
                                    icon = "close",
                                    opacity= 0,
                                    disabled = True,
                                    pos = (self.unselect_note_icon_x, self.unselect_note_icon_y), # This code is not reponsive compliant : todo try another solution than pos y for 
                                )
        
        self.search_textfield = SearchField(
                                    size_hint = (None,None),
                                    width = Window.width/2,
                                    pos = (0.05*Window.width , self.search_textfield_y),
                                    opacity = 0,
                                    disabled = True,
                                )
        
        self.close_textfield_icon = CloseIconButton(
        icon = "close",
        opacity= 0,
        disabled = True,
        )
        
        self.close_textfield_icon.pos = [0.05*Window.width + self.search_textfield.width - self.close_textfield_icon.padding[3] - self.search_textfield.padding[3] , self.search_textfield_y]
        self.close_textfield_icon.bind(on_release = self.close_textfield)
    
        floatlayout = MDFloatLayout(size_hint = (1,None), pos_hint = {"center_x":.5, "center_y":.5})
        floatlayout.add_widget(self.unselect_note_icon)
        floatlayout.add_widget(self.search_textfield)
        floatlayout.add_widget(self.close_textfield_icon)
        if len(wigets_in_appbar) < 7:
            box.add_widget(floatlayout,1)

    def register_appbar_widgets_position(self):
        ''' 
        Register the positon of the cross unselect note button, 
        search_textfield and close_textfield_icon widgets to screen config. 
        Only in Android, no need to code the windows version
        '''
        if platform in ["android","ios"]:
            if config_input["unselect_note_icon_changed_android"] == "false": # if user has not changed yet manually the y position : 

                self.app.manager.screenD3.ids._unselect_note_cross_x.ids._configbox_field.text = str(round(float(self.unselect_note_icon_x), 0))
                self.app.manager.screenD3.ids._unselect_note_cross_y.ids._configbox_field.text = str(round(float(self.unselect_note_icon_y), 0))
                self.app.manager.screenD3.ids._search_textfield_y.ids._configbox_field.text = str(round(float(self.search_textfield_y), 0))
                config_input["unselect_note_icon_x_android"] = self.unselect_note_icon_x
                config_input["unselect_note_icon_y_android"] = self.unselect_note_icon_y
                config_input["search_textfield_y_android"] = self.search_textfield_y
                save_config(config_input)

    def menu_appbar(self, button):
        ''' called every time three dots right action button is pressed. '''
        # 1. restore default screen transition for screen calcul and E1 where transition was changed : 
        if self.current_nav_screen == "screen D":
            self.app.restore_screen_transition()

        if self.current_nav_screen == "screen C":
            self.search()
        else:
            self.menu.caller = button
            self.menu.open()
            
            # create the invisible tiles for the A4 screen, why here, to optimise time response
            self.app.optimize_loading_A4_screen(5)

    def set_right_actions_appbar(self, index, opacity, disabled, icon = "", tooltip_text = ""):
        self.ids.right_actions.children[index].opacity = opacity
        self.ids.right_actions.children[index].disabled = disabled
        self.ids.right_actions.children[index].icon = icon
        self.ids.right_actions.children[index].tooltip_text = tooltip_text

    def item_menu(self, index):
        ''' Methods that deals the redirection items menu screen A1 to A5
        We deal the screen A5 recipe search icon. '''

        self.title = self.titles[index]
        self.app.manager.index = index
        screen_name = self.current_nav_screen + str(index+1)
        
        if screen_name in ["screen A1", "screen A2", "screen A3", "screen A4"]:
            # icon "menu" icon is cool too
            tooltip = self.app.current_lang["tooltip_text_appbar"][0]
            self.set_right_actions_appbar(1, 1, False, icon = "magnify", tooltip_text = tooltip)

            if not self.app.manager.screen_a4_loaded:
                self.app.manager.load_A4_screen()

        elif screen_name == "screen A5":

            tooltip = self.app.current_lang["tooltip_text_appbar"][3]
            self.set_right_actions_appbar(1, 1, False, icon = "trash-can", tooltip_text = tooltip)

            if not self.app.manager.screen_a5_loaded: 
                self.app.manager.load_A5_screen()

            self.app.manager.screenA5.reset_recipe_items()
            self.close_textfield(self.close_textfield_icon)

        elif screen_name in ["screen D1", "screen D2", "screen D3", "screen D4"]:
            match screen_name:
                case "screen D1":
                    if not self.app.manager.screen_d1_loaded:
                        self.app.manager.load_D1_screen()
                case "screen D2":
                    if not self.app.manager.screen_d2_loaded:
                        self.app.manager.load_D2_screen()
                case "screen D3":
                    if not self.app.manager.screen_d3_loaded:
                        self.app.manager.load_D3_screen()
                case "screen D4":
                    if not self.app.manager.screen_d4_loaded:
                        self.app.manager.load_D4_screen()

        else:
            self.set_right_actions_appbar(1, 0, True, icon = "magnify")

        self.app.manager.current = screen_name
        
        # screen redirection
        if screen_name == "screen A5": # for screen direction purpose when user modify or create new recipe
            self.app.A5_edition = False
        self.menu.dismiss()

        # create the invisible tiles for the A4 screen, why here, to optimise time response
        # because A5 is dynamically open and takes time, we optimize only on other screens
        if screen_name != "screen A5":
            self.app.optimize_loading_A4_screen(10)

    def close_textfield(self, button):
        # launched when closing search textfield
        self.close_textfield_icon.opacity = 0
        self.close_textfield_icon.disabled = True
        self.search_textfield.opacity = 0
        self.search_textfield.text = ""
        self.search_textfield.disabled = True
        self.ids.label_title.opacity = 1
        if self.app.manager.screen_c1_loaded:
            self.app.manager.screenC1.ids["_selection_list"].filtering = False

    def change_appbar_from_nav(self, screen_nav):
        # called when clicking on the navigation buttons
        
        if self.last_nav_screen != screen_nav:
            self.titles = self.app.current_lang["all_titles"][screen_nav]
            self.title = self.titles[0]
            self.current_nav_screen = screen_nav
            self.create_appbar()

            # we close the searchfield in case it was open
            self.close_textfield(self.close_textfield_icon)
            
            if screen_nav == "screen B":
                # all buttons are disabled

                self.set_right_actions_appbar(0, 0, True) 
                self.set_right_actions_appbar(1, 0, True) 

            elif screen_nav == "screen C":
                # here to have a smooth screen change we replace magnify for the three dots button
                self.reset_appbar_notes_unselected()
                
            elif screen_nav == "screen D":
                match self.app.manager.current:
                    case "screen D1":
                        self.title = self.titles[0]
                    case "screen D2":
                        self.title = self.titles[1]
                    case "screen D3":
                        self.title = self.titles[2]
                    case "screen D4":
                        self.title = self.titles[3]

                self.set_right_actions_appbar(0, 1, False, icon = "dots-vertical")
                self.set_right_actions_appbar(1, 0, True)

            else: # screen A
                
                if self.app.manager.current in ["screen A1", "screen A2", "screen A3", "screen A4"]:
                    # icon "menu" icon is cool too
                    tooltip = self.app.current_lang["tooltip_text_appbar"][0]
                    self.set_right_actions_appbar(1, 1, False, icon = "magnify", tooltip_text= tooltip)

                elif self.app.manager.current == "screen A5":
                    tooltip = self.app.current_lang["tooltip_text_appbar"][3]
                    self.set_right_actions_appbar(1, 1, False, icon = "trash-can", tooltip_text= tooltip)
                    
                match self.app.manager.current:
                    case "screen A1":
                        self.title = self.titles[0]
                    case "screen A2":
                        self.title = self.titles[1]
                    case "screen A3":
                        self.title = self.titles[2]
                    case "screen A4":
                        self.title = self.titles[3]
                    case "screen A5":
                        self.title = self.titles[4]

                self.search_textfield.hint_text = self.app.current_lang["searchfield_hint_text"][0]

                tooltip = self.app.current_lang["tooltip_text_appbar"][1]
                self.set_right_actions_appbar(0, 1, False, icon = "dots-vertical", tooltip_text= tooltip)

    def search(self):
        ''' Function called when magnify or trash icon button is pressed, the icon changes related to 
        the current screen, that 's why we need to separate logics here. '''

        if self.app.manager.current == "screen A5": 
            # button search is used here as button reset items...
            self.app.manager.screenA5.reset_recipe_items()
            
        elif self.app.manager.current == "screen C1" and Note.selected_notes > 0:
            # button search is used here as button delete notes selected
            self.app.manager.screenC1.ids._selection_list.delete_notes_selection()

        else:
            self.ids.label_title.opacity=0

            self.search_textfield.opacity=1
            self.search_textfield.disabled= False

            self.close_textfield_icon.opacity= 1
            self.close_textfield_icon.disabled= False

            if self.app.manager.screen_c1_loaded:
                self.app.manager.screenC1.ids["_selection_list"].filtering = True
            
            Clock.schedule_once(self.focus_field, 0.3) # adding focus with clock

    def focus_field(self, dt): # here value is expected by self.focus_field 
        ''' focus the search texfield when clicking on it '''
        self.search_textfield.focus = True 

    def reset_appbar_notes_unselected(self):
        ''' reset the appbar icons after unselecting notes. '''
        # Note.selected_notes = 0
        self.title = self.app.current_lang["all_titles"]["screen C"][0]
        self.search_textfield.hint_text = self.app.current_lang["searchfield_hint_text"][1]

        self.set_right_actions_appbar(1, 0, True)
        tooltip = self.app.current_lang["tooltip_text_appbar"][3]
        self.set_right_actions_appbar(0, 1, False, icon = "magnify", tooltip_text= tooltip)

        self.unselect_note_icon.opacity = 0
        self.unselect_note_icon.disabled = True

    @mainthread
    def restore_appbar_after_language(self, dt):
        ''' $bug : this is a bug apparently induce to the use of DictProperty current_lang
        it changes the opacity and enable/disable the right actions buttons ... why we don't know
        very strange behavior but because we are two lazt to debug, we just add a "fix"
        we change it manually so we keep the DictProperty. '''

        if self.app.manager.current == "screen D1":
            self.set_right_actions_appbar(1, 0, True)

    def reset_appbar_notes_selected(self): 
        ''' set the appbar icons when notes are selected. '''

        self.set_right_actions_appbar(1, 0, True)

        tooltip = self.app.current_lang["tooltip_text_appbar"][4]
        self.set_right_actions_appbar(0, 1, False, icon = "trash-can", tooltip_text = tooltip)

        self.unselect_note_icon.opacity = 1
        self.unselect_note_icon.disabled = False

    def validate_unselect_icon_y(self,text):
        ''' triggered when user enters manually the unselect note icon y position in config screen '''
        
        self.unselect_note_icon_y = float(text)
        self.unselect_note_icon.y = float(text)
        config_input["unselect_note_icon_changed_android"] = "true"

        if platform in ["android","ios"]:
            config_input["unselect_note_icon_y_android"] = float(text)
        else:
            config_input["unselect_note_icon_y_win"] = float(text)
        
        save_config(config_input)

    def validate_search_textfield_y(self,text):
        ''' triggered when user enters manually the search field y position in config screen '''

        self.search_textfield_y = float(text)
        self.search_textfield.y = float(text)
        self.close_textfield_icon.y = float(text)
        config_input["searchfield_icon_changed_android"] = "true"

        if platform in ["android","ios"]:
            config_input["search_textfield_y_android"] = float(text)
        else:
            config_input["search_textfield_y_win"] = float(text)
        
        save_config(config_input)

    def validate_unselect_icon_x(self,text):
        ''' triggered when user enters manually the unselect note icon x position in config screen '''

        config_input["unselect_note_icon_changed_android"] = "true"
        
        self.unselect_note_icon_x = float(text)
        self.unselect_note_icon.x = float(text)

        if platform in ["android","ios"]:
            config_input["unselect_note_icon_x_android"] = float(text)
        else:
            config_input["unselect_note_icon_x_win"] = float(text)
        
        save_config(config_input)

class ItemMenu(MDLabel): 
    ''' Class to personalize the MenuItems could subclass with MDLabel
    and OneLineListItem, the on_release callback would
    be automatic but problems in the text repeated twice. '''

    appbar = ObjectProperty()

    def label_click(self, w,touch):
        if w.collide_point(*touch.pos):
            self.appbar.menu.items[self.index]["on_release"]() # we call the on_release in an obscure maneer          
            
'''##################################################################################
                                Classes NavigationBottom
##################################################################################'''

class NavigationGrid(MDGridLayout):
    last_button = StringProperty("bowl-mix")

    def change_color_navigation(self, icon_name):
        app = MDApp.get_running_app()
        #1 change color of the last button selected
        if self.last_button != icon_name:
            id = "_" + self.last_button
            app.navigation.ids[id].children[0].text_color = self.children[0].icon_color_inactive
            app.navigation.ids[id].children[1].text_color = self.children[0].text_color_inactive

            #2. change color of the button selected:
            id = "_" + icon_name
            app.navigation.ids[id].children[0].text_color = self.children[0].icon_color_active
            app.navigation.ids[id].children[1].text_color = self.children[0].text_color_active

            #3 keep reference to the last button selected
            self.last_button = icon_name

class NavigationRelativeLayout(RelativeLayout):
    icon = StringProperty()
    text = StringProperty()
    name = StringProperty()
    text_color = ListProperty()
    icon_color = ListProperty()
    icon_color_active = [1,1,1,1]
    icon_color_inactive = [0.3803921568627451, 0.3803921568627451, 0.3803921568627451, 1.0]
    text_color_active = [1,1,1,1]
    text_color_inactive = [0.3803921568627451, 0.3803921568627451, 0.3803921568627451, 1.0]

'''##################################################################################
                                Class Manager
##################################################################################'''

class MyMDScreenManager(MDScreenManager):
    app = ObjectProperty()
    screenA1 = ObjectProperty()
    screenA2 = ObjectProperty()
    screenA3 = ObjectProperty()
    screenA4 = ObjectProperty()
    screenA5 = ObjectProperty()
    screenB1 = ObjectProperty()
    screenC1 = ObjectProperty()
    screenD1 = ObjectProperty()
    screenD2 = ObjectProperty()
    screenD3 = ObjectProperty()
    screenD4 = ObjectProperty()
    screenE1 = ObjectProperty()

    screenEditNote = ObjectProperty()
    screenRstEdit = ObjectProperty()
    screenRstHelp = ObjectProperty()
    screenRstCode = ObjectProperty()

    screenPicture = ObjectProperty()
    screenFullPicture = ObjectProperty()

    index = NumericProperty()
    previous_tile = ObjectProperty()
    tile_mother_manager = ObjectProperty()
    
    previous_screen = StringProperty("screen A1")
    last_A_screen = StringProperty("screen A1")
    last_B_screen = StringProperty("screen B1")
    last_C_screen = StringProperty("screen C1")
    last_D_screen = StringProperty("screen D1")

    screen_a4_loaded = BooleanProperty(False)
    screen_a5_loaded = BooleanProperty(False)
    screen_b1_loaded = BooleanProperty(False)
    screen_c1_loaded = BooleanProperty(False)
    screen_d1_loaded = BooleanProperty(False)
    screen_d2_loaded = BooleanProperty(False)
    screen_d3_loaded = BooleanProperty(False)
    screen_d4_loaded = BooleanProperty(False)
    screen_e1_loaded = BooleanProperty(False)
    screen_calcul_loaded = BooleanProperty(False)
    screen_rst_edit_loaded = BooleanProperty(False)
    screen_rst_help_loaded = BooleanProperty(False)
    screen_rst_code_loaded = BooleanProperty(False)
    screen_full_picture_loaded = BooleanProperty(False)
    screen_season_loaded = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def set_tile_source(self, key):
        ''' set the source for the tile's image '''
        if exists(join("images", "recipes", key + ".jpg")) :
            source = join("images", "recipes", key + ".jpg") 
        else:
            source = source_image_default
        return source
    
    def change_screen_navigation(self, screen_name):
        ''' Triggered when pressing the navigation icons Bottom bar. 
        Here we need to change the index manager when coming from D4-D3-D2 etc, otherwise last screen is messed up. '''

        self.index = int(screen_name[-1])-1
        if self.current[-2:-1] != screen_name[-2:-1]:
            self.transition.direction = "left"
            if screen_name == "screen B1" and not self.screen_b1_loaded:
                self.load_B1_screen()
            if screen_name == "screen C1" and not self.screen_c1_loaded:
                self.load_C1_screen()
            if screen_name == "screen D1" and not self.screen_d1_loaded:
                self.load_D1_screen()

            self.current = screen_name
            self.app.appbar.change_appbar_from_nav(screen_name[:-1])

    def load_screens(self):
        # screen loaded at build time
        self.load_A1_screen()
        self.load_A2_screen()
        self.load_A3_screen()

    def load_A1_screen(self): 
        for key in recipes[0].keys():
            title1 = recipes[0][key]["title"]
            instruction1 = recipes[0][key]["description"]
            ingredients1 = recipes[0][key]["ingredients"]
            source_recette1 = recipes[0][key]["source"]
            astuces1 = recipes[0][key]["astuces"]
            commentaire1 = recipes[0][key]["commentaire"]
            nbpersonne1 = recipes[0][key]["nombre de personne"] if "nombre de personne" in recipes[0][key] else ""
            saison1 = recipes[0][key]["saison"] if "saison" in recipes[0][key] else ""
            source1 = self.set_tile_source(key)
            Tile1= MyMDSmartTile(text= title1, description = instruction1, 
                                ingredients = ingredients1, source_recette = source_recette1, astuces = astuces1,
                                commentaire = commentaire1, nb_personne = nbpersonne1, saison = saison1, index_picture = key, tile_screen = "screen A1",
                                source = source1)
            
            self.screenA1.ids._grid1.add_widget(Tile1)

    def load_A2_screen(self):
        for key in recipes[1].keys():
            title2 = recipes[1][key]["title"]
            instruction2 = recipes[1][key]["description"]
            ingredients2 = recipes[1][key]["ingredients"]
            source_recette2 = recipes[1][key]["source"]
            astuces2 = recipes[1][key]["astuces"]
            commentaire2 = recipes[1][key]["commentaire"]
            nbpersonne2 = recipes[1][key]["nombre de personne"] if "nombre de personne" in recipes[1][key] else ""
            saison2 = recipes[1][key]["saison"] if "saison" in recipes[1][key] else ""
            source2 = self.set_tile_source(key)
            
            Tile2=MyMDSmartTile(text= title2, description = instruction2, 
                                ingredients = ingredients2, source_recette = source_recette2, astuces = astuces2,
                                commentaire = commentaire2, nb_personne = nbpersonne2, saison = saison2, index_picture = key, tile_screen = "screen A2",
                                source = source2)
            
            self.screenA2.ids._grid2.add_widget(Tile2)

    def load_A3_screen(self):   
        # set UI design
        self.screenA3.ids._tabs.carousel.parent.size_hint_y = None
        self.screenA3.ids._tabs.carousel.parent.height = 0
        self.screenA3.ids._tabs.size_hint_y = None
        self.screenA3.ids._tabs.height = self.screenA3.ids._tabs.tab_bar_height
        # create tab bar or delete and create for the loading recipe purpose   
        self.screenA3.ids._tabs.create_tabs()

        nb_recipe = 10
        nb_range = self.app.nb_recipe_returned(nb_recipe) # in case nb recipes less than 10
        for i in range(nb_range):
            key = str(i+1)        
            instruction3 = recipes[2][key]["description"]
            ingredients3 = recipes[2][key]["ingredients"]
            source_recette3 = recipes[2][key]["source"]
            astuces3 = recipes[2][key]["astuces"]
            commentaire3 = recipes[2][key]["commentaire"]
            nb_personne3 = recipes[2][key]["nombre de personne"] if "nombre de personne" in recipes[2][key] else ""
            saison3 = recipes[2][key]["saison"] if "saison" in recipes[2][key] else ""
            title = recipes[2][key]["title"]
            source3 = self.set_tile_source(key)

            Tile3 = MyMDSmartTile(
                text= title, description = instruction3, 
                ingredients = ingredients3, source_recette = source_recette3, astuces = astuces3,
                commentaire = commentaire3, nb_personne = nb_personne3, saison = saison3, index_picture = key, tile_screen = "screen A3" ,
                source = source3)

            self.screenA3.ids._tabs.grid.add_widget(Tile3)

    def load_A4_screen(self):
        self.screen_a4_loaded = True
        self.screenA4 = Builder.load_file('screen_A4.kv')
        self.add_widget(self.screenA4)

    def load_A5_screen(self):
        self.screen_a5_loaded = True
        self.screenA5 = Builder.load_file('screen_A5.kv')
        self.add_widget(self.screenA5)
    
    def load_B1_screen(self):
        self.screen_b1_loaded = True
        self.screenB1 = Builder.load_file('screen_B1.kv')
        self.add_widget(self.screenB1)
    
    def load_C1_screen(self):
        self.screen_c1_loaded = True
        self.screenC1 = Builder.load_file('screen_C1.kv')
        self.add_widget(self.screenC1)
        self.app.appbar.unselect_note_icon.bind(on_release = self.screenC1.ids._selection_list.unselect_notes)
        self.screenC1.ids._selection_list.load_notes_from_data()

    def load_D1_screen(self):
        self.screen_d1_loaded = True
        self.screenD1 = Builder.load_file('screen_D1.kv')
        self.add_widget(self.screenD1)

        # changing the active segmented button, here Clock is needed otherwise, the rendering is not good
        Clock.schedule_once(partial(self.screenD1.ids._segmented_control_color.fake_active, "color"), 0)
        Clock.schedule_once(partial(self.screenD1.ids._segmented_control_lang.fake_active, "language"), 0)

    def load_D2_screen(self):
        self.screen_d2_loaded = True
        self.screenD2 = Builder.load_file('screen_D2.kv')
        self.add_widget(self.screenD2)

    def load_D3_screen(self):
        self.screen_d3_loaded = True
        self.screenD3 = Builder.load_file('screen_D3.kv')
        self.add_widget(self.screenD3)
        self.app.appbar.register_appbar_widgets_position() # added to make postion appbar widgets responsive

    def load_D4_screen(self):
        self.screen_d4_loaded = True
        self.screenD4 = Builder.load_file('screen_D4.kv')
        self.add_widget(self.screenD4)
    
    def load_E1_screen(self):
        self.screen_e1_loaded = True
        self.screenE1 = Builder.load_file('screen_E1.kv')
        self.add_widget(self.screenE1)

    def load_calcul_screen(self):
        self.screen_calcul_loaded = True
        screen_calcul = Builder.load_file('screen_calcul.kv')
        self.add_widget(screen_calcul)

    def load_rst_edit_screen(self):
        self.screen_rst_edit_loaded = True
        self.screenRstEdit = Builder.load_file('screen_rst_edit.kv')
        self.add_widget(self.screenRstEdit)

    def load_rst_help_screen(self):
        self.screen_rst_help_loaded = True
        self.screenRstHelp = Builder.load_file('screen_rst_help.kv')
        self.add_widget(self.screenRstHelp)

    def load_rst_code_screen(self):
        self.screen_rst_code_loaded = True
        self.screenRstCode = Builder.load_file('screen_rst_code.kv')
        self.add_widget(self.screenRstCode)

    def load_full_picture_screen(self):
        self.screen_full_picture_loaded = True
        self.screenFullPicture = Builder.load_file('screen_full_picture.kv')
        self.add_widget(self.screenFullPicture)

    def load_season_screen(self):
        self.screen_season_loaded = True
        screen_season = Builder.load_file('screen_season.kv')
        self.add_widget(screen_season)

    @mainthread
    def reload_recipes_screens(self, screens):
        ''' Screens here is a list of screen names to reload
        Launch when a ingredient is added or deleted from stack
        Firt we match the number of tiles with the new number of recipes
        Then we rewrite the new content. This reload is smart because it does not clear widget 
        which would be too long. '''
        
        def add_empty_tiles(grid, i, r):
            #1 Add empty tiles to grid
            for tile in range(r): # on kv post and init comes with instanciation of MyMDSmartTile
                grid.add_widget(MyMDSmartTile(text = "", description = "",
                                              ingredients = [], source_recette = "", astuces = "",
                                              commentaire = "", nb_personne = "", saison = "", index_picture = "", tile_screen = "screen A" + str(i+1),
                                              source = source_image_default))
        
        def remove_empty_tiles(grid, i, r):
            #1 Delete r number tiles in grid
            for tile in range(r):
                grid.remove_widget(grid.children[0]) # we don't care which tile we delete because we reload all of them

        def reload_tiles_content(grid,i):
            n=1
            # not the best because replace tiles that no need to be replaced
            for key in recipes[i].keys():
                instruction = recipes[i][key]["description"]
                title = recipes[i][key]["title"]
                ingredients = recipes[i][key]["ingredients"]
                commentaire = recipes[i][key]["commentaire"]
                astuces = recipes[i][key]["astuces"]
                nb_personne = recipes[i][key]["nombre de personne"] if "nombre de personne" in recipes[i][key] else ""
                saison = recipes[i][key]["saison"] if "saison" in recipes[i][key] else ""
                source_recette = recipes[i][key]["source"]

                self.app.replace_tile(grid.children[-n], key, instruction, title,
                                                     ingredients, commentaire, nb_personne, saison, astuces, source_recette)
                n+=1

        # Screen A0
        if "screen A0" in screens:
            # $bug potential only happened in Android.
            ''' Because of the weird overlapping of source and saison MDLabels, we could have reload them
            here, but for now the bug has not been seen for a long time so we leave it like this '''
            pass
        
        # Screen A1
        if "screen A1" in screens:
            old_size_A1 = len(self.screenA1.ids._grid1.children)
            new_size_A1 = len(recipes[0])

            #1. First add empty tiles to match the new correct grid size
            if new_size_A1 > old_size_A1 :
                add_empty_tiles(self.screenA1.ids._grid1, 0, new_size_A1-old_size_A1)
            elif new_size_A1 < old_size_A1:
                remove_empty_tiles(self.screenA1.ids._grid1, 0, old_size_A1-new_size_A1)
            
            #2. Reload the tiles with the content
            reload_tiles_content(self.screenA1.ids._grid1,0)
        
        # Screen A2
        if "screen A2" in screens:
            old_size_A2 = len(self.screenA2.ids._grid2.children)
            new_size_A2 = len(recipes[1])

            if new_size_A2 > old_size_A2 :
                add_empty_tiles(self.screenA2.ids._grid2, 1, new_size_A2-old_size_A2)
            elif new_size_A2 < old_size_A2:
                remove_empty_tiles(self.screenA2.ids._grid2, 1, old_size_A2-new_size_A2)
            
            reload_tiles_content(self.screenA2.ids._grid2,1)

        # Screen A3
        if "screen A3" in screens:
            self.screenA3.ids._tabs.reload_A3_screen()

        # Screen A4
        if "screen A4" in screens:
            ingredient = self.app.last_ingredient_filtered
            if not self.screen_a4_loaded: 
                self.load_A4_screen()
            rv_a4_childs = self.screenA4.ids._rv_a4.children
            if rv_a4_childs: 
                rv_a4_childs[0].populate_rvgrid(ingredient)

    def edit_full_screen(self):
        '''make the screen be full screen'''
        self.app.appbar.opacity = 0
        self.app.appbar.size_hint_y = None
        self.app.appbar.height = 0
        self.app.appbar.disabled = True    

        self.disabled_nav_bar()

    def disabled_nav_bar(self):
        ''' when screen is full, we disable nav bar. '''
        self.app.navigation.opacity = 0
        self.app.navigation.size_hint_y = None
        self.app.navigation.height = 0
        self.app.navigation.disabled = True    

    def restore_screen(self):
        '''restore the screen from full screen to normal screen '''
        self.app.appbar.opacity = 1
        self.app.appbar.size_hint_y = float(self.app.size_hint_appbar)
        self.app.appbar.disabled = False  

        self.app.navigation.opacity = 1
        self.app.navigation.size_hint_y = float(self.app.size_hint_navigation)   
        self.app.navigation.disabled = False   

    def enabled_nav_bar(self):
        self.app.navigation.opacity = 1
        self.app.navigation.size_hint_y = float(self.app.size_hint_navigation)   
        self.app.navigation.disabled = False    

    def set_previous_screen_navigation(self):
        index = self.previous_screen[-2:-1]
        match index:
            case "A":
                self.last_A_screen = self.previous_screen
            case "B":
                self.last_B_screen = self.previous_screen
            case "C":
                self.last_C_screen = self.previous_screen
            case "D":
                self.last_D_screen = self.previous_screen

    def create_invisible_a4_tile(self,difference):
        for i in range(difference):
            RVTile = MyMDSmartTile(text = "", description = "",
                                ingredients = [], source_recette = "", astuces = "",
                                commentaire = "", nb_personne = "", saison = "", index_picture = "", tile_screen = "screen A4",
                                source = source_image_default, opacity = 0)
            self.screenA4.ids._rvgrid.add_widget(RVTile)

'''##################################################################################
                                Class Screen
##################################################################################'''

class MyMDScreen(MDScreen):
    edition = BooleanProperty(False)
    tile_A0 = ObjectProperty()
    stack_A5 = ObjectProperty()
    app = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def fill_A5_stack(self):
        ''' triggered when passing from screen A0 to screen A5. the A5 stack is refilled according
        to A0 stack '''
        # delete previous stack
        self.app.manager.screenA5.ids._stack_a5.delete_all_stack()

        # fill stack with ingredients when edition recipe, other components are filled directly in KV
        for ingredient in self.tile_A0.ingredients:
            self.app.manager.screenA5.ids._stack_a5.add_ingredient(ingredient)

    def reset_recipe_items(self):
        ''' called to initialise A5 screen, when leaving A5 screen or pressing the trash button. '''
        self.app.manager.screenA5.tile_A5.ids.image.source = source_image_default
        self.app.manager.screenA5.ids._title_field.text = ""
        self.app.manager.screenA5.ids._ingredient_search_a5.text = ""
        self.app.manager.screenA5.ids._instruction_field.text = ""
        self.app.manager.screenA5.ids._source_field.text = ""
        self.app.manager.screenA5.ids._astuce_field.text = ""
        self.app.manager.screenA5.ids._commentaire_field.text = ""
        self.app.manager.screenA5.ids._nb_personne_field.text = ""
        self.app.manager.screenA5.ids.type_field.text = ""
        self.app.manager.screenA5.ids._stack_a5.delete_all_stack()
       
class ScreenPicture(MDScreen):
    # screen where camerashoot button belongs
    tile = ObjectProperty()
    app = ObjectProperty()
    picture_name = StringProperty()
    photo_preview = ObjectProperty(None) # store the widget instance Preview
    source = StringProperty()
    subdir = "recipes" # used in capture path, using stringprop seems to introduce weird behavior
    if platform in ["android", "ios"]:
        deviceOrientation = DeviceOrientation() # instance class to get orientation from java Listener
    orientation = StringProperty("6")
    torch = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_leave(self):
        self.app.manager.previous_screen = self.name

    def on_enter(self):
        Clock.schedule_once(self.preview_camera, 0)

    def preview_camera(self, dt):
        ''' 
        We add try except because of the error 'NoneType' object has no attribute 'setTexture'
        that occurs time to time, here is where self._camera is set, sometimes self._camera is None...
        '''

        try:
            # self.photo_preview.connect_camera(enable_video = False, filepath_callback= self.capture_path)
            self.photo_preview.connect_camera(filepath_callback= self.capture_path)

        except Exception as e:
            e = traceback_format_exc()
            text_exception = "---- Error while connecting to camera : " + str(e)
            log(text_exception)
            toast(self.app.current_lang["toast"][5])
            self.app.manager.current = self.app.manager.previous_screen
            self.app.check_exceptions(text_exception)
                                          
        if platform in ["android", "ios"]:
            self.deviceOrientation.sensorEnable(True)

    def capture_path(self,file_path): ## called when clicking on the camera button
        ''' Capture photo is where you set the file_path, we tried to set subdir images/recipes or notes but error 
        #/data/user/0/org.test.appname/files/DCIM/ is the root where the picture is stored, + subdir from capture photo + name + "jpg"

        if location not specified then the path will be : join(DCIM, app_name, subdir, name)
            and file will be saved to join(DCIM, app_name, subdir, name + jpg).
            but error Permisson denied when we want to open it with Pillow at :
                -join(primary_external_storage_path(), DCIM, app_name, subdir, name)
                -file_path
            because app can't access to private data from internal storage, but can access to their 
            own private data...
                
        if location = "private" means /data/user/0/org.example.my_c4k/files/DCIM/ folder

        file_path = /data/user/0/org.example.my_c4k/files/DCIM/images/0.jpg with  my_c4k name of the app
        app_storage_path returns /data/user/0/org.test.appname/files/
        file_path is the location where the picture exists same as join(app_storage_path(), "DCIM", "images", self.picture_name+".jpg")
        destination = join(".","images", self.picture_name + ".jpg") # not working with os.rename maybe
        or because it is a relative path
        Environment.DIRECTORY_DCIM = "DCIM"

        root source list dir : ['app', 'DCIM'] # list dir(join(app_storage_path()))
        app source list dir : (root source + "app") : ['main.pyc', 'libpybundle.version', 'toast.pyc', 'camerax_provider', '.nomedia', 'android_permissions.pyc', '.kivy', 'p4a_env_vars.txt', '_python_bundle', 'sitecustomize.pyc', 'private.version']
        app source not showing folder images maybe because empty ? or because buildozer clean

        os.path.exists(file_path) : True

        cannot move image file_path path to join(app_storage_path(), "app", "images", self.picture_name + ".jpg")
        because os.rename only works if folder exist, here app/images does not exist

        if folder in app root created after buildozer debug, then need a buildozer clean and debug again
        if self.source = file_path, it seems that we can't load image from there so we need to move to 
        destination folder which is : join(app_storage_path(), "app", "images", self.picture_name + ".jpg")

        when spec is portrait and no plyer orientation : exif always portrait
        when spec is portrait and screen picture is plyer.orientation set to any: exif is good '''
        
        log(" in capture path : file_path is : " + file_path)
        log(" in capture path : subdir is : " + self.subdir)
        log(" in capture path : picture_name is : " +  self.picture_name)

        self.app.source_picture = join("images",self.subdir,self.picture_name + ".jpg")
        log(" in capture path : app source_picture is : " + self.app.source_picture)

        if platform in ["android","ios"]: # not sure for ios
            ''' Move file from legacy storage (not secure) to app storage (secure)
            We wanted to thread the disconnecting for performance, but unfortunately, doesn't work, so we decide 
            to move it at beginning and performance is okay. '''

            # 1. Close and disconnect camera :
            self.change_screen_to_previous()
            self.close_camera() # we choose to close now so the waiting will be in home screen
            self.disconnect_camera()

            # 2. save the picture to shared storage before downgrading:
            private_storage = join("images",self.subdir, self.picture_name + ".jpg") # images/recipes/2.jpg
            # here save file has same source than destination because destination is tokenize and we get only the suffixe
            # We wanted to thread this one also for performance but introduce an unwanted behavior
            log("saving to shared storage path is : " + private_storage)  # images/recipes/2.jpg
            ss = MySharedStorage()
            ss.copy_to_shared(file_path, collection = Environment.DIRECTORY_DOCUMENTS, filepath = private_storage)

            
            destination = join(app_storage_path(), "app", "images", self.subdir, self.picture_name + ".jpg")
            log("capture path : destination is " + destination)
            self.source = destination
               
            # copy file from source to destination
            self.replace_file(file_path, destination, self.subdir)

            # Do some changes like orientation and resolution
            self.get_device_orientation()
            self.transpose_and_save()
            self.app.downgrade_image_resolution(destination, self.subdir)
            
            if self.subdir == "recipes":
                self.app.load_recipe_image()
            else:
                self.app.load_note_image()

            # Check File parenthesis in case android failed to replace file
            ''' We check all files, we never know how android adds parenthesis sometimes before extension
            sometimes after like (1), (2) etc.. to pictures names.'''
            dir = join("images", self.subdir)
            self.app.checkfilename(dir)
            
        elif platform in ["win","macos","linux","unknown"]: # for desktop tests
            self.change_screen_to_previous()
            self.close_camera()
            self.disconnect_camera()
            self.source = join("images", self.subdir, self.picture_name + ".jpg")
            self.app.source_picture = self.source
            # no need to copyfile here, capture photo already copy it in the subdir specified
            # if exists it is replaced by the new one
            if self.subdir == "recipes":
                self.app.load_recipe_image()
            else:               
                self.app.load_note_image()

        # added to reload Picture full image
        if exists(self.source): 
            self.reload_full_image()
            
    @mainthread
    def reload_full_image(self):
        if not self.app.manager.screen_full_picture_loaded:
            self.app.manager.load_full_picture_screen()
        self.app.manager.screenFullPicture.ids._full_image.source = self.source
        
    def replace_file(self, source, dest, subdir):
        ''' Copy and replace file if necessary from source to destination'''
        
        try:
            log("trying to replace file with copyfile")
            # we use replace, not rename, because replace is cross-platform
            # we could also use copyfile, both seems to be working       
            replace(source, dest) # move a file from source to destination 
            log("--- in replace file : success moving from DCIM to ./images/" + subdir)
        except FileNotFoundError:
            # there is no app folder so we create it,
            log("--- creating folder app for strorage purpose : " + join(app_storage_path(), "app","images",subdir))
            makedirs(join(app_storage_path(), "app","images",subdir), exist_ok = True)
            replace(source,dest)

    @mainthread # on mainthread to avoid the two screen merging.
    def change_screen_to_previous(self):
        self.app.manager.current = self.app.manager.previous_screen

    @mainthread
    def close_camera(self):
        if not self.app.A5_edition and self.app.manager.current != "screen edit note":
            self.app.manager.restore_screen()
        if platform in ["android", "ios"]:
            self.deviceOrientation.sensorEnable(False)
            self.torch.active = False

    def disconnect_camera(self):
        self.photo_preview.torch(state = "off")
        self.photo_preview.disconnect_camera()

    def get_device_orientation(self):
        # check if orientaton
        if not self.deviceOrientation.triumph:
            toast(self.app.current_lang["toast"][6])
        else:
            # retrieve orientation from java sensors
            orientation = self.deviceOrientation.getOrientation()
            orientation = str(orientation)
            self.orientation = orientation
        
    # We add decorator because TypeError not in the mainThread, 
    # this was caused because tile.source = self.source was in def capture path
    # it maybe doesn't be needed anymore
    # In general UI Changes needs to be done in mainthread

    def rotate_image(self, relative_path):
        if relative_path != source_image_default:
            if platform in ["android", "ios"]:
                image_path = join(DIR_APP_PRIVATE,relative_path)
                
            else:
                image_path = relative_path

            # 1. Rotate image  
            with Image.open(image_path) as im:
                image_transposed = im.rotate(angle=90,expand=True)

            # 2. save it to private
            image_transposed.save(image_path) # replace image

            # 3. Reload image
            self.source = relative_path
            self.app.source_picture = relative_path 

            if self.subdir == "recipes":
                self.app.load_recipe_image()
            else:
                self.app.load_note_image()

            # 4. save it to shared
            if platform in ["android", "ios"]:
                ss = MySharedStorage()
                private_storage = relative_path
                ss.copy_to_shared(private_storage, collection = Environment.DIRECTORY_DOCUMENTS, filepath = private_storage)
        
    def transpose_and_save(self):
        ''' Image.FLIP_LEFT_RIGHT : rotate y axis (mirror the image)
        Image.ROTATE_90 or 180 or 270 same as Image.rotate() anticlockwise
        Image.TRANSPOSE = Image.FLIP_LEFT_RIGHT.ROTATE_90
        Even if transpose ROTATE_270 is faster (see plyer fonction), we choose rotate more flexible with angles
        code. Warning, PIL .open or .save introduce a bug, which is the black line surrounder,
        But it's an easy fix thanks to expand=True '''

        if self.orientation != "1":
            # rotate and override image
            with Image.open(self.source) as im:
                if self.orientation == "6":  #"portrait"
                    image_transposed = im.rotate(angle=270,expand=True)
                elif self.orientation == "3":  #"landscape-reverse"
                    image_transposed = im.rotate(angle=180,expand=True)
                elif self.orientation == "8": # "portrait-reverse"
                    image_transposed = im.rotate(angle=90,expand=True)

            image_transposed.save(self.source) # replace image

class ScreenA4(MyMDScreen):
    search_by_ingredient_triggered = BooleanProperty(False)
    last_ingredient_searched = StringProperty()

class ScreenA5(MyMDScreen):
    pass

class ScreenB1(MyMDScreen):
    pass

class ScreenC1(MyMDScreen):
    pass

class ScreenD1(MyMDScreen):
    pass

class ScreenD2(MyMDScreen):
    pass

class ScreenD3(MyMDScreen):
    pass

class ScreenD4(MyMDScreen):
    pass

class ScreenRstHelp(MDScreen):
    pass

class ScreenRstCode(MDScreen):
    pass

class ScreenFullPicture(MDScreen):
    pass

class ScreenSeason(MDScreen):
    pass

'''##################################################################################
                                Class TABS Screen A3 screen settings
##################################################################################'''

class Tab(MDFloatLayout, MDTabsBase): # can be MDBoxLayout etc...
    '''Class implementing content for a tab.'''
    pass

class MyMDTabs(MDTabs):
    app = ObjectProperty()
    grid = ObjectProperty()
    current_tab = NumericProperty(0)
    last_tab = NumericProperty(0)
    tab_bar_h = NumericProperty(config_input["tab_bar_h"])
    tab_bar_size_hint_y = NumericProperty(0.1)

    def __init__(self,**args):
        super().__init__(**args)
        self.app = MDApp.get_running_app()
        self.tab_bar_height = self.tab_bar_h

    def on_tab_bar_h(self, mytab, value): # for config purpose
        self.tab_bar_height = str(value) + "dp"
        self.height = self.tab_bar_height

    def create_tabs(self):
        # create tab bar or delete and create for the loading recipe purpose   
        nb_recipes= len(recipes[2])
        tab_length = int(nb_recipes/10) + 1 if nb_recipes%10 > 0 else int(nb_recipes/10)
        self.tab_bar.layout.clear_widgets() # in case load is used on real time like in load backup recipes
        for i in range(tab_length):
            self.add_widget(Tab(title=str(i)))

    def reload_A3_screen(self):
        self.create_tabs()
        # this code is added in case new recipes_input smaller than old one and tabs open no longer exists
        if self.current_tab*10 > len(recipes[2]) :
            self.last_tab = 0
            self.current_tab = 0
        self.replace_tiles()
        self.app.manager.screenA3.scroll.scroll_y = 1

    def on_tab_switch(self, instance_tab, instance_tab_label, tab_text):
        ''' Called when more precisely when clicking on any tab
        Warning when using it threw class MDApp you need to add the parameter instance_tabs, 
        Here in MDTabs class there is no need for that one. '''

        self.last_tab = int(self.get_current_tab().title)
        self.current_tab = int(tab_text)
        if self.current_tab!= self.last_tab: 
            self.replace_tiles()
        self.app.manager.screenA3.scroll.scroll_y = 1 # reset le scroll

    def replace_tiles(self):
        ''' Replace tiles for A3 (all recipes) instead of clearing wigdet (longer)
        for case user in all recipes screen. '''

        nb_recipes= len(recipes[2])
        nb_tabs = len(self.ids.tab_bar.layout.children)

        if self.current_tab!= nb_tabs-1:
            range_tiles = range(self.current_tab*10, self.current_tab*10 +10)
            last = False
        else: 
            range_tiles = range(self.current_tab*10, nb_recipes)
            last = True

        n=1 # counter for iteration
        for i in range_tiles:
            key = str(i+1)
            instruction = recipes[2][key]["description"]
            title = recipes[2][key]["title"]
            ingredients = recipes[2][key]["ingredients"]
            commentaire = recipes[2][key]["commentaire"]
            nb_personne = recipes[2][key]["nombre de personne"] if "nombre de personne" in recipes[2][key] else ""
            saison = recipes[2][key]["saison"] if "saison" in recipes[2][key] else ""
            astuces = recipes[2][key]["astuces"]
            source_recette = recipes[2][key]["source"]

            self.app.replace_tile(self.grid.children[-n], key, instruction, title,
                                                 ingredients, commentaire, nb_personne, saison, astuces, source_recette)
            n+=1
        
        if last: # last tabs has n tiles between[1:10] so we need to turn off those who will not be showed
            nb_usual_range = 11 
            nb_range = self.app.nb_recipe_returned(nb_usual_range) # check if nb less than 10
            for i in range(n, nb_range):
                self.grid.children[-i].opacity = 0

    def change_tabs_color(self,rgba_color, active_color, inactive_color):
        self.tab_bar.md_bg_color = rgba_color
        for tab_label in self.get_tab_list():
            if not self.text_color_normal:
                tab_label.text_color_normal = inactive_color
            if not self.text_color_active:
                tab_label.text_color_active = active_color

'''##################################################################################
                                Class Camera Picture
##################################################################################'''

class FlashIcons(ButtonBehavior, Label):
    active = BooleanProperty(False)

    def on_active(self,*args):
        if self.active:
            with self.canvas.before:
                Color(rgba = self.icon_active)
        else:
            with self.canvas.before:
                Color(rgba = self.icon_inactive)

class MyPreview(Preview):
    screen = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Lowering the resolution allows to speed up the app, and avoid black screen, memory error.
        if platform in ["android", "ios"]:
            self.preview = MyPreviewCameraX()
        else :
            self.preview = CameraPreview()

        child = self.children[0]
        self.remove_widget(child)
        self.add_widget(self.preview)
        for key in ['letterbox_color', 'aspect_ratio',
                'orientation']:
            if key in kwargs:
                setattr(self, key, kwargs[key])
                if key == 'aspect_ratio':
                    self.preview.set_aspect_ratio(kwargs[key])
                if key == 'orientation':
                    self.preview.set_orientation(kwargs[key])

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.close_camerascreen()
            
        return super().on_touch_down(touch)

    def close_camerascreen(self):
        self.screen.change_screen_to_previous()
        self.screen.close_camera()
        self.disconnect_camera()

class CameraShootButton(ButtonBehavior, Label):

    def darker(self, color, factor=0.5):
        r, g, b, a = color
        r *= factor
        g *= factor
        b *= factor
        return r, g, b, a

if platform in ["android", "ios"]:
    class MySharedStorage(SharedStorage):
        ''' Override Class SharedStorage, to save picture not in Android Picture 
            Collection but in Documents '''
        

        def copy_to_shared(self, private_file, collection = None, filepath = None, MIME_type = "text/plain"):
            ''' Warning working with python file as mime-type will fail because it returns None, python file seems to be invisible
            so instead we copy the content to a txt file and its okay not beautiful but works
            MIME_type = "text/plain" to save to Documents collection '''

            # path1 = join("images","recipes",basename_image_default) # uri exists
            # path4 = join(app_storage_path(), "app", "images","recipes",basename_image_default) # exists
            # path2 = join("core","input_recettes.py") # uri is NONE does not exists
            # path6 = join(app_storage_path(), "app", "core","input_recettes.py") # does not exists

            log("------ copy_to_shared MySharedStorage start  -------")
            log("------ copy_to_shared private file is : " + private_file)
            log("------ copy_to_shared filepath is : " + filepath)
            log("------ copy_to_shared private exists : " + str(exists(private_file)))

            FileInputStream = autoclass('java.io.FileInputStream')
            FileUtils = autoclass('android.os.FileUtils')
            ContentValues = autoclass('android.content.ContentValues')

            if private_file == None or not exists(private_file):
               return None
            log("------ copy_to_shared MySharedStorage 1  -------")
            file_name = basename(private_file) # basename("folder1.file1.text") returns file1.txt
            # MIME_type = self.get_file_MIME_type(file_name) # xavier1 returns the mime type here "text/plain"
            log("------ copy_to_shared MySharedStorage 2  -------")
            auto_collection = self._get_auto_collection(MIME_type) # return collection from mimetype here "Documents" (Environment.DIRECTORY_DOCUMENTS)            
            if not self._legal_collection(auto_collection, collection): # check if arg collection correct
                collection = auto_collection
            path = [collection, appname] # ["Documents","appname"]

            if filepath: # "fold1/fold2/file1.txt"
                sfp = filepath.split('/') # ["fold1","fold2","file1.txt"]
                file_name = sfp[-1] # "file1.txt"
                for f in sfp[:-1]:
                    path.append(f) # ["Documents","appname","fold1","fold2"]

            log("------ copy_to_shared MySharedStorage 3  -------")
            if api_version > 28:
                log("------ copy_to_shared MySharedStorage 3 api 28  -------")
                sub_directory = ''
                for d in path:
                    sub_directory = join(sub_directory,d) # "Documents/appname/fold1/fold2"
                #uri = self._get_uri(join(sub_directory, file_name), text/plain) # text/plain, text/x-python
                uri = self._get_uri(join(sub_directory, file_name), MIME_type) # text/plain, text/x-python
                log("----copy_to_shared MySharedStorage----------uri is : " + str(uri))
                try:
                    cr =  context.getContentResolver()
                    ws = None
                    if uri:
                        log("------ copy_to_shared MySharedStorage 4  -------")
                        try:
                            ws  = cr.openOutputStream(uri,"rwt") # "rwt" for read and write access that truncates any existing file, truncates means the file is not deleted but truncated to 0 bits.
                        except:
                            log('File replace permission not granted.')
                            log('A new file version will be created.')
                            uri = None
                            text_exception = "In ss.copy_to_shared, uri could not be retrieve " \
                            "with ss._get_uri and private file we wanted to copy is " + str(private_file)
                            MDApp.get_running_app().check_exceptions(text_exception)

                    if not ws:
                        cv = ContentValues()
                        cv.put(MediaStoreMediaColumns.DISPLAY_NAME, file_name)
                        cv.put(MediaStoreMediaColumns.RELATIVE_PATH, sub_directory)
                        root_uri = MediaStoreFiles.getContentUri('external')
                        uri = cr.insert(root_uri, cv)
                        ws  = cr.openOutputStream(uri)
                        # see https://android.googlesource.com/platform/frameworks/base/+/851a541/core/java/android/content/ContentResolver.java
                    # copy file contents
                    rs = FileInputStream(private_file)
                    FileUtils.copy(rs,ws)
                    ws.flush()
                    ws.close()
                    rs.close()
                except Exception as e:
                    e = traceback_format_exc()
                    log("------ copy_to_shared MySharedStorage exception  -------")
                    log_warning('SharedStorage.copy_to_shared():')
                    log_warning(str(e))
                    uri = None
                    text_exception = "---- Error in ss.copy_to_shared while trying to copy: " + str(e)
                    MDApp.get_running_app().check_exceptions(text_exception)
                return uri
            else:
                root_directory = self._get_legacy_storage_location() # storage/emulated/0
                log("--------------in copy_to_shared root directory : " + str(root_directory))
                if root_directory == None:
                    return None
                sub_directory = root_directory
                for d in path:
                    sub_directory = join(sub_directory,d) 

                    if not exists(sub_directory):
                        log("-------in copy_to_shared creating sub_directory : " + str(sub_directory))
                        mkdir(sub_directory)
                public_path = join(sub_directory, file_name)
                self.delete_shared(public_path)
                copyfile(private_file, public_path)
                return public_path

        def _get_uri(self, shared_file, mimetype): # mimetype  xavier 0 shared_file "Documents/appname/fold1/fold2/file1.ext"
            ''''shared_file should be Documents/appname/ect...'''

            ContentUris = autoclass('android.content.ContentUris')
            if type(shared_file) == str:
                shared_file = shared_file
                if 'file://' in shared_file or 'content://' in shared_file:
                    return None
            else:
                uri = cast('android.net.Uri',shared_file)
                try:
                    if uri.getScheme().lower() == 'content':
                        return uri
                    else:
                        return None
                except:
                    return None

            file_name = basename(shared_file) # ex : "file1.ext"
            # MIME_type = self.get_file_MIME_type(file_name) # text/plain
            MIME_type = mimetype # xavier4
            path = shared_file.split('/') # ["Documents", "appname", "fold1...", "file1.ext"]
            if len(path) < 1:
                return None
            root = path[0] # "Documents"
            self.selection = MediaStoreMediaColumns.DISPLAY_NAME+"=? AND " # "_display_name=? AND "
            if api_version > 28:
                location = ''
                for d in path[:-1]:
                    location = join(location,d) # location = "Documents/appname/fold1"
                self.selection = self.selection +\
                    MediaStoreMediaColumns.RELATIVE_PATH+"=?" # "_display_name=? AND relative_path=?"
                self.args = [file_name, location+'/'] # [file1.ext,"Documents/appname/fold1/"]
            else:
                self.selection = self.selection + MediaStoreMediaColumns.DATA+"=?" # "_display_name=? AND _data=?"
                self.args = [file_name, shared_file] # ["file1.ext", "Documents/appname/fold1/fold2/file1.ext"]

            root_uri = self._get_root_uri(root, MIME_type) #returns uri
            cursor = context.getContentResolver().query(root_uri, 
                                                        None,
                                                        self.selection,
                                                        self.args, 
                                                        None)
            fileUri = None
            if cursor:
                while cursor.moveToNext():
                    dn = MediaStoreMediaColumns.DISPLAY_NAME
                    index = cursor.getColumnIndex(dn)
                    fileName = cursor.getString(index)
                    if file_name == fileName:
                        id_index = cursor.getColumnIndex(MediaStoreMediaColumns._ID)
                        id = cursor.getLong(id_index)
                        fileUri = ContentUris.withAppendedId(root_uri,id)
                        break
                cursor.close()
            return fileUri

    class MyPreviewCameraX(PreviewCameraX):
        
        def capture_photo(self, location = '',  subdir = '', name = ''):
            if self._camera:
                self.capture_in_progress = True
                self._set_location(location)
                subdir = self._default_subdir_android(subdir)
                name = self._default_file_name(name, '.jpg')
                log(" debug in preview : subdir : " + subdir)
                log(" debug in preview : name : " + name)
                if self.file_storage:
                    self._name_pipe.append(join(subdir, name))
                self._camera.capture_photo(subdir, name, self.file_storage)

        @mainthread
        def _create_pipeline(self, texture_size, rotation):
            id = self._create_texture(texture_size)
            self._create_fbo(texture_size, rotation)
            if self._camera:
                self._camera.setTexture(id,texture_size)
                self._schedule_pipeline()
            else:
                # $bug sometimes self._camera does not exists... don't have time so this is a trick to avoid app crash
                Clock.schedule_once(partial(self.setTexture_scheduled, id, texture_size), .5)

        @mainthread
        def setTexture_scheduled(self, id, texture_size, value):
            '''because sometimes _camera is not set yet, we try to schedule it...'''
            app = MDApp.get_running_app()
            if self._camera:
                self._camera.setTexture(id,texture_size)
                self._schedule_pipeline()
            else:
                app.manager.screenPicture.change_screen_to_previous()
                toast(app.current_lang["toast"][4])

        def _default_location(self):
            ''' we override this method to change the root_path, I know it is not a good idea for internal functions '''
            
            if self.private_storage:
                root_path = join(app_storage_path(),"app") # modif xavier before /data/user/0/org.test.appname/files/DCIM
                if not exists(root_path):
                    mkdir(root_path)
            else:
                if api_version < 29:
                    root_path = join(primary_external_storage_path(),
                                Environment.DIRECTORY_DCIM,
                                self._app_name())
                    if not exists(root_path):
                        mkdir(root_path)
                else:
                    root_path = join(Environment.DIRECTORY_DCIM, self._app_name())
            return root_path

'''##################################################################################
                                Classes Note
##################################################################################'''

class StackBoxLayout(MDBoxLayout):
    '''
    To avoid to add fake note because note is bottom placed when adpative height = True,
    we add pos_hint: {"top": 1} to the NoteStackLayout
    Only working with BoxLayout, not Grid !!!
    '''

    app = ObjectProperty()
    notes_list = ListProperty()
    notes_filered_list = ListProperty()
    notes_selected_list = ListProperty()
    left_h = NumericProperty(0)
    right_h = NumericProperty(0)
    left_h_filtered = NumericProperty(0)
    right_h_filtered = NumericProperty(0)
    new_note_stack = StringProperty()
    matches = ListProperty()
    filtering = BooleanProperty(False) # avoid selecting and filtering at the same time which will get some trouble

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    @mainthread
    def load_notes_from_data(self):
        ''' notes loaded added when coming back from a note'''
        for key in note_index:
            self.get_stacks_heights()
            if self.left_h <= self.right_h:
                self.add_new_note_init(key, note_data[key]["description"], 1)
            else:
                self.add_new_note_init(key, note_data[key]["description"], 2)
         
    def equalize_stack(self):
        ''' Used when user delete notes from selection, some test 
        are still needed there, but seems to work quite good. '''

        self.get_stacks_heights()

        if self.left_h < self.right_h:
            diff = self.right_h - self.left_h
            h = self.app.manager.screenC1.ids["_selection_list_2"].children[0].height
            diff2 = abs(diff - 2*h - 20) # after mathemat calculat
            while  diff2 < diff :
                last = self.app.manager.screenC1.ids["_selection_list_2"].children[0]
                self.app.manager.screenC1.ids["_selection_list_2"].remove_widget(last)
                self.app.manager.screenC1.ids["_selection_list_1"].add_widget(last)
                self.get_stacks_heights()
                diff = diff2
                h = self.app.manager.screenC1.ids["_selection_list_2"].children[0].height
                diff2 = abs(self.right_h-self.left_h - 2*h - 20) # after mathemat calculat

        else:
            diff = self.left_h-self.right_h
            h = self.app.manager.screenC1.ids["_selection_list_1"].children[0].height
            diff2 = abs(diff - 2*h - 20) # after mathemat calculat
            while  diff2 < diff:
                last = self.app.manager.screenC1.ids["_selection_list_1"].children[0]
                self.app.manager.screenC1.ids["_selection_list_1"].remove_widget(last)
                self.app.manager.screenC1.ids["_selection_list_2"].add_widget(last)
                self.get_stacks_heights()
                diff = diff2
                h = self.app.manager.screenC1.ids["_selection_list_1"].children[0].height
                diff2 = abs(self.left_h-self.right_h  -2*h - 20) # after mathemat calculat

    def add_new_note_init(self, text, desc, column):
        new_note = Note(size_hint =(1,None),
                            title = text, description = desc, 
                            md_bg_color = self.app.unselected_note_color
                        )
        self.notes_list.append(new_note)

        stack1_len = len(self.app.manager.screenC1.ids["_selection_list_1"].children)
        stack2_len = len(self.app.manager.screenC1.ids["_selection_list_2"].children)

        if column == 1:
            self.app.manager.screenC1.ids["_selection_list_1"].add_widget(new_note, stack1_len + 1)
        if column == 2:
            self.app.manager.screenC1.ids["_selection_list_2"].add_widget(new_note, stack2_len + 1)

    def reload_note(self, note, text, desc):
        # reload note when note already created
            note.title = text
            note.description = desc

    def add_new_note(self, text, desc, filter):
        self.get_stacks_heights()
        new_note = Note(size_hint = (1,None),
                        title = text, description = desc,
                        )
        stack1_len = len(self.app.manager.screenC1.ids["_selection_list_1"].children)
        stack2_len = len(self.app.manager.screenC1.ids["_selection_list_2"].children)
        if filter:
            self.notes_filered_list.append(new_note)
            # ajouter note a la hauteur la plus petite mais hauteur relative sans prendre en compte hauteur total
            if self.left_h_filtered <= self.right_h_filtered:
                self.app.manager.screenC1.ids["_selection_list_1"].add_widget(new_note,stack1_len + 1)
                self.new_note_stack = "_selection_list_1"
                self.left_h_filtered += new_note.height
                
            else :
                self.app.manager.screenC1.ids["_selection_list_2"].add_widget(new_note, stack2_len + 1)
                self.new_note_stack = "_selection_list_2"
                self.right_h_filtered += new_note.height

        else:
            self.notes_list.append(new_note)

            if self.left_h <= self.right_h:
                self.app.manager.screenC1.ids["_selection_list_1"].add_widget(new_note,stack1_len + 1)
                self.new_note_stack = "_selection_list_1"

            else :
                self.app.manager.screenC1.ids["_selection_list_2"].add_widget(new_note, stack2_len + 1)
                self.new_note_stack = "_selection_list_2"

    def get_stacks_heights(self):
        def stack_height(id):
            h = 0
            count = 1
            for note in self.app.manager.screenC1.ids[id].children:
                h+= note.height
                count +=1 
            h = h + count * 10
            return h

        self.left_h = stack_height("_selection_list_1")
        self.right_h = stack_height("_selection_list_2")

    @mainthread
    def delete_all_notes(self):
        log("------ delete all_notes start  -------")
        Note.selected_notes = 0
        self.notes_selected_list = []
        self.notes_list = []
        if not self.app.manager.screen_c1_loaded:
            self.app.manager.load_C1_screen()
        self.app.manager.screenC1.ids._selection_list_1.clear_widgets()
        self.app.manager.screenC1.ids._selection_list_2.clear_widgets()
        log("------ delete all_notes end  -------")

    def delete_notes_selection(self):
        note_deleted = []
        Note.selected_notes = 0
        backup_dir = join("data","backup","images")

        # 1. Loop threw the notes selected
        for note in self.notes_list:
            if note.long_touched:
                note.parent.remove_widget(note)
                note_deleted.append(note)
                pictures_to_delete = []
                for item in note_data[note.title]["data"]:
                    if 'Picture' in item[0] and item[1] != basename_image_default:
                        pictures_to_delete.append(item[1])
                
                for picture_name in pictures_to_delete:

                # a. save the image note to backup folder
                    source = join("images","notes",picture_name)
                    dest = join(backup_dir, picture_name)
                    if platform in ["android", "ios"]:
                        self.app.save_to_shared(source, dest)
                        self.app.checkfilename(backup_dir)
                        
                    elif platform in ["win","macos","linux","unknown"]:
                        try:
                            copyfile(source, dest)
                        except FileNotFoundError:
                            # if no files in folder it will raise error
                            # there is no app folder or source does not exists,
                            makedirs(backup_dir, exist_ok = True) # exist_ok = True otherwise can raise error if folder exists
                            if exists(source):
                                copyfile(source, dest)
                                log("--------- backup list file are : " + str(self.app.java_list_files(backup_dir)))

                # b. remove the picture from private

                    if platform in ["android", "ios"]:
                        private_path = join(DIR_NOTES_PRIVATE,picture_name)
                    else:
                        private_path = join("images","notes", picture_name)

                    if exists(private_path):
                        remove(private_path)
                        log("The file located at : " + private_path + " has been removed")
                    else:
                        log("The file located at : " + private_path + " does not exist")

                # c. remove the picture from shared
                    if platform in ["android", "ios"]:
                        shared_path = join(ROOT_FOLDER,"Documents", appname, "images", "notes", picture_name)
                        self.app.delete_file_java(shared_path)
                
            # d. remove note data key title    
                del note_data[note.title]
                note_index.remove(note.title)
 
        # 2. save note_data to private
        self.app.manager.screenEditNote.ids["_note_box"].save_notes_to_private() 
        self.notes_selected_list = []
        
        # 3. save note_data to shared :
        if platform in ["android", "ios"]:
            self.app.manager.screenEditNote.ids["_note_box"].save_notes_to_shared()

        # 4. remove notes from notes_list
        for note in note_deleted:
            self.notes_list.remove(note)
            
        # 5. equalize stack
        if len(self.notes_list) > 2:
            self.equalize_stack()
        
        # 6. reset appbar
        self.app.appbar.reset_appbar_notes_unselected()
        self.app.manager.enabled_nav_bar()
       
    def unselect_notes(self, button):
        # needs the button argument because this function is binded
        for note in self.notes_list:
            note.unselect_note()

        self.app.appbar.reset_appbar_notes_unselected()
        self.app.manager.enabled_nav_bar()

    def notes_filter(self):
        '''triggered when notes number is 6 or more and search icon pressed'''

        #1. opacify and disable new note button
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].opacity = 0
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].disabled = True

        #2 opacify and disable all notes in stack
        for stack in range(2):
            for note in self.children[stack].children:
                note.opacity = 0
                note.disabled = True
        
        # add the 5 matches
        for item in self.matches[::-1]:
            desc = note_data[item]["description"]
            self.add_new_note(item, desc, True)

    def notes_unfilter(self):
        ''' triggered when user press close texfield search or input text is empty '''

        #1. opacify and disable new note button
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].opacity = 1
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].disabled = False

        #2 opacify and disable all notes in stack
        for stack in range(2):
            for note in self.children[stack].children:
                note.opacity = 1
                note.disabled = False

        # remove the 5 matches 
        for note in self.notes_filered_list:
            if note in self.children[0].children:
                self.children[0].remove_widget(note)
            else:
                self.children[1].remove_widget(note)
        
        self.notes_filered_list = []
        self.left_h_filtered = 0
        self.right_h_filtered = 0

class Note(MDCard, CommonElevationBehavior, TouchBehavior):
    app = ObjectProperty()
    selected_notes = 0
    unselected_color = "#f8f5f4ff"
    selected_color = "#f4b5b5ff"
    long_touched = BooleanProperty(False)
    title = StringProperty()
    description = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def on_press(self):
        filtering = self.app.manager.screenC1.ids["_selection_list"].filtering
        if self.long_touched:
            if Note.selected_notes > 1:
                self.unselect_note()
            else:
                self.unselect_last_note()
        else:
            if Note.selected_notes > 0 and not filtering :
                self.select_note()

        self.app.manager.screenEditNote.saved_note = False

    def delay_notes_count(self, dt):
        Note.selected_notes -= 1
        
    def on_release(self):
        if Note.selected_notes == 0 :
            self.app.manager.screenEditNote.ids["_note_box"].note_selected = self
            self.app.manager.screenEditNote.ids["_note_box"].deactivate_edit_mode()
            self.load_note()

    def select_note(self):
        self.long_touched = True
        self.app.manager.screenC1.ids["_selection_list"].notes_selected_list.append(self)
        Note.selected_notes +=1
        self.md_bg_color = self.app.selected_note_color
        self.app.appbar.title = str(Note.selected_notes)

    def unselect_note(self):
        if self.long_touched:
            self.long_touched = False
            self.app.manager.screenC1.ids["_selection_list"].notes_selected_list.remove(self)
            Note.selected_notes -=1
            self.md_bg_color = self.app.unselected_note_color
            self.app.appbar.title = str(Note.selected_notes)

    def unselect_last_note(self):
        self.long_touched = False
        self.app.manager.screenC1.ids["_selection_list"].notes_selected_list.remove(self)
        self.md_bg_color = self.app.unselected_note_color
        self.app.appbar.reset_appbar_notes_unselected()
        self.app.manager.enabled_nav_bar()
        Clock.schedule_once(self.delay_notes_count, 0.1)
    
    def load_note(self):
        if config_input["default_theme"] == "Black":
            self.app.mdbg_screen_edit_note = self.app.main_theme_bg_color
            self.app.text_notefield_color_normal = self.app.white_rgba_80
            self.app.item_icon_button_color = self.app.white_rgba_80
            self.app.separator_line_color = self.app.white_rgba_38
            self.app.line_textfield_note_color_normal = self.app.main_theme_bg_color

        for item in note_data[self.title]["data"]:
            widget_type = item[0]

            if "TextFieldBox" in widget_type:
                text = item[1]
                self.app.manager.screenEditNote.ids._note_box.add_widget(TextFieldBox(text = text))
                    
            elif "TitleFieldBox" in widget_type:
                text = item[1]
                self.app.manager.screenEditNote.ids._note_box.add_widget(TitleFieldBox(title = text))

            elif "RstBox" in widget_type:
                ''' because the md_bg of the emphasis text is hard to change, maybe not possible, 
                we change the  background rst screen edit note color '''
                
                self.app.mdbg_screen_edit_note = self.app.white_rgba_default
                self.app.text_notefield_color_normal = self.app.black_rgba_80
                self.app.item_icon_button_color = self.app.black_rgba_80
                self.app.separator_line_color = self.app.black_rgba_38
                self.app.line_textfield_note_color_normal = self.app.white_rgba_theme

                self.app.set_default_rst_colors()

                text = item[1]
                widget = RstBox(text = text)
                widget.children[0].colors["paragraph"] = self.app.rstbox_paragraph_color
                widget.children[0].colors["title"] = self.app.rstbox_title_color
                widget.children[0].colors["bullet"] = self.app.rstbox_bullet_color
                widget.children[0].colors["background"] = self.app.rstbox_background_color
                
                self.app.manager.screenEditNote.ids._note_box.add_widget(widget)

            elif "Picture" in widget_type:
                source = item[1]
                if source == basename_image_default and platform == "android":
                    source_picture = join(DIR_APP_PRIVATE,"images",source)

                elif platform == "android" and source != basename_image_default:
                    source_picture = join(DIR_NOTES_PRIVATE, source)

                elif platform != "android" and source == basename_image_default:
                    source_picture = join("images", source)

                else: 
                    source_picture = join("images","notes", source)

                self.app.manager.screenEditNote.ids._note_box.add_widget(PictureBox(source = source_picture))

            elif "NoteField" in widget_type:
                text = item[1]
                self.app.manager.screenEditNote.ids._note_box.add_widget(NoteField(text = text, font_size= "32sp",
                                                             multiline = True))
            elif "Separator" in widget_type:
                self.app.manager.screenEditNote.ids._note_box.add_widget(SeparatorBox())

        self.app.manager.transition.direction = "up" # $transition
        self.app.manager.edit_full_screen()
        self.app.manager.current = "screen edit note"  

    def on_long_touch(self, touch, *args):
        ''' comes before on_release we could code the fact the user can filter 
        and select note at the same time but too lazy for that, because of conflict we add a filtering boolean'''
        filtering = self.app.manager.screenC1.ids["_selection_list"].filtering

        if Note.selected_notes == 0 and not filtering :
            self.app.manager.disabled_nav_bar()
            self.select_note()
            self.app.appbar.reset_appbar_notes_selected()

class ScreenEditNote(MDScreen):
    app = ObjectProperty()
    saved_note = BooleanProperty(False)
    item_disabled = BooleanProperty(False)
    item_opacity = NumericProperty(1)
    item_height = NumericProperty(dp(40)) # seems to have no incidence
    next_screen = StringProperty()
    speed_object = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_leave(self):
        if self.next_screen == "screen C1":
            self.item_disabled = True
            self.item_opacity = 0
            self.item_height = dp(0)

            self.speed_object.ids["_add_note_action_button"].opacity = 0
            self.speed_object.ids["_add_note_action_button"].close_speed()
            self.ids["_pencil_edit_note"].icon = "pencil"

    def on_touch_down(self, touch): # here touch is a parameter that contains useful information like coordinates
        if self.speed_object.ids["_add_note_action_button"].speed_active :
        
            if not self.speed_object.ids["_speed_text_button"].collide_point(touch.x, touch.y) and \
            not self.speed_object.ids["_speed_title_button"].collide_point(touch.x, touch.y) and \
            not self.speed_object.ids["_speed_picture_button"].collide_point(touch.x, touch.y) and \
            not self.speed_object.ids["_speed_separator_button"].collide_point(touch.x, touch.y) and \
            not self.speed_object.ids["_speed_rst_button"].collide_point(touch.x, touch.y) and \
            not self.speed_object.ids["_add_note_action_button"].collide_point(touch.x, touch.y) : 
                self.speed_object.ids["_add_note_action_button"].close_speed()
                return True # tells the parent, if we took care of the event by True and not by False
            return super(ScreenEditNote,self).on_touch_down(touch)
        return super(ScreenEditNote,self).on_touch_down(touch)

class NoteBoxLayout(MDBoxLayout):
    app = ObjectProperty()
    content_cls = ObjectProperty()
    dialog = ObjectProperty()
    note_selected = ObjectProperty()
    edit_mode = BooleanProperty(False)
    nb_picture_notebox = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def on_kv_post(self,w):
        self.nb_picture_notebox = self.calculate_notebox_picture()

    def get_indice_picture(self, picture):
        n = 0
        for item in self.children[::-1]:
            widget_type = str(item.__self__)

            if "Picture" in widget_type:
                n+=1
                if widget_type == str(picture.parent.__self__):
                    break
        return n

    def save_note(self):
        ''' The note is saved even no changes has been made, it' ok for now. Maybe later we'll add a condition '''

        log("---- save_note start -----")
        dic_items = {}
        all_items = []
        description = None
        save_description = True
        for item in self.children[::-1]:
            widget_type = str(item.__self__)

            if "TextFieldBox" in widget_type:
                text = item.ids._notefield_text.text
                all_items.append(["TextFieldBox", text])
                if save_description:
                    index = int(logar(len(text)+1)) * 10 + 1
                    description = text[0:index] + "..."
                    save_description = False
                    
            elif "TitleFieldBox" in widget_type:
                text = item.ids._notefield_title.text
                all_items.append(["TitleFieldBox", text])

            elif "RstBox" in widget_type:
                text = item.ids._rst_note.text
                all_items.append(["RstBox", text])
                if save_description:
                    index = int(logar(len(text))) * 10 + 1
                    description = text[0:index] + "..."
                    save_description = False

            elif "Picture" in widget_type:
                source = item.source
                log(" the source of the picture is : " + source)
                all_items.append(["Picture", basename(source)])

            elif "Separator" in widget_type:
                all_items.append(["Separator"])
 
            elif "NoteField" in widget_type:
                text = item.text
                all_items.append(["NoteField", text])

        key = all_items[0][1]
        if not description:
            description = "..."

        dic_items["data"] = all_items
        dic_items["description"] = description

        # two conditions there in case, we change the name of a current note
        if key not in note_data.keys() and not self.note_selected.description:  
            note_index.append(key)
            self.app.manager.screenC1.ids._selection_list.add_new_note(key, description, False)    
        else: 
            previous_key = self.note_selected.title

            if key != previous_key and key in note_data.keys():
                self.children[-1].error = True
                self.children[-1].hint_text = self.app.current_lang["dialog"][10]
                return 
            
            # reload note
            else:
                self.app.manager.screenC1.ids._selection_list.reload_note(self.note_selected, key, description)
                if key != previous_key:
                    del note_data[previous_key]
                    note_index.insert(note_index.index(previous_key), key)
                    note_index.remove(previous_key)
            
        note_data[key] = dic_items
        
        # save to private :
        self.save_notes_to_private()

        # save to shared :
        if platform in ["android", "ios"]:
            self.save_notes_to_shared()

        # leave screen    
        self.clear_widgets()
        self.app.manager.screenEditNote.next_screen = "screen C1"
        self.app.manager.transition.direction = "down"
        self.app.manager.current = "screen C1"
        log("---- save note end -----")

    def save_notes_to_private(self):
        log("------ save_notes_to_private start  -------")
        json_note_data = json_dumps(note_data, ensure_ascii=False, indent= 4)
        with open(join("data","note_data.py"), 'w',encoding='utf-8') as f:
            f.write("note_data = " + str(json_note_data) + "\n" +
                        "note_index = " + str(note_index))
        log("------ save_notes_to_private end  -------")
            
    def save_notes_to_shared(self):
        log("------ save notes_to_shared start  -------")
        ss = MySharedStorage()
        source = join("data","note_data.py")
        dest = join("data", "note_data.py")
        ss.copy_to_shared(source, collection = Environment.DIRECTORY_DOCUMENTS, filepath = dest) # if folder in file_path then it wil be created
        # Check File parenthesis in case android failed to replace file
        dir = "data"
        self.app.checkfilename(dir)
        log("------ save notes_to_shared end  -------")

    def activate_edit_mode(self):
        ''' triggered when user press edit, allow him to access to the note's items. '''

        self.app.manager.screenEditNote.ids["_pencil_edit_note"].icon = "pencil-off"
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].opacity = 1
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].disabled = False

        self.app.manager.screenEditNote.item_opacity = 1
        self.app.manager.screenEditNote.item_disabled = False

        self.app.manager.screenEditNote.saved_note = True
        self.app.manager.screenEditNote.item_height = dp(40)

        self.edit_mode = True # controller for enabled/disabled NoteField

    def deactivate_edit_mode(self):
        ''' triggered when user press edit striped, or when user add a new note, 
        prevent user from modifying note items. '''

        self.app.manager.screenEditNote.ids["_pencil_edit_note"].icon = "pencil"
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].opacity = 0
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].disabled = True
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].close_speed()

        self.app.manager.screenEditNote.item_opacity = 0
        self.app.manager.screenEditNote.item_disabled = True

        self.app.manager.screenEditNote.item_height = dp(0)

        self.edit_mode = False # controller for enabled/disabled NoteField

    def add_textfield(self):
        textfield = TextFieldBox()
        self.add_widget(textfield)
        self.close_speed_dial()
        Clock.schedule_once(partial(self.delay_focus_textfield, textfield.ids._notefield_text), 0)

    def add_separator(self):
        self.add_widget(SeparatorBox())
        self.close_speed_dial()

    def edit_rst(self):
        if not self.app.manager.screen_rst_edit_loaded:
            self.app.manager.load_rst_edit_screen()

        self.app.manager.current = "screen rst edit"
        self.app.manager.screenRstEdit.ids._textinput_edit.text = "Titre RST" + "\n" + "--------------"
        self.close_speed_dial()

    def add_rst(self, rst, rst_text):
        if not rst.rst_edition:
            self.add_widget(RstBox(text = rst_text))
        else:
            rst.rst_edition = False
            rst.rst_edited.text = rst_text

        rst.render()

    def calculate_notebox_picture(self):
        n = 0
        for item in self.children[::-1]:
            widget_type = str(item.__self__)
            if "Picture" in widget_type:
                n+=1
        return n

    def add_picture(self):
        self.add_widget(PictureBox(source = source_image_default))
        self.close_speed_dial()

    def create_title_note(self, instance_button, dialog_content, dialog_instance):
        title = dialog_content.ids._dialog_field.text
        self.app.manager.screenEditNote.ids["_note_box"].note_selected = Note(title=title) # added without root = to differ New Note from an old note,see save_note()
        
        if title not in note_data and title!= "" :
            self.add_widget(NoteField(text = title, multiline= True, 
                                    font_size= "32sp"))
            dialog_instance.dismiss()
            self.close_speed_dial()
            self.app.manager.edit_full_screen()
            self.app.manager.current = "screen edit note"
            dialog_content.ids._dialog_field.error = False
            dialog_content.ids._dialog_field.hint_text = self.app.current_lang["dialog"][1]

        elif title == "":
            dialog_content.ids._dialog_field.error = True
            dialog_content.ids._dialog_field.hint_text = self.app.current_lang["dialog"][9]
        else:
            dialog_content.ids._dialog_field.error = True
            dialog_content.ids._dialog_field.hint_text = self.app.current_lang["dialog"][10]

    def add_title(self):
        self.show_note_dialog()

    def add_another_title(self):
        titlefield = TitleFieldBox()
        self.add_widget(titlefield)
        self.close_speed_dial()
        Clock.schedule_once(partial(self.delay_focus_textfield, titlefield.ids._notefield_title), 0)

    def show_note_dialog(self):
        ''' Here lambda function is needed because we need to return args
        otherwise just on_release = myfunction # is ok. '''
        self.content_cls = DialogNoteContent()
        self.dialog = MyMDDialog(
            id_dialog = "note_creation",
            title= self.app.current_lang["dialog"][0],
            type="custom",
            content_cls= self.content_cls,
            pos_hint = {"center_x":.5, "top":.8},
            buttons=[
                MDFlatButton(
                    text= self.app.current_lang["dialog"][7],
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release= lambda x: self.app.close_dialog(x, self.dialog),
                ),
                MDFlatButton(
                    text= self.app.current_lang["dialog"][6],
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release= lambda x: self.create_title_note(x, self.content_cls, self.dialog),
                ),
            ],
        )
        self.dialog.open()
        Clock.schedule_once(partial(self.delay_focus_textfield, self.content_cls.ids._dialog_field), 0.8)

    def delay_focus_textfield(self, textfield_instance, dt):
        textfield_instance.focus = True

    def close_speed_dial(self):
        self.app.manager.screenEditNote.speed_object.ids["_add_note_action_button"].close_speed()

    def trash_item(self, item):
        ''' Allow user to delete a notebox item like a picture or textbox. '''
        
        widget_type = str(item.parent.__self__)
        backup_dir = join("data","backup","images")
        if "Picture" in widget_type:
            source_path = item.parent.source # "images/notes/picture1.jpg"
            if basename(source_path) != basename_image_default:
                # 1. save the image note_data to backup folder, use when we load a note_data file backup
                dest = join(backup_dir, basename(source_path))

                if platform in ["android", "ios"]:
                    self.app.save_to_shared(source_path, dest)
                    self.app.checkfilename(backup_dir)

                elif platform in ["win","macos","linux","unknown"]:
                    try:
                        copyfile(source_path, dest)
                    except FileNotFoundError:
                        log("there is no file")

                # 2. remove the picture from private
                if platform in ["android", "ios"]:
                    private_path = join(DIR_APP_PRIVATE,source_path)
                else:
                    private_path = source_path

                if exists(private_path):
                    remove(private_path)
                    log("The file located at : " + private_path + " has been removed")
                else:
                    log("The file located at : " + private_path + " does not exist")

                # 3. remove the picture from shared
                if platform in ["android", "ios"]:
                    shared_path = join(ROOT_FOLDER,"Documents", appname, source_path)
                    self.app.delete_file_java(shared_path)

        self.remove_widget(item.parent)

    def move_item(self, item, up_or_down):
        index = self.children.index(item.parent)
        widget_type = str(item.parent.__self__)

        # Make Title one always in first position
        if index == len(self.children) -2 and up_or_down == "up":
            return

        if "TextFieldBox" in widget_type:
            old_text = item.parent.ids._notefield_text.text
            new_widget = TextFieldBox()
            new_widget.ids._notefield_text.text = old_text

        elif "TitleFieldBox" in widget_type:
            old_text = item.parent.ids._notefield_title.text
            new_widget = TitleFieldBox()
            new_widget.ids._notefield_title.text = old_text

        elif "RstBox" in widget_type:
            old_text = item.parent.ids._rst_note.text
            new_widget = RstBox(text = old_text)

        elif "Separator" in widget_type:
            new_widget = SeparatorBox()

        elif "Picture" in widget_type:
            new_widget = PictureBox(source = item.parent.source)

        self.remove_widget(item.parent)

        if up_or_down == "down":
            self.move_down_item(new_widget, index)
        else:
            self.move_up_item(new_widget, index)

    def move_down_item(self, item, n):
        self.add_widget(item, n-1)

    def move_up_item(self, item, n):
        self.add_widget(item, n+1)

class TitleFieldBox(MDBoxLayout):
    title = StringProperty()

class PictureBox(MDBoxLayout):
    source = StringProperty()
    
class SeparatorBox(MDBoxLayout):
    pass

class TextFieldBox(MDBoxLayout):
    text = StringProperty()

class RstBox(MDBoxLayout):
    text = StringProperty()

class ScreenRstEdit(MDScreen):
    code_h = NumericProperty(dp(0))
    rst_h = NumericProperty(dp(0))
    pad = NumericProperty(dp(0))

    def on_kv_post(self, base_widget):
        self.pad = self.ids._rst_edit_box.padding[1] * 2
        self.code_h = Window.height - self.pad

    def backdrop(self):
        ''' triggered when user press on the arrow down bold, from screen rst edit
        allow user to see the rst rendering result '''
        if self.rst_h > self.code_h: 
            self.code_h = self.height - self.pad
            self.rst_h = self.pad
        else: 
            self.rst_h = self.height - self.pad
            self.code_h = self.pad

class NoteField(MDTextField):
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        
    def on_touch_down(self, touch): # here touch is a parameter that contains useful information like coordinates
        edit_mode = self.app.manager.screenEditNote.ids["_note_box"].edit_mode

        if self.collide_point(touch.x, touch.y):
            if edit_mode:
                return super(NoteField,self).on_touch_down(touch)
            else:
                return

    def on_triple_tap(self):
        self.focus = True
        Clock.schedule_once(lambda dt: self.select_all())

class DialogNoteContent(MDBoxLayout):
    pass

class NoteStackLayout(MDStackLayout):
    pass

class ItemIconButton(FloatLayout):
    icon_color = ListProperty()

class ItemIconButtonPicture(FloatLayout):
    icon_color = ListProperty()

class MyRstDocument(RstDocument, TouchBehavior):
    app = ObjectProperty()
    rst_edition = BooleanProperty(False)
    rst_edited = ObjectProperty()

    def on_kv_post(self, w):
        self.app = MDApp.get_running_app()
        self.content.padding = 0
        self.colors['paragraph']= self.app.rstbox_paragraph_color
        self.colors["title"]= self.app.rstbox_title_color
        self.colors["bullet"]= self.app.rstbox_bullet_color
        self.colors["background"]= self.app.rstbox_background_color

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):

            edit_mode = self.app.manager.screenEditNote.ids["_note_box"].edit_mode
            if touch.is_double_tap and edit_mode:
                if not self.app.manager.screen_rst_edit_loaded:
                    self.app.manager.load_rst_edit_screen()
                self.rst_edition = True
                self.rst_edited = self
                self.app.manager.screenRstEdit.ids._textinput_edit.text = self.text
                self.app.manager.screenRstEdit.ids._rst_document.rst_edition = True
                self.app.manager.screenRstEdit.ids._rst_document.rst_edited = self
                self.app.manager.screenEditNote.next_screen = "screen rst edit"
                self.app.manager.current = "screen rst edit"
        return super().on_touch_down(touch)

'''##################################################################################
                                Classes Speed
##################################################################################'''

class MyMDFloatingActionButton(RotateBehavior, MDFloatingActionButton):
    ''' Action Button to let the user select the diferent Note Items like TextBox or PictureBox'''
    
    opacity_button = NumericProperty(0)
    opening_time_button_rotation = NumericProperty(0.2)
    opening_transition_button_rotation = StringProperty("out_cubic")
    rotate_value_angle = NumericProperty(0)
    disabled_speed = BooleanProperty(True)
    speed_active = BooleanProperty(False)
    app = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def open_speed(self):
        """Called when a stack is opened."""
        self.app.manager.screenEditNote.ids._note_box.opacity = 0.2
        self.speed_active = True
        Animation(
            rotate_value_angle= 90,
            d=self.opening_time_button_rotation,
            t=self.opening_transition_button_rotation,
            ).start(self)
        
        self.icon = "minus"
        self.opacity_button = 1
        self.disabled_speed = False

    def close_speed(self):
        self.speed_active = False
        if self.icon == "minus":
            self.app.manager.screenEditNote.ids._note_box.opacity = 1
            Animation(
                rotate_value_angle= -90,
                d=self.opening_time_button_rotation,
                t=self.opening_transition_button_rotation,
                ).start(self)
            
            self.icon = "plus"
            self.opacity_button = 0
            self.disabled_speed = True

'''##################################################################################
                                Custom straightforward Widgets
##################################################################################'''

class AddRecipeField(MDTextField):

    def on_kv_post(self,widget):
        '''added to mimic a focus click otherwise when field is empty the line_color_normal is not set'''
        if not self.text :
            Clock.schedule_once(partial(MDApp.get_running_app().delay_focus_true, self), 0)
    
    def on_triple_tap(self):
        self.focus = True
        Clock.schedule_once(lambda dt: self.select_all())

class ClickableTextField(MDRelativeLayout):
    hint_text = StringProperty()
    helper_text = StringProperty()
    icon_color = ListProperty()
    text_color_normal = ListProperty()
    hint_text_color_normal  = ListProperty()
    helper_text_color_normal = ListProperty()
    line_color_normal = ListProperty()
    helper_text_color_focus = ListProperty()

    def on_kv_post(self,widget):
        '''added to mimic a focus click otherwise when field is empty the line_color_normal is not set'''
        if not self.ids._ingredient_field.text:
            Clock.schedule_once(partial(MDApp.get_running_app().delay_focus_true, self.ids._ingredient_field), 0)

class ConfigBoxField(MDBoxLayout):
    label_hint_x_config = NumericProperty()
    field_hint_x_config = NumericProperty()
    label_text_config = StringProperty("")
    input_text_config = StringProperty("")
    function_code_config = StringProperty("")
    input_filter = ObjectProperty(None, allownone=True)

class ConfigBoxButton(MDBoxLayout):
    label_hint_x_config = NumericProperty()
    button_hint_x_config = NumericProperty()
    label_text_config = StringProperty("")
    button_text_config = StringProperty("")
    function_code_config = StringProperty("")

class ConfigBoxSegmented(MDBoxLayout):
    label_text_config = StringProperty("")

class DisabledField(MDTextField):
    ''' fake disabled textfield to get the right text color 
    otherwise it is set to disabled default value'''

    def on_touch_down(self, touch):
        return

'''##################################################################################
                                Custom Complex Widgets
##################################################################################'''

class MyMDSmartTile(MDSmartTile):
    text = StringProperty()
    app = ObjectProperty()
    description = StringProperty()
    ingredients = ListProperty()
    source_recette = StringProperty()
    astuces = StringProperty()
    commentaire = StringProperty()
    nb_personne = StringProperty()
    saison = StringProperty()
    index_picture = StringProperty()
    tile_screen = StringProperty()
    ingredient_missing = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def on_release(self):
        ''' Passage des info de Tile A1, A2, A3, A4 à Tile A0  '''

        source = join("images", "recipes", self.index_picture+".jpg")

        if self.app.manager.current in ["screen A1", "screen A2", "screen A3", "screen A4"]:
            self.app.manager.tile_mother_manager = self
            if self.opacity :
                self.app.manager.screenA0.tile_A0.text = self.text
                self.app.manager.screenA0.tile_A0.description = self.description
                self.app.manager.screenA0.tile_A0.ingredients = self.ingredients
                self.app.manager.screenA0.tile_A0.index_picture = self.index_picture
                self.app.manager.screenA0.tile_A0.source_recette = self.source_recette
                self.app.manager.screenA0.tile_A0.astuces = self.astuces
                self.app.manager.screenA0.tile_A0.nb_personne = self.nb_personne
                self.app.manager.screenA0.tile_A0.saison = self.saison
                self.app.manager.screenA0.tile_A0.commentaire = self.commentaire
                self.app.manager.screenA0.tile_A0.ingredient_missing = self.ingredient_missing

                # set A0 ingredient markup text
                self.app.set_a0_ingredient_text(self.app.manager.screenA0.tile_A0)

                if exists(source): 
                    self.app.manager.screenA0.tile_A0.ids.image.source = source # $source runtime added to solve bug image not showing
                    self.app.manager.screenA0.tile_A0.ids.image.reload()
                else:
                    self.app.manager.screenA0.tile_A0.ids.image.source = source_image_default # $source runtime
                    self.app.manager.screenA0.tile_A0.ids.image.reload()
                
                log(" tile A1 width is : " + str(self.width))
                log(" tile A1 height is : " + str(self.height))
                self.app.manager.edit_full_screen()
                self.app.manager.transition.direction = "up"
                self.app.manager.current = "screen A0"

class SearchField(MDTextField):
    starting_no = NumericProperty(3)
    app = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def on_text(self, instance, value):
        def filter_recipe(index, recipe, grid):
            #find all the occurrence of the word
            if index == 2:
                # check number recipe and set 10 if more than 10 recipes
                if len(recipe) > 10:
                    len_recipe = 10
                else:
                    len_recipe = len(recipe)

            elif index == 3:
                if recipe:
                    len_recipe = len(recipe)
                else:
                    len_recipe = 0
            else:
                len_recipe = len(recipe)

            if len(value) > self.starting_no and len_recipe > 5 : # value = self.text
                #0 Check if enough recipes so we can return 5 string matches:
                nb_result = self.app.nb_recipe_returned(5)
                #1 Get matches dictionnary
                matches = home_made(recipe, value, nb_result) # return dictionnary with 5 keys

                #2 Replace SmartTiles content
                n = 1
                for key in matches.keys():
                    instruction = matches[key]["description"]
                    title = matches[key]['title']
                    ingredients = matches[key]['ingredients']
                    commentaire = matches[key]['commentaire']
                    nb_personne = matches[key]["nombre de personne"] if "nombre de personne" in matches[key] else ""
                    saison = matches[key]["saison"] if "saison" in matches[key] else ""
                    astuces = matches[key]['astuces']
                    source_recette = matches[key]['source']

                    self.app.replace_tile(grid.children[-n], key, instruction, title,
                                                         ingredients, commentaire, nb_personne, saison, astuces, source_recette)
                    n+=1
                for i in range(n, len_recipe + 1):
                    grid.children[-i].opacity = 0

                grid.parent.scroll_y = 1
            
            # case user delete all textfield entries
            if len(value) == 0 and len_recipe > 5:
                if index == 2:
                    self.app.manager.screenA3.ids._tabs.replace_tiles()
                else:
                    n = 1
                    for key in recipe.keys():
                        instruction = recipe[key]["description"]
                        title = recipe[key]["title"]
                        ingredients = recipe[key]["ingredients"]
                        commentaire = recipe[key]["commentaire"]
                        nb_personne = recipe[key]["nombre de personne"] if "nombre de personne" in recipe[key] else ""
                        saison = recipe[key]["saison"] if "saison" in recipe[key] else ""
                        astuces = recipe[key]["astuces"]
                        source_recette = recipe[key]["source"]

                        self.app.replace_tile(grid.children[-n], key, instruction, title,
                                                             ingredients, commentaire, nb_personne, saison, astuces, source_recette)
                        n+=1
                grid.parent.scroll_y = 1

        def filter_notes():
            ''' find all the occurrence of the word, the home made function can be improved, but 
            we use it because it is much more faster than other founded doing a benchmark. '''
            
            notes_number = len(self.app.manager.screenC1.ids["_selection_list"].notes_list)
            if len(value) > self.starting_no and notes_number > 5: # value = self.text
                self.app.manager.screenC1.ids["_selection_list"].matches = home_made(note_data,value,6)
                self.app.manager.screenC1.ids["_selection_list"].notes_filter()
            # case user delete all textfield entries
            if len(value) == 0:
                self.app.manager.screenC1.ids["_selection_list"].notes_unfilter()

        if self.app.manager.current[:-1] == "screen A":
            index = self.app.manager.index # index 0 == grid1, 1 == grid2

            match index:
                case 0:
                    filter_recipe(0, recipes[0], self.app.manager.screenA1.ids._grid1)
                case 1:
                    filter_recipe(1, recipes[1], self.app.manager.screenA2.ids._grid2)
                case 2:
                    filter_recipe(2, recipes[2], self.app.manager.screenA3.ids._grid3)
                case 3:
                    filter_recipe(3, self.app.rv_ingredient_dic, self.app.manager.screenA4.ids._rvgrid) # here recipe[3] depends on if an ingredient research os operating

        elif self.app.manager.current == "screen C1":
            filter_notes()

    def on_triple_tap(self):
        self.focus = True
        Clock.schedule_once(lambda dt: self.select_all())

class RV(MDBoxLayout):
    first_research = BooleanProperty(True)
    last_research_len = NumericProperty(0)
    rvbox = ObjectProperty() # RV parent needed for RVMDLabel
    rvscroll = ObjectProperty()
    markup_label_a4 = ObjectProperty()
    markup_label_b1 = ObjectProperty()
    rvtextfield = ObjectProperty()
    app = ObjectProperty()
    name = StringProperty()

    def on_kv_post(self, widget):
        ''' added here with a, b. c because in kv lang and in python we had error f-string: unmatched "[" 
        condition if was added to avoid doing twice the declaration for each RV instances'''
        
        self.app = MDApp.get_running_app()

        if self.name == "rv_a4":
            a = self.app.current_lang["markup"][0]
            b = self.app.current_lang["markup"][1]
            c = self.app.current_lang["markup"][2]
            self.markup_label_a4.text =  f"[size=24sp] [color=#4c79ffff][b]{a}[i][size=42sp][sub][color=#ff65d8ff]{b}[/color][/sub][/size][/i]{c}[/color][/size]"
            
        elif self.name == "rv_b1":
            d = self.app.current_lang["markup"][3]
            e = self.app.current_lang["markup"][4]
            f = self.app.current_lang["markup"][5]
            self.markup_label_b1.text =  f"[size=24sp] [color=#4c79ffff][b]{d}[i][size=42sp][sub][color=#ff65d8ff]{e}[/color][/sub][/size][/i]{f}[/color][/size]"

    def load_data(self, data):
        self.clear_widgets()
        for ingredient in data:
            self.add_widget(RVMDLabel(text = ingredient['text']))

class RVMDLabel(MDLabel):
    ''' Class that deals the ingredient choice within the three screens cases A4, A5, B1
    Parent : rv '''
    app = ObjectProperty()
    
    def __init__(self,**args):
        super().__init__(**args)
        self.markup = True
        self.app = MDApp.get_running_app()

    def label_click(self, w, touch):
        ''' iterate threw all ingredients selected in RV so 
        self.text must be inside collide_point'''

        if w.collide_point(*touch.pos):
            current_screen = self.app.manager.current
            self.app.last_ingredient_filtered = self.text
            self.parent.rvtextfield.changed_by_click = True
            self.parent.rvtextfield.text = "" # reset textfield text
            Clock.schedule_once(self.reset_changed_by_click, 0.1)

            if current_screen == "screen A4": # case when filtering recipes by ingredient
                self.app.manager.screenA4.search_by_ingredient_triggered = True
                self.app.manager.screenA4.last_ingredient_searched = self.text
                
                self.populate_rvgrid(self.text)
                a = self.app.current_lang["markup"][0]
                b = self.app.current_lang["markup"][1]
                c = self.app.current_lang["markup"][2]
                d = c + "\n"

                # change title markup
                if len(self.text) <7 :
                    self.parent.markup_label_a4.text = f"[size=24sp] [color=#4c79ffff][b]{a}[i][size=42sp][sub][color=#ff65d8ff]{b}[/color][/sub][/size][/i]{c}[/color][/size] [size=24sp][i][color=#ff65d8ff]{self.text}[/color][/b][/i][/size]" # \\n
                else:
                    self.parent.markup_label_a4.text = f"[size=24sp] [color=#4c79ffff][b]{a}[i][size=42sp][sub][color=#ff65d8ff]{b}[/color][/sub][/size][/i]{d}[/color][/size] [size=24sp][i][color=#ff65d8ff]{self.text}[/color][/b][/i][/size]" # \\n
            
            if current_screen == "screen A5":
                self.app.manager.screenA5.stack_a5.add_ingredient(self.text) # add button ingredient to stack
            
            if current_screen == "screen B1":
                self.app.manager.screenB1.ids._stack_b1.add_ingredient(self.text) # add button ingredient to stack

            self.restore_rv()

    def restore_rv(self):
        # change height and clear RV
        self.parent.text = ""
        self.parent.canvas.opacity = 0
        Clock.schedule_once(self.resize, 0.1)
    
    def resize(self, value):
        self.parent.height = 1 # ensure the height is ok

    def populate_rvgrid(self,txt):
        ingredient_recipes = recipes[3][txt]
        nb_tiles_wanted = len(ingredient_recipes)

        self.app.dic_old_a4_tiles = ingredient_recipes
        self.app.nb_old_a4_tiles = str(nb_tiles_wanted)
        
        # create the invisible tiles for the ingredient search, tags are dinamically created, after instanciation
        nb_tiles_current = len(self.app.manager.screenA4.ids._rvgrid.children)
        if nb_tiles_wanted > nb_tiles_current:
            diff = nb_tiles_wanted - nb_tiles_current
            self.app.manager.create_invisible_a4_tile(diff)

        self.app.rv_ingredient_dic = recipes[3][txt] # needed for filter
        n=1

        for key in ingredient_recipes.keys():
            instruction = ingredient_recipes[key]["description"]
            title = ingredient_recipes[key]["title"]
            ingredients = ingredient_recipes[key]["ingredients"]
            commentaire = ingredient_recipes[key]["commentaire"]
            nb_personne = ingredient_recipes[key]["nombre de personne"] if "nombre de personne" in ingredient_recipes[key] else ""
            saison = ingredient_recipes[key]["saison"] if "saison" in ingredient_recipes[key] else ""
            astuces = ingredient_recipes[key]["astuces"]
            source_recette = ingredient_recipes[key]["source"]

            self.app.replace_tile(self.parent.rvbox.rvgrid.children[-n], key, 
                                                 instruction, title, ingredients, 
                                                 commentaire, nb_personne, saison, astuces, source_recette)
            n+=1

        # Make Tiles tags not visible from previous search : 
        if not self.parent.first_research: # parent RV
            if len(ingredient_recipes) < self.parent.last_research_len:
                for n in range(len(ingredient_recipes) + 1, self.parent.last_research_len + 1):
                    self.parent.rvbox.rvgrid.children[-n].opacity = 0
 
        self.parent.last_research_len = len(ingredient_recipes)
        self.parent.first_research = False
        self.parent.rvscroll.scroll_y = 1
        
    def reset_changed_by_click(self,dt):
        self.parent.rvtextfield.changed_by_click = False # needed otherwise the RV data changes

class RVMDBoxLayout(MDBoxLayout):
    ''' BoxLayout used in screen A4, A5, B1. to resize the RV widget '''

    rv = ObjectProperty()
    rvgrid = ObjectProperty()
    app = ObjectProperty()

    def on_touch_down(self, touch):
        ''' Clear Data and Resize RV on touch outside '''

        if not self.rv.collide_point(*touch.pos):
            self.rv.text = ""
            self.rv.canvas.opacity = 0
            Clock.schedule_once(self.resize, 0.1)
            
        return super(RVMDBoxLayout, self).on_touch_down(touch)
    
    def resize(self, value):
        self.rv.height = 1 # ensure the height is ok

class RVMDTextField(MDTextField):
    ''' field where user can search text and match the text with 
    ingredients database. IngredientSearchField A4-A5-B1. '''

    rv = ObjectProperty()
    suggestion_text = ''
    changed_by_click = BooleanProperty(False)
    app = ObjectProperty()

    def on_kv_post(self,widget):
        '''added to mimic a focus click otherwise when field is empty the line_color_normal is not set'''
        
        self.app = MDApp.get_running_app()
        if not self.text:
            Clock.schedule_once(partial(self.app.delay_focus_true, self), 0)

    def on_text(self, instance, value):
        ''' string comparison better for value < 4 find all the occurrence of the word '''
        
        if value == "":
            self.rv.opacity = 0
            self.rv.canvas.opacity = 0
            self.rv.height = 1

        else:
            self.suggestion_text = value
            self.rv.opacity = 1
            self.rv.canvas.opacity = 1

            nb_result = 6
            nb_matches = self.app.nb_recipe_returned(nb_result)
            matches = home_made(recipes[4],value, nb_matches)

            # display the data in the recycleview
            if not self.changed_by_click: # needed to not change the data rv when comes from click
                display_data = []
                for i in matches:
                    display_data.append({'text':i})

            # ensure the size is okay
            # Warning minimum heigth is required to detect click smoothly
            self.rv.height = Window.height/3 - 20

            # display the data
            if not self.changed_by_click: # needed to not change the data rv when comes from click
                self.rv.load_data(display_data)

            # create the invisible tiles for the A4 screen, why here, to optimise time response
            self.app.optimize_loading_A4_screen(5)

    def on_triple_tap(self):
        self.focus = True
        Clock.schedule_once(lambda dt: self.select_all())

class SaveRecipeButton(MDRectangleFlatIconButton):
    app = ObjectProperty()
    required_field = ['_title_field', '_instruction_field']
    required_field_completed = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
    
    def on_release(self):
        # 1. Check if there is another recipe with same title : 
        if not self.app.A5_edition : 
            for recette in recipes[2].values():
                if self.app.manager.screenA5.ids["_title_field"].text == recette["title"]:
                    self.app.manager.screenA5.ids["_title_field"].error = True
                    self.app.manager.screenA5.ids._rvscroll_a5.scroll_y = self.app.manager.screenA5.ids["_title_field"].y / self.app.manager.screenA5.ids._rvbox_a5.height
                    return toast(self.app.current_lang["toast"][0])
        

        # 2. ensure that all required field are filled
        for field in self.required_field:
            if self.app.manager.screenA5.ids[field].text == "" :
                self.app.manager.screenA5.ids[field].error = True 
                self.app.manager.screenA5.ids._rvscroll_a5.scroll_y = self.app.manager.screenA5.ids[field].y / self.app.manager.screenA5.ids._rvbox_a5.height
                self.required_field_completed = False
                return toast(self.app.current_lang["toast"][1])

        # 3. ensure ingredient stack is not empty :
        # and check if new ingredient and add it to dico that stores all ingredients
        ingredients = []
        
        for ingredient in self.app.manager.screenA5.ids._stack_a5.children :
            ingredients.append(ingredient.text)
            if ingredient not in recipes[4]:
                recipes[4][ingredient] = {"title": str(ingredient)}

        if ingredients == []:
            self.app.manager.screenA5.ids["_ingredient_search_a5"].ids._rv_textfield.error = True
            self.app.manager.screenA5.ids["_rvscroll_a5"].scroll_y = self.app.manager.screenA5.ids["_stack_a5"].y / self.app.manager.screenA5.ids["_rvbox_a5"].height
            self.required_field_completed = False
            return toast(self.app.current_lang["toast"][2])

        self.required_field_completed = True

        # 4. Store the new recipe
        if self.app.A5_edition : 
            key = self.app.manager.screenA0.tile_A0.index_picture
        else:
            key = str(len(recipes[2])+1)

        title = self.app.manager.screenA5.ids._title_field.text
        instruction = self.app.manager.screenA5.ids._instruction_field.text
        source_recette = self.app.manager.screenA5.ids._source_field.text
        astuces = self.app.manager.screenA5.ids._astuce_field.text
        commentaire = self.app.manager.screenA5.ids._commentaire_field.text
        nb_personne = self.app.manager.screenA5.ids._nb_personne_field.text
        type = self.app.manager.screenA5.ids.type_field.text

        # not tested on all $platform, aded to solved image not found issue on windows
        source = join(".","images","recipes", key) + ".jpg"

        new_recipe = {"key": key,
                       "title" : title,
                       "description": instruction,
                       "source": source_recette,
                       "source_type": "Texte",
                       "ingredients": ingredients,
                       "astuces": astuces,
                       "commentaire": commentaire,
                       "nombre de personne": nb_personne,
                       "type": type}

        if not self.app.A5_edition :
            toast(self.app.current_lang["toast"][3])

        recettes["recipes"][key] = new_recipe

        # 5. Save to private
        json_recettes = json_dumps(recettes, ensure_ascii=False, indent= 4)
        with open(join("core","input_recettes.py"), 'w',encoding='utf-8') as f:
            f.write("recettes = " + str(json_recettes))

        # 6. Save to shared for android
        source_shared = join("core","input_recettes.py")
        self.app.save_to_shared(source_shared, join("data", "input_recettes.py"))
        
        # 7. Check Files names
        if platform in ["android", "ios"]:
            dir = "data"
            self.app.checkfilename(dir)

        # 8. Reload core recipes
        self.app.reload_core()

        # 9. reload A1 A2 A3 A4 and max_ingredient and A0
        # A1 : check if new recipe ingredient match with ingredient screen B1
        stack_list = [ing for ing in mydico_frigo["ingredients"].keys()]
        missing = []
        for ingredient in ingredients:
            if ingredient not in stack_list:
                missing.append(ingredient)
        
        # new recipe
        if len(missing) == 0 and not self.app.A5_edition:
            self.app.manager.screenA1.ids._grid1.add_widget(
                MyMDSmartTile(
                    text= title, description = instruction, ingredients = ingredients, 
                    commentaire = commentaire, nb_personne = nb_personne, astuces = astuces, 
                    source_recette = source_recette, index_picture = key, tile_screen = "screen A1", 
                    source = source))
        
        # edit recipe
        if self.app.A5_edition :
            for children in self.app.manager.screenA1.ids._grid1.children:
                if key == children.index_picture:
                    children.text = title
                    children.description = instruction
                    children.source_recette = source_recette
                    children.astuces = astuces
                    children.commentaire = commentaire
                    children.nb_personne = nb_personne
                    children.ingredients = ingredients

            # Reload screens A1
            self.app.manager.reload_recipes_screens(["screen A1"])
            
        # A2
        # new recipe 
        elif len(missing) == 1 and not self.app.A5_edition:
            self.app.manager.screenA2.ids._grid2.add_widget(
                MyMDSmartTile(
                    text= title, commentaire = commentaire, nb_personne = nb_personne,
                    astuces = astuces, source_recette = source_recette,
                    description = instruction, ingredients = ingredients, 
                    index_picture = key, tile_screen = "screen A2", source = source))
            
        # edit recipe can be factorise
        if self.app.A5_edition :
            for children in self.app.manager.screenA2.ids._grid2.children:
                if key == children.index_picture:
                    children.text = title
                    children.description = instruction
                    children.source_recette = source_recette
                    children.astuces = astuces
                    children.commentaire = commentaire
                    children.nb_personne = nb_personne
                    children.ingredients = ingredients
 
        # we reload screen A2 in case the missing ingredient was deleted
            self.app.manager.reload_recipes_screens(["screen A2"])

        # A3
        if self.app.A5_edition :
            for children in self.app.manager.screenA3.ids._grid3.children:
                if key == children.index_picture:
                    children.text = title
                    children.description = instruction
                    children.source_recette = source_recette
                    children.astuces = astuces
                    children.commentaire = commentaire
                    children.nb_personne = nb_personne
                    children.ingredients = ingredients

        else:
            nb_tabs = len(self.app.manager.screenA3.ids._tabs.tab_bar.layout.children)

            if len(recipes[2]) % 10 != 1:
                # reload last tabs if cursor in last tab
                if self.app.manager.screenA3.ids._tabs.current_tab == nb_tabs-1 :
                    self.app.manager.screenA3.ids._tabs.replace_tiles()
                # else : no need for else because when moving to another tab, replace tiles method will reload the new tile
                
            else : 
                # create new tab and add it to this new tab
                self.app.manager.screenA3.ids._tabs.add_widget(Tab(title=str(nb_tabs)))

        # A4, reload max_ingredient
        last_max_ingredient = config_input["max_ingredient"]
        config_input["ingredient_max_calcul"] = False
        global max_ingredient
        max_ingredient = ingredient_max_calcul(config_input, recipes)

        if not self.app.manager.screen_a4_loaded: 
            self.app.manager.load_A4_screen()

        n = max_ingredient - last_max_ingredient
        if n > 0:
            # add the invisible Tiles to screen A4
            for i in range(n):
                RVTile = MyMDSmartTile(text = "", commentaire = "", nb_personne = "", saison = "", 
                                        astuces = "", source_recette = "",
                                        description = "", ingredients = [], 
                                        index_picture = "", tile_screen = "screen A4", 
                                        source = source_image_default,
                                        opacity = 0
                                        )
                self.app.manager.screenA4.ids._rvgrid.add_widget(RVTile)

        # Check if text in rvtextfield and repopulate rvgrid both edition and new recipe are same logic
        rvtextfield = self.app.manager.screenA4.last_ingredient_searched
        screen = self.app.appbar.current_nav_screen
        previous_screen = screen + str(self.app.manager.index+1)

        if self.app.manager.screenA4.search_by_ingredient_triggered and rvtextfield != "" :
            # rvtextfield = "" can lead to key error
            new_number_tiles_A4 = str(len(recipes[3][rvtextfield]))
            
            # 1. repopulate if new number recipes different than tiles number
            if new_number_tiles_A4 != self.app.nb_old_a4_tiles:
                self.app.manager.screenA4.ids._rv_a4.children[0].populate_rvgrid(rvtextfield) # select one of the rvlabel

            # 2. repopulate if screen A4, even if there were no changes (too lazy to code that one)
            if previous_screen == "screen A4":
                self.app.manager.screenA4.ids._rv_a4.children[0].populate_rvgrid(rvtextfield) # select one of the rvlabel

            # 3. repopulate if not in screen A4 and tiles changed in tiles A4.
            if previous_screen != "screen A4" and key in self.app.dic_old_a4_tiles:
                self.app.manager.screenA4.ids._rv_a4.children[0].populate_rvgrid(rvtextfield) # select one of the rvlabel

        # reload A0 # only in edition mode
        if self.app.A5_edition :
            self.app.manager.screenA0.tile_A0.text = title # On passe le text de la Tile A à la Tile B
            self.app.manager.screenA0.tile_A0.description = instruction
            self.app.manager.screenA0.tile_A0.ingredients = ingredients
            self.app.manager.screenA0.tile_A0.source_recette = source_recette
            self.app.manager.screenA0.tile_A0.astuces = astuces
            self.app.manager.screenA0.tile_A0.commentaire = commentaire
            self.app.manager.screenA0.tile_A0.nb_personne = nb_personne
             
            if exists(source): 
                self.app.manager.screenA0.tile_A0.ids.image.source = source #$source runtime added to solve bug image not showing
                self.app.manager.screenA0.tile_A0.ids.image.reload()
            else:
                self.app.manager.screenA0.tile_A0.ids.image.source = source_image_default #$source runtime
                self.app.manager.screenA0.tile_A0.ids.image.reload()
        
        # 10. Empty all fields
        if not self.app.A5_edition :
            self.app.manager.screenA5.reset_recipe_items()

'''##################################################################################
                                Custom Complex Layouts
##################################################################################'''

class MyMDStackLayout(MDStackLayout):
    stack_list_B1 = []
    stack_list_A5 = []
    current_screen = StringProperty("")
    app = ObjectProperty()

    def on_kv_post(self,widget):
        self.app = MDApp.get_running_app()
        self.populate_stack()

    @mainthread
    def populate_stack(self):
        # only populate for screen B1 and screen D (load input_frigo file) (because there are several instances)
        if self.current_screen in ["screen B1","screen D4"]: 
            #1 append ing in stack list
            for ing in mydico_frigo["ingredients"].keys():
                self.stack_list_B1.append(ing)
            
            #2 sort stack list
            self.stack_list_B1.sort()

            #3 populate the stack layout
            for ing in self.stack_list_B1:
                self.add_widget(MyMDFillRoundFlatIconButton(text = ing, font_size = self.app.font_size_button_ingredient))

    @mainthread
    def delete_ingredient(self, button):
        current_screen = self.app.manager.current
        self.remove_widget(button)
        if current_screen == "screen B1":
            self.stack_list_B1.remove(button.text)
            del mydico_frigo["ingredients"][button.text]
            Clock.schedule_once(self.actualize_recipe, 0)
            
        if current_screen == "screen A5":
            self.stack_list_A5.remove(button.text)
            self.app.manager.screenA0.tile_A0.ingredients.remove(button.text)

    @mainthread
    def add_ingredient(self,ing): # n beeing the node
        ''' here mainthread is needed otherwise changes are not made to the screen when coming from A0 to A5 '''
        current_screen = self.app.manager.current

        if current_screen in ["screen B1", "screen D4"]:
            if ing not in self.stack_list_B1:
                # calculate index by inserting ing to stack list at the right place
                index = len(self.stack_list_B1) - self.insert_sorted(self.stack_list_B1, ing)
                self.add_widget(MyMDFillRoundFlatIconButton(text = ing, font_size = self.app.font_size_button_ingredient), index)
                # self.add_widget(MyMDFillRoundFlatIconButton(text = ing, font_size = self.app.font_size_button_ingredient), index, canvas = "after")

            if ing not in mydico_frigo["ingredients"] :
                mydico_frigo["ingredients"][ing] = "ingredient"
                Clock.schedule_once(self.actualize_recipe, 0.4)
                
        if current_screen == "screen A5": 
            ''' here in A5 the core is not reload in case of new 
            ingredient no need to, it will be reload next session '''
            
            if ing not in self.stack_list_A5:
                index = len(self.stack_list_A5) - self.insert_sorted(self.stack_list_A5, ing)
                self.add_widget(MyMDFillRoundFlatIconButton(text = ing, font_size = self.app.font_size_button_ingredient), index)
            
            # edit ingredients list in tile_A0
            if ing not in self.app.manager.screenA0.tile_A0.ingredients:
                self.app.manager.screenA0.tile_A0.ingredients.append(ing)

    @mainthread
    def actualize_recipe(self, dt):
        # used when adding or removing ingredient to stack, A1 and A2 screen involved
        json_mydico_frigo = json_dumps(mydico_frigo, ensure_ascii=False, indent= 4)
        
        with open(join("core","input_frigo.py"), 'w',encoding='utf-8') as f:
            f.write("mydico_frigo = " + str(json_mydico_frigo))

        self.app.reload_core()
        self.app.manager.reload_recipes_screens(["screen A1", "screen A2"])
        
    def insert_sorted(self,lst, s):
        lst.append(s)
        i = len(lst) - 1
        while i > 0 and lst[i] < lst[i-1]:
            lst[i], lst[i-1] = lst[i-1], lst[i]
            i -= 1
        return i

    @mainthread
    def delete_all_stack(self):
        # not pretty but to avoid clearing widget and not clearing list
        if self.current_screen in ["screen B1", "screen D4"]:
            self.clear_widgets()
            self.stack_list_B1 = []
        if self.current_screen == "screen A5":
            self.clear_widgets()
            self.stack_list_A5 = []

'''##################################################################################
                                Custom Icons Widgets
##################################################################################'''

class GoBackIconButton(MDIconButton):
    ''' go back from screen A0 to screen AX. '''
    app = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def on_release(self):
        self.app.manager.transition.direction = "down"
        screen = self.app.appbar.current_nav_screen
        self.app.manager.restore_screen()
        self.app.manager.current = screen + str(self.app.manager.index+1)

class UnselectNoteIcon(MDIconButton):
    pass

class CloseIconButton(MDIconButton):
    ''' added to allow color icon changes in kv and not in python'''
    pass

class IngredientSearchField(MDRelativeLayout):
    rv = ObjectProperty()
    rvtextfield = ObjectProperty()

class MyMDFillRoundFlatIconButton(MDFillRoundFlatButton):
    def on_press(self):
        self.parent.delete_ingredient(self)

'''##################################################################################
                                Classes Settings
##################################################################################'''

class SettingsField(MDTextField):
    ''' This was added because of the unexpected behavior when declared in kv,
    on_triple_tap highlight all the sequence but when deleting, only deleting 1 character.. '''

    def on_triple_tap(self):
        self.focus = True
        Clock.schedule_once(lambda dt: self.select_all())

class FakeTouch(object):
    '''needed because active prop MDSegmentedControl not working
    so we fake a touch'''
    pass

class MyMDSegmentedControl(MDSegmentedControl):
    def on_kv_post(self, base_widget):
        self.ids.segment_panel.width = dp(80)
    
    # because self.active not changing the buttons' color, we fake a touch, mainthread is needed here
    @mainthread
    def fake_active(self, option, dt):
        app = MDApp.get_running_app()
        if option == "color":
            active = config_input["default_theme"]
            match active:
                case "Blue":
                    sci = app.manager.screenD1.ids._sci_blue
                case "White":
                    sci = app.manager.screenD1.ids._sci_white
                case "Black":
                    sci = app.manager.screenD1.ids._sci_black
        else:
            active = config_input["language"]
            match active:
                case "French":
                    sci = app.manager.screenD1.ids._sci_french
                case "English":
                    sci = app.manager.screenD1.ids._sci_english

        sci.active = True
        self.current_active_segment = sci
        touch = FakeTouch()
        touch.x = sci.center_x
        touch.y = sci.center_y

        self.on_press_segment(sci, touch)
        self.animation_segment_switch(sci)
        
class MyMDDialog(MDDialog):
    id_dialog = StringProperty("")

    def update_width(self, *args) -> None:
        self.width = Window.width - dp(80)

class MyColorPicker(ColorPicker):
    label_id = StringProperty("_unselected_note_color_field")
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
         
    def change_picker_color(self, color):
        match self.label_id:
            case "_unselected_note_color_field":
                self.app.unselected_note_color = color
                config_input["unselected_note_color"] = color
                self.app.manager.screenD2.ids._unselected_note_color_field.text = color
            case "_selected_note_color_field":
                self.app.selected_note_color = color
                config_input["selected_note_color"] = color
                self.app.manager.screenD2.ids._selected_note_color_field.text = color

        save_config(config_input)

    def check_text(self, text):
        ''' added to prevent ValueError in colorpicker inputtext when user
        writes non hexadecimal characters like $??& 
        In kivy master branch, that error was solved thanks to ElliotGarbus and Kuzeyron 
        '''
        import re
        regex_pattern = r"^[a-fA-F0-9#]+$"
        if not re.match(regex_pattern, text):
            return
        else:
            self._trigger_update_hex(text)

    def update_initial_hex(self,text, dt):
        ''' we had to clock this initial update because when loading screen picker kv just before
        setting picker hex, picker hex was not updated... so we found a trick to make it work'''
        self._trigger_update_hex(text)

class MyScatterPlane(ScatterPlane):
    ''' Source code from 
        https://stackoverflow.com/questions/59671570/how-to-zoom-on-a-particular-point-with-kivy-in-python
        Because it is not as good as Android Picture Viewer, 
        we only use Scatter if fail to connect to google Picture. '''   
 
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                if touch.button == 'scrolldown':
                    mat = Matrix().scale(.9, .9, .9)
                    self.apply_transform(mat, anchor=touch.pos)
                elif touch.button == 'scrollup':
                    mat = Matrix().scale(1.1, 1.1, 1.1)
                    self.apply_transform(mat, anchor=touch.pos)
        return super().on_touch_up(touch)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                if touch.button == 'scrolldown':
                    mat = Matrix().scale(.9, .9, .9)
                    self.apply_transform(mat, anchor=touch.pos)
                elif touch.button == 'scrollup':
                    mat = Matrix().scale(1.1, 1.1, 1.1)
                    self.apply_transform(mat, anchor=touch.pos)
        return super().on_touch_down(touch)

class DialogHelpContent(MDBoxLayout):
    text_content = StringProperty("")

class ItemConfirm(OneLineAvatarIconListItem):
    divider = None

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False

        MDApp.get_running_app().font_style_checkbox = self.text

'''##################################################################################
                                Class MDApp
##################################################################################'''

class CuistotDingoApp(MDApp):

    # Parent Widgets
    appbar = ObjectProperty()
    manager = ObjectProperty()
    navigation = ObjectProperty()

    rv_ingredient_dic = DictProperty()
    appname_callback = StringProperty("") # 
    last_ingredient_filtered = StringProperty("") # 
    load_action = StringProperty("recipes") # 
    A5_edition = BooleanProperty(False) # for screen direction purpose when user modify or create new recipe
    nb_old_a4_tiles = StringProperty()
    dic_old_a4_tiles = DictProperty()

    # Config props
    current_lang = DictProperty() # before DictProperty(lang_fr) but bug
    # current_lang = lang_fr # before DictProperty(lang_fr) but bug
    separator_padding_y = StringProperty(config_input["separator_padding_y"])
    font_style_menu = StringProperty(config_input["font_style_menu"])
    font_style_tile = StringProperty(config_input["font_style_tile"])
    font_size_nav = StringProperty(config_input["font_size_nav"])
    source_picture = StringProperty(source_image_default)
    current_fitimage = ObjectProperty()
    unselected_note_color = StringProperty(config_input["unselected_note_color"])
    selected_note_color = StringProperty(config_input["selected_note_color"])
    load_recipes_dialog = ObjectProperty()
    load_notes_dialog = ObjectProperty()
    font_style_checkbox = ""
    configbox = ObjectProperty()
    center_y_note_item = NumericProperty(config_input["center_y_note_item"])
    font_size_button_ingredient = 22 if platform in ["win","macos","linux","unknown"] else NumericProperty(float(config_input["ingredient_button"]))
    size_hint_appbar = NumericProperty(config_input["size_hint_appbar"])
    size_hint_navigation = NumericProperty(config_input["size_hint_navigation"])

    blue_tabs_text_color_active = [1, 1, 1, 1]
    blue_tabs_text_color_inactive = [1, 1, 1, 0.87]
    white_tabs_text_color_active = [0, 0, 0, 1]
    white_tabs_text_color_inactive = [0.0, 0.0, 0.0, 0.87]

    blue_rgba_theme = [0.12941176470588237, 0.5882352941176471, 0.9529411764705882, 1]
    black_rgba_default = [0,0,0,1]
    white_rgba_default = [1,1,1,1]
    black_rgba_80 = [0,0,0,0.8]
    black_rgba_68 = [0,0,0,0.68]
    white_rgba_80 = [1,1,1,.8]
    white_rgba_68 = [1,1,1,.68]
    white_rgba_38 = [1,1,1,.38]
    black_rgba_38 = [0,0,0,0.38]
    white_rgba = ColorProperty()
    
    text_label_color = ColorProperty([0,0,0,1])
    color_pink = ColorProperty([1.0, 0.396078431372549, 0.8470588235294118, 1.0]) # Not used for now  
    
    text_textfield_color_normal = ColorProperty([0, 0, 0, 1.0])  
    text_notefield_color_normal = ColorProperty([0, 0, 0, 1.0])  
    text_searchfield_color_normal = ColorProperty([1, 1, 1, 0.8])  
    text_searchfield_color_focus = ColorProperty([1, 1, 1, 0.8])  
    line_searchfield_color_normal = ColorProperty([1, 1, 1, 0])
    line_searchfield_color_focus = ColorProperty([1, 1, 1, 0.8]) 
    hint_searchfield_color_normal = ColorProperty([1, 1, 1, 0.8]) 

    hint_textfield_color = ColorProperty([0, 0, 0, 0.38])
    helper_textfield_color_normal = ColorProperty([1,1,1,0.68])
    helper_textfield_color_focus = ColorProperty([0,0,0,0.68])
    line_textfield_color_normal = ColorProperty([0,0,0,0.38])
    line_textfield_note_color_normal = ColorProperty([0.5, 0.5, 0.5, 1.0])
    line_textfield_color_focus = ColorProperty([0,0,0,0.38])

    close_textfield_icon_color = ColorProperty([1,1,1,1])

    # rstbox_paragraph_color = "202020ff"
    # rstbox_title_color = "204a87ff"
    # rstbox_bullet_color = "000000ff"
    # rstbox_background_color = "262730ff"

    rstbox_paragraph_color = "ffffffcc"
    rstbox_title_color = "204a87ff"
    rstbox_bullet_color = "000000ff"
    rstbox_background_color = "ffffffcc"

    separator_line_color = ColorProperty([0,0,0,0.38])
    item_icon_button_color = ColorProperty([0,0,0,1])
    unselect_icon_button_color = ColorProperty([1,1,1,0.8])
    speed_label_color = ColorProperty([0,0,0,1])
    rvbox_rectangle_color = ColorProperty([0,0,0,1])

    colorpicker_icon_color = ColorProperty([0,0,0,1])

    hex_dark_mode1 = "#313338"
    hex_dark_mode2 = "#2B2D31"
    hex_dark_mode3 = "#292B2F"
    hex_dark_mode4 = "#262730"
    hex_dark_mode5 = "#1c1d23"
    hex_dark_mode6 = "#0e1113"

    hex_light_mode1 = "#EEEEEE"
    hex_light_mode2 = "#E0E0E0"
    hex_light_mode3 = "#BDBDBD"

    white_rgba_theme = ColorProperty()
    black_rgba_theme = ColorProperty()
    main_theme_bg_color = ColorProperty()

    mdbg_screen_edit_note = ColorProperty()

    season_shared_uri = None
    picture_shared_uri = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(exit_manager=self.exit_manager, 
                                        select_path=self.chooser_callback_pc)
        self.white_rgba_theme = hex_to_rgba(self.hex_light_mode1)
        self.black_rgba_theme = hex_to_rgba(self.hex_dark_mode4)
        self.main_theme_bg_color = self.white_rgba_theme
        self.white_rgba = hex_to_rgba(self.hex_light_mode1)
        self.mdbg_screen_edit_note = self.white_rgba_default
        self.set_language()

        Window.bind(on_keyboard=self.on_key)
        if platform in ["android", "ios"]:
            self.chooser_picture = Chooser(self.chooser_callback_picture) # for loading picture recipe/notes from gallery
            self.chooser_load_recipes = Chooser(self.chooser_callback_recipes)  # for loading all recipes python file
            self.chooser_load_saison = Chooser(self.chooser_callback_saison)  # for loading all recipes python file
            self.chooser_load_notes = Chooser(self.chooser_callback_notes)  # for loading note_data.py
            self.chooser_load_ingredients = Chooser(self.chooser_callback_ingredients)  # for loading note_data.py

        # Add kv path to resource
        KV_PATH = abspath(join(dirname(__file__), 'kv'))
        resource_add_path(KV_PATH)

        if platform in ["win","macos","linux","unknown"]:
            Window.size = (360, 640)
            Window.minimum_width, Window.minimum_height = (360, 640)

    def build(self):
        ''' Avoid any operations unrelated to building the UI here, Only 
        Create and return widgets, Set widget properties
        Define the widget tree/layout '''

        root_widget = Builder.load_file('main.kv')
        # manager must be initialize before other since we use it as a "root" reference
        self.manager = Builder.load_file('manager.kv')
        self.appbar = Builder.load_file('appbar.kv')
        
        self.navigation = Builder.load_file('navigation.kv')

        root_widget.add_widget(self.appbar)
        root_widget.add_widget(self.manager)
        root_widget.add_widget(self.navigation)
        self.manager.load_screens()
        
        return root_widget # unload_string would be the opposite to reload KV

    def on_start(self):
        Clock.schedule_once(self.on_start_sheduled, 0)
        
    def on_start_sheduled(self, dt):
        ''' 
        Because on_start is called after the lifecycle method on_stop etc.. see kivyschool
        we postpone on_start method to avoid black screen because 
        of heavy memomry task in on start 
        '''
        
        log(" on start kivy !!")
        self.dont_gc = AndroidPermissions(self.start_app)
        # self.bind(on_resume = self.begone_you_black_screen)

        # load color theme
        self.segmented_activate(config_input["default_theme"])

        # load default language
        self.segmented_activate( config_input["language"])
        
    def start_app(self):
        self.dont_gc = None

    def on_pause(self):
        ''' Called when another activity comes into the foreground. '''
        return True

    # def on_destroy(self):
    #     ''' Called when when the activity is destroyed by the system. '''

    def on_stop(self):
        # Make sure Sensor is disconnected:
        if platform in ["android", "ios"]:
            log("app was stopped !!")
            self.manager.screenPicture.deviceOrientation.sensorEnable(False)
        
        # for performance analysis
        # self.profile.disable()
        # self.profile.dump_stats('cuistotdingo.profile')

        # stats = pstats.Stats('cuistotdingo.profile')
        # stats.sort_stats(pstats.SortKey.CUMULATIVE) # Sort by cumulative time
        # stats.print_stats(10) # Print the top 10 most time-consuming functions

    # def on_resume(self):
    #     # $bug black screen
    #     ''' Called when returning to the app after pausing. '''
        
    #     log("On resume !! Returning to kivy screen, we restore screen because of black screen...")
    #     Clock.schedule_once(self.update_viewport_sleep_mode, 0)

    # def begone_you_black_screen(self, arg):
    #     ''' this method is slighty different from the original source which does not use Clock '''
    #     log("app is resumed begone blcak screen test")
    #     self.unbind(on_resume = self.begone_you_black_screen)
    #     Clock.schedule_once(self.update_viewport_sleep_mode, 0.1)
        
    def on_key(self, window, key, *args):
        
        if key == 27:  # Check if the pressed key is the back button (Escape)
            match self.manager.current:
                case "screen A0":
                    self.manager.screenA0.ids._go_back_to_recipes.on_release()
                    return True # Indicate that the event was handled and prevent default behavior

                case "screen A5":
                    self.manager.screenA5.ids._save_recipe.on_release()
                    if self.manager.previous_screen == "screen A0" and self.manager.screenA5.ids._save_recipe.required_field_completed:
                        self.manager.current = "screen A0"
                        return True
                    else:
                        return False
                    
                case "picture screen":
                    self.manager.screenPicture.ids._preview.close_camerascreen()
                    return True

                case "screen edit note":
                    self.manager.restore_screen()
                    self.manager.screenEditNote.ids._note_box.save_note()
                    return True

                case "screen rst edit":
                    self.manager.screenEditNote.ids._note_box.add_rst(self.manager.screenRstEdit.ids._rst_document, self.manager.screenRstEdit.ids._rst_document.text)
                    self.manager.current = "screen edit note"
                    return True

                case "screen rst help":
                    self.manager.current = "screen rst edit"
                    return True

                case "screen rst code":
                    self.manager.current = "screen rst help"
                    return True

                case "screen full picture":
                    if not self.A5_edition : 
                        self.manager.restore_screen() 
                    self.manager.current = "screen A5"
                    return True

                case "screen E1":
                    self.manager.restore_screen()
                    hex_color = self.manager.screenE1.ids._colorpicker.hex_color
                    self.manager.screenE1.ids._colorpicker.change_picker_color(hex_color)
                    self.manager.current = "screen D2"
                    return True

                case "screen calcul":
                    self.manager.restore_screen()
                    self.manager.current = "screen D1"
                    return True

                case "screen season":
                    self.manager.restore_screen()
                    self.manager.current = "screen D1"
                    return True

            return False  # Allow default behavior (app exit)
        
        return False  # Allow default behavior for other keys

    # @mainthread
    # def update_viewport_sleep_mode(self, dt):
    #     ''' Wwe add this in case android kills the memory to refresh the black screen
    #           but it seems that it adds some weird behavior like  MDsegmented button not colored ..
    # so w found a better solution that was to delete unacessary operations in on_start method '''

    #     Window.update_viewport()
    #     Clock.schedule_once(self.refresh_segmented_control,0)
    
    def refresh_segmented_control(self, dt):
        ''' added because of the Window.update viewport() inducing a graphical bug... '''
        if not self.manager.screen_d1_loaded:
            self.manager.load_D1_screen()
        self.manager.screenD1.ids._segmented_control_color.do_layout()
        self.manager.screenD1.ids._segmented_control_lang.do_layout()
    
    '''##################################################################################
                                Setting functions
    ##################################################################################'''

    def set_language(self):
        language = config_input["language"]

        match language:
            case "English":
                self.current_lang = lang_en
            case "French":
                self.current_lang = lang_fr

    '''##################################################################################
                                Loading reloading functions
    ##################################################################################'''

    def reload_core(self):
        global recipes 
        recipes = get_recipes()

    def reload_input_recettes_module(self):
        from core import input_recettes as recettes_to_reload
        recettes_reloaded  = reload(recettes_to_reload)
        global recettes 
        recettes = recettes_reloaded.recettes    

    def reload_input_frigo_module(self):
        from core import input_frigo as input_frigo_to_reload
        mydico_frigo_reloaded  = reload(input_frigo_to_reload)
        global mydico_frigo 
        mydico_frigo = mydico_frigo_reloaded.mydico_frigo

    def reload_note_data_screen(self):
        from data import note_data as note_data_to_reload
        note_data_reloaded  = reload(note_data_to_reload) # 3. note_data_to_reload must be a module
        global note_data
        global note_index
        note_data = note_data_reloaded.note_data
        note_index = note_data_reloaded.note_index

        folder_private = join("images","notes")
        # check if all picturebox has their picture otherwise check backup or default picture...

        if platform in ["android", "ios"]:
            backup_dir = join(ROOT_FOLDER,"Documents", appname, "data", "backup","images")
        elif platform in ["win","macos","linux","unknown"]:
            backup_dir = join("data","backup","images")

        log("----- exists backup dir : " + str(exists(backup_dir)))
        for key in note_data:
            for elem in note_data[key]["data"]:
                if elem[0] == "Picture":
                    source = join("images", "notes", elem[1])
                    log("----- in reloading note data screen ---- source pict to find is : " + source)
                    log("----- exists source : " + str(exists(source)))
                    if elem[1] == "CuistotDingo.png":
                        source = source_image_default
                    
                    if not exists(source):

                        if platform in ["android", "ios"]:
                            backup_source = join(ROOT_FOLDER,"Documents", appname, "data", "backup","images",elem[1])
                        elif platform in ["win","macos","linux","unknown"]:
                           backup_source = join("data","backup","images", elem[1])

                        log("----- exists backup_source : " + str(exists(backup_source)))

                        try:
                            if exists(backup_source):
                                log("--------- backup_source pict is : " + backup_source)
                                try:
                                    copyfile(backup_source, source)
                                except Exception as e:
                                    e = traceback_format_exc()
                                    log("--------cannot copy file  backup_source creating folder-----" + str(e))
                                    # there is no app folder so we create it,
                                    makedirs(join("images","notes"), exist_ok = True)
                                    copyfile(backup_source, source)
                        except Exception as e:
                            e = traceback_format_exc()
                            log("--------file might not exists-----" + str(e))
                            backup_source = source_image_default
                            try:
                                copyfile(backup_source, source)
                            except Exception as e:
                                e = traceback_format_exc()
                                # there is no app folder so we create it,
                                log("---cannot copy file  backup_source creating folder---" + str(e))
                                makedirs(join("images","notes"), exist_ok = True)
                                copyfile(backup_source, source)
                            
        log("----- end reload note_data_screen  ------- ")

    @mainthread
    def load_recipe_image(self):
        log("----  Start load recipe_image mainthread -----")
        if not self.manager.screen_a4_loaded: 
            self.manager.load_A4_screen()

        source_image = self.manager.screenPicture.source
        log(" in load recipe_image : source_image : " + source_image)
        # tile, picture_name, source, root
        grid1 = self.manager.screenA1.ids._grid1
        grid2 = self.manager.screenA2.ids._grid2
        grid3 = self.manager.screenA3.ids._grid3
        rvgrid = self.manager.screenA4.ids._rvgrid

        # 1. For New recipe image
        if self.manager.current == "screen A5" and not self.A5_edition:
            self.manager.screenA5.tile_A5.ids.image.source = source_image # for screen A $source runtime
            self.manager.screenA5.tile_A5.ids.image.reload()
            self.manager.previous_screen = 'screen A5'

        # 2. Modifying existing recipe image
        else:
            screens = {"screen A1": grid1,"screen A2": grid2,"screen A3": grid3,"screen A4": rvgrid}
            root_screen = self.manager.tile_mother_manager.tile_screen
            if root_screen in ["screen A1", "screen A2"]:
                screens.pop("screen A1")
                screens.pop("screen A2")
            else:
                screens.pop(root_screen)

            ''' Weird things are happening when dealing with source 'tiles or source images,
            first we changed tiles'source (without reloading because it added unexpected behavior)
            Now it is not working, so we need to reload() and reload it... '''

            # here self.tile is mother tile 
            self.manager.tile_mother_manager.source = source_image # for screen A0 $source runtime
            self.manager.tile_mother_manager.ids.image.source = source_image # for screen A0 $source runtime
            self.manager.tile_mother_manager.ids.image.reload()
            self.manager.screenA0.tile_A0.source = source_image # for screen A $source runtime
            self.manager.screenA0.tile_A0.ids.image.source = source_image # for screen A $source runtime
            self.manager.screenA0.tile_A0.ids.image.reload()
            
            if not self.manager.screen_a5_loaded: 
                self.manager.load_A5_screen()
            self.manager.screenA5.tile_A5.source = source_image # for screen A $source runtime
            self.manager.screenA5.tile_A5.ids.image.source = source_image # for screen A $source runtime
            self.manager.screenA5.tile_A5.ids.image.reload()
            
            # propagate the loading to other grid images at runtime for Screen A
            for grid in screens.values():
                for tile in grid.children:
                    if self.manager.screenPicture.picture_name == tile.index_picture:
                        # load source
                        tile.ids.image.source = source_image # $source runtime
                        tile.ids.image.reload()

        log("----  End load_recipe_image mainthread -----")

    @mainthread
    def load_note_image(self):
        ''' Because of the black Screen we try to do this in the mainthread'''

        log(" ------- start load_note_image ------------")
        log("self.source_picture : "+ self.source_picture)

        if platform in ["android", "ios"]:
            path = join(app_storage_path(), "app" , self.source_picture)
        else:
            path = self.source_picture #images/notes/picture_name

        if exists(path):
            self.current_fitimage.source = self.source_picture #$source runtime
            self.current_fitimage.reload() #$source runtime
            self.current_fitimage.parent.source = self.source_picture #$needed because of the save note code
  
        log(" ------- end load_note_image ------------")

    '''##################################################################################
                                dialog functions
    ##################################################################################'''

    def close_dialog(self, instance_button, dialog_instance):
        if dialog_instance.id_dialog == "font_style":
            if "menu" in self.configbox.ids._configbox_label.text:
                self.configbox.ids._configbox_field.text = self.font_style_menu
            if "tile" in self.configbox.ids._configbox_label.text:
                self.configbox.ids._configbox_field.text = self.font_style_tile

        dialog_instance.dismiss()

    def show_load_recettes_dialog(self):
        ''' Here lambda function is needed because we need to return args
        otherwise just on_release = myfunction # is ok. '''

        self.load_action = "recipes"
        self.load_recipes_dialog = MyMDDialog(
            id_dialog = "load_recipes_data",
            title= self.current_lang["dialog"][2],
            type="custom",
            buttons=[
                MDFlatButton(
                    text= self.current_lang["dialog"][7],
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release= lambda x: self.close_dialog(x, self.load_recipes_dialog),

                ),
                MDRaisedButton(
                    text= self.current_lang["dialog"][6],
                    on_release= lambda x : self.chooser_start_load_recipes(x, self.load_recipes_dialog),
                ),
            ],
        )
        self.load_recipes_dialog.open()

    def show_load_notes_dialog(self):
        self.load_action = "notes"
        self.load_notes_dialog = MyMDDialog(
            id_dialog = "load_note_data",
            title= self.current_lang["dialog"][3],
            type="custom",
            buttons=[
                MDFlatButton(
                    text= self.current_lang["dialog"][7],
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release= lambda x: self.close_dialog(x, self.load_notes_dialog),

                ),
                MDRaisedButton(
                    text= self.current_lang["dialog"][6],
                    on_release= lambda x : self.chooser_start_load_notes(x, self.load_notes_dialog),
                ),
            ],
        )

        self.load_notes_dialog.open()

    def show_load_ingredients_dialog(self):
        self.load_action = "ingredients"
        self.load_ingredients_dialog = MyMDDialog(
            id_dialog = "load_note_data",
            title=self.current_lang["dialog"][4],
            type="custom",
            buttons=[
                MDFlatButton(
                    text= self.current_lang["dialog"][7],
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release= lambda x: self.close_dialog(x, self.load_ingredients_dialog),

                ),
                MDRaisedButton(
                    text= self.current_lang["dialog"][6],
                    on_release= lambda x : self.chooser_start_load_ingredients(x, self.load_ingredients_dialog),
                ),
            ],
        )

        self.load_ingredients_dialog.open()

    def show_load_saison_dialog(self):
        self.load_action = "saison"
        self.load_saison_dialog = MyMDDialog(
            id_dialog = "load_saison_data",
            title= self.current_lang["dialog"][5],
            type="custom",
            buttons=[
                MDFlatButton(
                    text= self.current_lang["dialog"][7],
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release= lambda x: self.close_dialog(x, self.load_saison_dialog),

                ),
                MDRaisedButton(
                    text= self.current_lang["dialog"][6],
                    on_release= lambda x : self.chooser_start_load_saison(x, self.load_saison_dialog),
                ),
            ],
        )

        self.load_saison_dialog.open()

    def show_help_dialog(self):
        self.load_help_dialog = MyMDDialog(
            id_dialog = "help_section",
            # width_offset = self.width_offset_dialog,
            # size_hint = (0.4, None),
            title= self.current_lang["help"][0],
            content_cls = DialogHelpContent(text_content = self.current_lang["help"][1]),
            type="custom",
            buttons=[
                MDRaisedButton(
                    text="Ok",
                    on_release= lambda x: self.close_dialog(x, self.load_help_dialog),
                ),
            ],
        )
        if platform in ["android", "ios"]:
            self.load_help_dialog.update_width()
        self.load_help_dialog.open()

    def show_font_style_dialog(self):
        self.dialog = MyMDDialog(
            id_dialog = "font_style",
            title= self.current_lang["dialog"][8],
            type="confirmation",
            auto_dismiss=True,
            items=[ItemConfirm(text=str(name_syle)) for name_syle in theme_font_styles[5:14]],
            buttons=[
                MDFlatButton(
                    text= self.current_lang["dialog"][7],
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release= lambda x: self.close_dialog(x, self.dialog)),
                MDRaisedButton(
                    text= self.current_lang["dialog"][6],
                    on_release= lambda x: self.save_style_and_close(self.dialog),
                ),
            ],
        )
        self.dialog.open()

    '''##################################################################################
                                File manager or filepicker functions
    ##################################################################################'''

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def chooser_callback_pc(self, path: str):
        ''' Called for non android like windows when click on the file name
        :param path: path to the selected directory or file;
        android equivalent is chooser_callback_picture. '''
        
        path = abspath(path) # setted because of the resource_add_path
        self.exit_manager()

        if self.manager.current == "screen edit note":
            self.get_image_note_file_manager(path)
            
        if self.manager.current == "picture screen":
            if self.manager.previous_screen == "screen edit note":
                self.get_image_note_file_manager(path)
                # we add this because folder is twice in note can be in item or in camera
            else:
                subdir = "recipes"
                picture_name = self.manager.screenPicture.picture_name
                self.source_picture = join("images", subdir, picture_name + ".jpg")
                copyfile(path,self.source_picture)
                self.downgrade_image_resolution(self.source_picture, subdir)
                self.manager.screenPicture.source = self.source_picture
                self.load_recipe_image()
            
            self.manager.current = self.manager.previous_screen
            self.manager.screenPicture.close_camera()
            self.manager.screenPicture.disconnect_camera()

        if self.manager.current == "screen D4":
            if self.load_action == "recipes" : 
                # check if new file has the code key value
                with open(path, "r") as f: 
                    data = f.read()[11:]
                try:
                    js = json_loads(data)
                    if isinstance(js,dict) and js["code"] == CODE_RECIPES :                        
                        # 1. Replace existant recipes input with new one
                        dest = join("core","input_recettes.py")
                        copyfile(path, dest)

                        # 2 Reload import and recettes variable
                        self.reload_input_recettes_module()

                        # 3 Reload core
                        self.reload_core()

                        # 4 Reload max_ingredient
                        config_input["ingredient_max_calcul"] = False
                        ingredient_max_calcul(config_input, recipes)
                        
                        # 5. Reload all screens
                        self.manager.reload_recipes_screens(["screen A1", "screen A2", "screen A3", "screen A4"])

                except json_JSONDecodeError as e:
                    log("The recipe file is not a valid json :" + str(e))
                    toast(self.current_lang["toast"][7])

            elif self.load_action == "saison":

                saison_title = ['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']
                data = []
                with open(path, "r", encoding='utf-8') as f: 
                    data_file = f.readline().split(",")
                for i in range(len(data_file)):
                    data.append(unidecode(data_file[i].strip("'\n'")))

                if data == saison_title:
                    # 1. Replace existant recipes input with new one
                    dest = join("core","saison.csv")
                    copyfile(path, dest)

                    # 2 Reload core
                    self.reload_core()

                    # 3. Reload all screens
                    self.manager.reload_recipes_screens(["screen A1", "screen A2", "screen A3", "screen A4"])
                else:
                    toast(self.current_lang["toast"][8])
            
            elif self.load_action == "notes":
                with open(path, "r") as f: 
                    data = f.read()
                try:
                    # 1. check if the note file is correct
                    if data[14:102] == CODE_NOTES:

                        # 1 Replace existant notes input with new one
                        dest = join("data","note_data.py")
                        copyfile(path, dest)

                        # 2. Reload new file notes  
                        self.reload_note_data_screen()

                        if not self.manager.screen_c1_loaded:
                            self.manager.load_C1_screen()

                        # 3. Delete existing notes
                        self.manager.screenC1.ids._selection_list.delete_all_notes()
                
                        # 4. Load notes from file
                        self.manager.screenC1.ids._selection_list.load_notes_from_data()

                except json_JSONDecodeError as e:
                    log("The note file is not a valid json :"+ str(e))
                    toast(self.current_lang["toast"][9])

            elif self.load_action == "ingredients":
                with open(path, "r") as f: 
                    data = f.read()[15:]
                try:
                    js = json_loads(data)
                    if isinstance(js,dict) and js["code"] == CODE_INGREDIENTS :

                        # 1 Replace existant input_frigo input with new one
                        dest = join("core","input_frigo.py")
                        copyfile(path, dest)

                        # 2 Reload import and mydico_frigo variable
                        self.reload_input_frigo_module()

                        # 3 Reload core
                        self.reload_core()

                        # 4 Clear and populate stack :
                        if not self.manager.screen_b1_loaded:
                            self.manager.load_B1_screen()

                        self.manager.screenB1.ids._stack_b1.delete_all_stack()
                        self.manager.screenB1.ids._stack_b1.populate_stack()

                        log( "in my fridge I have : " + str(mydico_frigo["ingredients"]))

                        # 5. Reload screens A1 and A2
                        self.manager.reload_recipes_screens(["screen A1", "screen A2"])

                except json_JSONDecodeError as e:
                    log("The ingredients file is not a valid json :"+ str(e))
                    toast(self.current_lang["toast"][10])

        log(" ----- end chooser callback pc ----")

    def chooser_start_picture(self):
        ''' Called to select picture from chooser. '''
        
        if platform in ["android","ios"]:
            self.chooser_picture.choose_content(MIME_type = 'image/*', multiple = False)
        else:
            self.file_manager_open()

    def chooser_start_load_recipes(self, button, instance_dialog):
        ''' Called to select recipes data file from chooser, 
        button args needed because of the lambda function. '''
        instance_dialog.dismiss()
        if platform in ["android","ios"]:
            self.chooser_load_recipes.choose_content(MIME_type = 'text/x-python', multiple = False)
        else:
            self.file_manager_open()

    def chooser_start_load_saison(self, button, instance_dialog):
        ''' Called to select season data file from chooser. '''
        instance_dialog.dismiss()
        if platform in ["android","ios"]:
            self.chooser_load_saison.choose_content(MIME_type = 'text/*', multiple = False)
        else:
            self.file_manager_open()

    def chooser_start_load_notes(self, button, instance_dialog):
        ''' Called to select notes data file from chooser'''
        instance_dialog.dismiss()
        if platform in ["android","ios"]:
            self.chooser_load_notes.choose_content(MIME_type = 'text/x-python', multiple = False)
        else:
            self.file_manager_open()

    def chooser_start_load_ingredients(self, button, instance_dialog):
        ''' Called to select ingredient data file from chooser'''
        instance_dialog.dismiss()
        if platform in ["android","ios"]:
            self.chooser_load_ingredients.choose_content(MIME_type = 'text/x-python', multiple = False)
        else:
            self.file_manager_open()

    def chooser_callback_picture(self,uri_list):
        '''Called when a pictures has been chosen by the user from gallery to notes or recipes pictures
            here uri_list has only one element since chooser has multiple=false option '''
        
        log(" ------------- in  chooser_callback_picture start -----------")

        current_screen = self.manager.current
        picture_name = self.manager.screenPicture.picture_name
        log(" ------------- Level 2 chooser_callback_picture picture_name is " + picture_name) # picture_name = 121
        self.source_picture = join("images", "notes", picture_name + ".jpg")


        if "note" in current_screen:
            log(" ------------- note in : " + str(current_screen) + " -----------")
            self.get_image_note_android_chooser(uri_list) # copy from shared and reload image
            folder = join("images","notes")

        else:
            if self.manager.previous_screen == "screen edit note":
                self.get_image_note_android_chooser(uri_list) # copy from shared and reload image
            else:
                # coming from screen A0 or A5
                self.source_picture = join("images","recipes",picture_name + ".jpg")
                folder = join("images","recipes")
                self.copy_uri_list_from_shared(uri_list, folder) #1.
                self.manager.screenPicture.source = self.source_picture #2.
                self.load_recipe_image()

            self.manager.screenPicture.change_screen_to_previous()  # because of the bug merging screen we do it in mainthread
        self.manager.screenPicture.close_camera()
        self.manager.screenPicture.disconnect_camera()
        
        #4. save image to shared storage
        ss = MySharedStorage()
        private_storage = self.source_picture
        ss.copy_to_shared(private_storage,collection = Environment.DIRECTORY_DOCUMENTS, filepath = private_storage)

        #5. Check File parenthesis in case android failed to replace file
        ''' We check all files, we never know how android adds parenthesis sometimes before extension
         sometimes after'''
        self.checkfilename(folder)
        log(" ------------- in  chooser_callback_picture end -----------")

    def chooser_callback_recipes(self, list_uri):
        log(" ----- start chooser callback recipes ----")
        # Code to replace current recipes_input with the one selected from chooser
        # create temp file and check if is valid json

        self.copy_uri_list_from_shared(list_uri, "temp")
        path = join(app_storage_path(), "app", "temp", "input_recettes.py")
        with open(path, "r") as f: 
            data = f.read()[11:]

        try:
            js = json_loads(data)
            if isinstance(js,dict) and js["code"] == CODE_RECIPES :

                # 1 Replace existant recipes input with new one
                self.copy_uri_list_from_shared(list_uri, "core")

                # 2. Check if images in private and delete them
                list_recipes_images = self.java_list_files(join("images","recipes"))
                log("--2-- list_recipes_images is : " + str(list_recipes_images))

                if list_recipes_images:
                    # Erase all recipes images in private storage
                    try:
                        self.delete_all_android_dir_files(DIR_RECIPES_PRIVATE)
                        log("all private pictures should be deleted")
                        log(" in private recipes I have : " + str(self.java_list_files(DIR_RECIPES_PRIVATE)))
                    except Exception as e:
                        e = traceback_format_exc()
                        log("--4-- error while deleting all shared files : " + str(e))
                        text_exception = "In app.chooser callback recipes , error while trying" \
                        " to delete_all_android_dir_files "  + str(e)
                        self.check_exceptions(text_exception)

                # 3 seek the appname to import the picture from that folder
                self.appname_callback = self.get_appname_by_uri(list_uri[0])
                log(" the appname seeked in callback recipe is : " + self.appname_callback)

                # 4 copy all images from shared images/recipes to private
                shared_dir = join("Documents",self.appname_callback,"images","recipes")
                # filesname = self.get_uri_filesname_from_folder(shared_dir)
                # we used get_uri_filename_from_folder before but because we are debugging lets try another way
                filesname = self.java_list_files(shared_dir)
                log(" In shared dir I have this recipes images :" + str(filesname))

                list_uri = library.getUrisFromSharedFolder(context, shared_dir)
                log("list_uri from library getUrisFromSharedFolder is : " + str(list_uri))

                if list_uri:
                    log(" list_uri exists starting to copy_uri_list_from_shared")
                    folder = join("images","recipes")
                    self.copy_uri_list_from_shared(list_uri, folder)
                    try:
                        list_files_interne = self.java_list_files(DIR_RECIPES_PRIVATE)
                        log("after copying from shared we have in private : " + str(list_files_interne))
                    except Exception as e:
                        e = traceback_format_exc()
                        log(" error while list files java DIR_RECIPES_PRIVATE : " + str(e))
                        list_files_interne = []
                        text_exception = "In app.chooser callback recipes , error while trying" \
                        " to get files list DIR_RECIPES_PRIVATE : "  + str(e)
                        self.check_exceptions(text_exception)

                    log("--4--1. in private recipes images folder I have this images : " + str(list_files_interne))
                    
                    # 5. Erase all recipes pictures in shared storage and copy new ones
                    if self.appname_callback != appname:
                        log(" 5. Erase all recipes pictures in shared storage and copy new ones")
                        file_dir_documents = join(ROOT_FOLDER,"Documents", appname,"images","recipes")
                        self.delete_all_android_dir_files(file_dir_documents)

                        ss = MySharedStorage()
                        for file in list_files_interne:
                            title = basename(file)
                            private_storage = join("images","recipes", title)
                            shared_path = ss.copy_to_shared(private_storage, collection = Environment.DIRECTORY_DOCUMENTS, filepath=private_storage) # if folder in file_path then it wil be created

                else:
                    if filesname:
                        log("list_uri not working but filesname is working so we try to copyfile")
                        for filename in filesname:
                            source = join(ROOT_FOLDER,"Documents", appname,"images","recipes",filename)
                            dest = join("images", "recipes", filename)
                        try:
                            copyfile(source, dest)
                            log("-------------succeeed to copy to ----------------" + dest)

                        except Exception as e:
                            log("-------------error while copying from " + source + " to " + dest)
                            e = traceback_format_exc()
                            log(" error while copying shared documents images recipes to private  : " + str(e))
                            text_exception = "In app.chooser callback recipes , error while trying" \
                            " to copyfile from : " + str(source) + " to : " + str(dest) + " : "  + str(e)
                            self.check_exceptions(text_exception)

                # 2 Reload import and recettes variable
                self.reload_input_recettes_module()

                # 3 Reload core
                self.reload_core()

                # 4 Reload max_ingredient
                config_input["ingredient_max_calcul"] = False
                ingredient_max_calcul(config_input, recipes)

                # 5. Reload all screens
                self.manager.reload_recipes_screens(["screen A0","screen A1", "screen A2", "screen A3", "screen A4"])

                # 6. Remove temp file
                if exists(path):
                    remove(path)
                    log("The file has been removed")
                else:
                    log("The file does not exist")

        except json_JSONDecodeError as e:
            log("The recipe file is not a valid json :"+ str(e))
            toast(self.current_lang["toast"][7])
            
        log(" ----- end chooser callback recipes ----")
    
    def chooser_callback_saison(self, uri_list):
        log(" ----- start chooser_callback saison ----")
        # Code to replace current saison.csv with the one selected from chooser
        # create temp file and check if is valid csv

        self.copy_uri_list_from_shared(uri_list, "temp_saison")
        path = join(app_storage_path(), "app", "temp", "saison.csv")
        
        saison_title = ['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']
        data = []
        with open(path, "r", encoding='utf-8') as f: 
            data_file = f.readline().split(",")
        for i in range(len(data_file)):
            data.append(unidecode(data_file[i].strip("'\n'")))

        if data == saison_title:
            # 1 Replace existant recipes input with new one
            self.copy_uri_list_from_shared(uri_list, "saison")

            # 2 Reload core
            self.reload_core()

            # 3. Reload all screens
            self.manager.reload_recipes_screens(["screen A1", "screen A2","screen A3", "screen A4"])

        else:
            toast(self.current_lang["toast"][8])

        # 4. Remove temp file
        if exists(path):
            remove(path)
            log("The file has been removed")
        else:
            log("The file does not exist")

    def chooser_callback_notes(self, uri_list):
        ''' Callback after selecting the note_data.py file to reload the last backup file
        multiple = False so uri_list only has one element. '''

        log("------ in chooser callback_notes start ------")

        # create temp file and check if is valid json
        self.copy_uri_list_from_shared(uri_list, "temp_note")
        temp_path = join(app_storage_path(), "app", "temp", "note_data.py")
        
        with open(temp_path, "r") as f: 
            test = f.read()

        # A. check if the note file is correct
        if test[14:102] == CODE_NOTES:
            # 1 Replace existant notes input with new one
            log("--1-- Copying from shared the note_data file to private")
            self.copy_uri_list_from_shared(uri_list, "data")

            try:
                list_images_notes = self.java_list_files(DIR_NOTES_PRIVATE)
                log("success to get files DIR_NOTES_PRIVATE ! : "+ str(list_images_notes))
            except Exception as e:
                e = traceback_format_exc()
                log("---- error while trying to read DIR_NOTES_PRIVATE with java list files : " + str(e))
                list_images_notes = []
                text_exception = "In app.chooser_callback_note , error while trying" \
                " to read directory with java list files... "  + str(e)
                self.check_exceptions(text_exception)
                
            if list_images_notes:

                # 2. Erase all notes images in private storage
                log("--2-- Erasing note private images")

                try:
                    self.delete_all_android_dir_files(DIR_NOTES_PRIVATE)
                except Exception as e:
                    e = traceback_format_exc()
                    log("--4-- error while deleting all shared files : " + str(e))
                    text_exception = "In app.chooser_callback_note , error while trying" \
                    " to delete_all_android_dir_files "  + str(e)
                    self.check_exceptions(text_exception)

                list_files_interne = self.java_list_files(DIR_NOTES_PRIVATE)
                log("--5-- now after deletion in notes folder I have this images : " + str(list_files_interne))

            # 3 seek the appname note_data folder to import the picture from that folder
            self.appname_callback = self.get_appname_by_uri(uri_list[0])

            # 4 copy all images from shared images/notes to private
            shared_dir = join("Documents",self.appname_callback,"images","notes")
            log("--7-shared dir for shared storage images-notes- : " + str(shared_dir))
            filesname = self.java_list_files(shared_dir)
            log("--8- filesname in shared storage images-notes- : " + str(filesname))

            MIME_type = "image/*"
            list_uri = library.getUrisFromSharedFolder(context, shared_dir)
            log("--9---- list_uri notes images is : " + str(list_uri) + " ------------")
            
            if list_uri:
                log("---   in list_files_externe ----")
                folder = join("images","notes")
                log("--------------------------------------------------------------------")
                log("--------------------------------------------------------------------")
                log("------ copying the notes images folder from shared to private ------")
                log("--------------------------------------------------------------------")
                log("--------------------------------------------------------------------")
                self.copy_uri_list_from_shared(list_uri, folder)
                list_files_interne = self.java_list_files(DIR_NOTES_PRIVATE)
                log("--10-- in notes folder I have copied form shared thoses images : " + str(list_files_interne))

                # 5. Erase all notes pictures in shared storage and copy new ones
                log("--11-- deletion process appname is : " + appname + " and appname_callback is : " + self.appname_callback )
                if self.appname_callback != appname:
                    file_dir_documents = join(ROOT_FOLDER,"Documents", appname,"images","notes")
                    self.delete_all_android_dir_files(file_dir_documents)

                    ss = MySharedStorage()
                    for file in list_files_interne:
                        title = basename(file)
                        private_storage = join("images","notes", title)
                        shared_path = ss.copy_to_shared(private_storage, collection = Environment.DIRECTORY_DOCUMENTS, filepath=private_storage) # if folder in file_path then it wil be created
            else:
                if filesname:
                    log("list_uri not working but filesname is working so we try to copyfile")
                    for filename in filesname:
                        source = join(ROOT_FOLDER,"Documents", appname,"images","notes",filename)
                        dest = join("images", "notes", filename)
                    try:
                        copyfile(source, dest)
                        log("-------------succeeed to copy to ----------------" + dest)

                    except Exception as e:
                        log("-------------error while copying from " + source + " to " + dest)
                        e = traceback_format_exc()
                        log(" error while copying shared documents images notes to private  : " + str(e))
                        text_exception = "In app.chooser_callback_notes , error while trying" \
                        " to copyfile from : " + str(source) + " to : " + str(dest) + " : "  + str(e)
                        self.check_exceptions(text_exception)
                        
            # 6. Reload new file notes  
            log(" reload_note_data_screen")
            self.reload_note_data_screen()
                
            # 7. Remove temp file
            if exists(temp_path):
                remove(temp_path)
                log("The file has been removed")
            else:
                log("The file does not exist")

            Clock.schedule_once(self.delete_and_reload_notes, 0)

        else:
            toast(self.current_lang["toast"][9])

        log("------ in chooser callback_notes end ------")

    @mainthread
    def delete_and_reload_notes(self, dt):
        # Clocked because of the error Mainthread when loading screen C1
        if not self.manager.screen_c1_loaded:
            self.manager.load_C1_screen()
        log(" in method delete all notes and reload")
        self.manager.screenC1.ids._selection_list.delete_all_notes()
        self.manager.screenC1.ids._selection_list.load_notes_from_data()

    def chooser_callback_ingredients(self, uri_list):
        log(" ----- start chooser_callback_ingredients ----")
        # Code to replace current ingredients stack with the one selected from chooser
        # create temp file and check if is valid json

        self.copy_uri_list_from_shared(uri_list, "temp_ingredients")
        path = join(app_storage_path(), "app", "temp", "input_frigo.py")
        with open(path, "r") as f: 
            data = f.read()[15:]
        try:
            js = json_loads(data)
            if isinstance(js,dict) and js["code"] == CODE_INGREDIENTS :

                # 1 Replace existant ingredients input with new one
                self.copy_uri_list_from_shared(uri_list, "core_ingredients")

                # 2 Reload import and mydico_frigo variable
                self.reload_input_frigo_module()
                
                # 3 Reload core
                self.reload_core()

                log( "in my fridge I have : " + str(mydico_frigo["ingredients"]))

                # 4 Clear and populate stack :
                if not self.manager.screen_b1_loaded:
                    self.manager.load_B1_screen()

                self.manager.screenB1.ids._stack_b1.delete_all_stack()
                self.manager.screenB1.ids._stack_b1.populate_stack()

                # 5. Reload screens A1 and A2
                self.manager.reload_recipes_screens(["screen A1", "screen A2"])

                # 6. Remove temp file
                if exists(path):
                    remove(path)
                    log("The file has been removed")
                else:
                    log("The file does not exist")

        except json_JSONDecodeError as e:
            log("The ingredients file is not a valid json :"+ str(e))
            toast(self.current_lang["toast"][10])  
    log(" ----- end chooser_callback_ingredients ----")

    def file_manager_open(self):
        self.file_manager.show_disks()

    def open_recipe_image_with_google(self, relative_path):
        if platform in ["android", "ios"] and relative_path != source_image_default:
            log("relative path in open recipe with google is : " + relative_path)
            relative_path = join("images","recipes", basename(relative_path))
            shared_path = join("Documents", appname, relative_path)
            shared_dir = join(ROOT_FOLDER, "Documents", appname,"images","recipes")
            abs_shared_path = join(ROOT_FOLDER, "Documents", appname, relative_path)
            log("shared path  is : " + shared_path)
            log("absolute_shared_path  is : " + shared_dir)
            filename = basename(relative_path)
            log("filename  is : " + filename)

            list_files_shared = self.java_list_files(shared_dir)
            log("list_files_shared  is : " + str(list_files_shared))

            # ss = MySharedStorage()
            # self.picture_shared_uri = ss._get_uri(shared_path, "image/png")
            # because sometimes uri is not available we try several ways, and if not, well yeaaah we leave it 
            
            self.picture_shared_uri = self.get_file_uri_provider(abs_shared_path, "cuistotdingov24")
            # if not self.picture_shared_uri:
            #     self.picture_shared_uri = library.getUriFromAbsoluteFilePath(context, abs_shared_path)
            log(" in open recipe image abs path is : " + abs_shared_path)
            log(" in open recipe image google self.picture_shared_uri is : " + str(self.picture_shared_uri))

            if filename in list_files_shared and self.picture_shared_uri:
                log("open with google")
                self.open_picture_with_google_photo(shared_path)
            else:
                log("open with kivy")
                self.open_picture_image_with_kivy(relative_path)
        else:
            self.open_picture_image_with_kivy(relative_path)
            
    def open_picture_image_with_kivy(self, relative_path):
        self.manager.edit_full_screen()
        if not self.manager.screen_full_picture_loaded: 
            self.manager.load_full_picture_screen()
        self.manager.screenFullPicture.ids._full_image.source = relative_path
        self.manager.current = "screen full picture"

    @mainthread
    def open_picture_with_google_photo(self, shared_path_picture):
        ''' 
        The parameter shared_path_picture must starts with Documents like Documents/appname/images/recipes/64.jpg
        That code was hard to make it good, because Uri was sometimes lost, and also google is different  
        when opened for the first 2 or 3 times, 
        so we introduce a safe season screen that works with scatterplane 
        '''
        Intent = autoclass('android.content.Intent')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        RESULT_LOAD_IMAGE = 1
        ss = MySharedStorage()
        intent = Intent(Intent.ACTION_VIEW)

        log("path_picture is : " + shared_path_picture)
        # self.picture_shared_uri = ss._get_uri(shared_path_picture, "image/png")
        self.picture_shared_uri = self.get_file_uri_provider(join(ROOT_FOLDER, shared_path_picture), "cuistotdingov24")
        intent.setDataAndType(self.picture_shared_uri, "image/png")

        intent.setPackage("com.google.android.apps.photos")
        # Grant read permissions to the receiving app (important for file URIs)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        # Start the activity to view the image
        currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        currentActivity.startActivityForResult(intent, RESULT_LOAD_IMAGE)

        self.picture_shared_uri = None

    def open_season_with_scatter(self):
        self.manager.edit_full_screen()
        if not self.manager.screen_season_loaded:
            self.manager.load_season_screen()
        self.manager.current = "screen season"

    def open_season_pictures(self, path_picture):
        if self.season_shared_uri:
            self.open_picture_with_google_photo(path_picture)
        else:
            self.season_to_shared()
            if self.season_shared_uri:
                self.open_picture_with_google_photo(path_picture)
            else:
                self.open_season_with_scatter()
    
    '''##################################################################################
                Saving copying deleting and other related functions
    ##################################################################################'''

    def save_to_shared(self, source, dest):
        if platform in ["android", "ios"]:
            ss = MySharedStorage()
            ss.copy_to_shared(source, collection = Environment.DIRECTORY_DOCUMENTS, filepath = dest) # if folder in file_path then it wil be created
            
    def copy_season_files(self):
        ''' We need to copy season files to shared since we couldn't diplay the google photos intent
        for private files, so we use shared files this is done at runtime 
        because otherwise files are not overwritted. '''

        if platform in ["android","ios"]:
            season_dir = join("Documents", appname, "images", "season")
            season_files = self.java_list_files(season_dir)

            if "saison_legumes_quebec.png" or "saison_legumes_france.png" not in season_files :
                season_files = []

            if not season_files:
                self.season_to_shared()

    def season_to_shared(self):
        ss = MySharedStorage()
        private_storage_france = join("images", "season", "saison_legumes_france.png")
        private_storage_quebec = join("images", "season", "saison_legumes_quebec.png")
        self.season_shared_uri = ss.copy_to_shared(private_storage_france,collection = Environment.DIRECTORY_DOCUMENTS, filepath = private_storage_france)
        ss.copy_to_shared(private_storage_quebec, collection = Environment.DIRECTORY_DOCUMENTS, filepath = private_storage_quebec)
        dir = join("images", "season")
        self.checkfilename(dir)

    def copy_recipe_to_clipboard(self, instruction_label, instruction, astuce_label, astuce, commentaire_label, commentaire,
                                  source_recette_label, source_recette):
        instruction = instruction_label +":\n    " + instruction + "\n"
        astuce = astuce_label + ":\n    " + astuce + "\n" if astuce else ""
        commentaire = commentaire_label + ":\n    " + commentaire + "\n" if commentaire else ""
        source_recette = source_recette_label + ":\n    " + source_recette if source_recette else ""

        Clipboard.copy(instruction + astuce + commentaire + source_recette)
        toast(self.current_lang["toast"][16]) #  texte copié

    def downgrade_image_resolution(self, path, subdir):
        ''' 
        Downsize the image filter (gives the highest quality)
        because pillow buildozer version is max 8.4.0 , module 'PIL.Image' has no attribute 
        'Resampling' so we use the old school Image.LANCZOS 
        Subdir is here in case we want to personalize the ratio for recipes or notes images...
        '''
        
        log("---- Downgrading image -------")

        # A1 size is (500,360)  , ratio is : 1.39
        # A0 size is (1080,405) , ratio is : 2.66
        # Note                    ratio is : 1.7

        with Image.open(path) as foo:  # original image is a (4032*3024) jpeg that is 4243 ko large
            ratio = foo.width/foo.height
            log("ratio : " + str(ratio) + " " + str(foo.width) + " " + str(foo.height)) # 0.75 3024 4032
            
            if subdir == "recipes":
                foo = foo.resize((int(378*ratio),378),Image.LANCZOS)
            else:
                if ratio>1: 
                    foo = foo.resize((int(378*ratio),378),Image.LANCZOS)
                else: 
                    foo = foo.resize((378,int(378*ratio)),Image.LANCZOS)

            foo.save(path, optimize=True, quality=80) 

    def copy_uri_list_from_shared(self, uri_list, subfolder):
        ''' Used when user select a file from shared like a picture or a python file to copy to the app storage
        copy data from shared storage to cache storage and copy cache to private 
        storage then delete the cache file copied
        the CuistotDingo.png image was compressed from 8 mo to 8 ko using 
        https://squoosh.app/editor
        https://imageoptim.com/online
        https://tinypng.com/ '''

        log("-------------------------------------------------------")
        log("-------------IN copy from_shared START-----------------")
        log("-------------------------------------------------------")
        log("------- copy from_shared uri_list is : " + str(uri_list))
        log("------- copy from_shared subfolder is : " + subfolder )
        try:
            ss = SharedStorage()
            i=0
            for uri in uri_list:
                i+=1
                log("------- i uri_list from copy from_shared is : " + str(i) )
                # default copy to "/storage/emulated/0/Android/data/org.test.appname/cache/FromSharedStorage/"
                path = str(ss.copy_from_shared(uri)) # /storage/emulated/0/Android/data/org.test/cuistotdingov16/cache/FromSharedStorage/40.jpg
                log("------- copy from_shared path is : " + path )
                # app_storage_path returns /data/user/0/org.test.appname/files/

                # 1. downgrade image resolution and rotate 90° if first lower than second like 3024*4032
                if subfolder == join("images","notes") or  subfolder == join("images","recipes"):
                    subdir = basename(subfolder)
                    self.downgrade_image_resolution(path, subdir)
                
                # 2. set file name and copy file to private
                if subfolder == join("images","notes"):
                    log("------subfolder == join(images,notes)-------")
                    log("------current fitimage == -------" + str(self.current_fitimage))
                    
                    if self.current_fitimage and not self.manager.current == "screen D4":
                        # check if image replaced was default or not
                        log("----copy from shared--current_fitimage.source == -------" + str(self.current_fitimage.source))
                        if basename(self.current_fitimage.source) == basename(source_image_default):
                            file_basename = self.generate_picture_note_name()
                            log("------- file_basename 1 is : " + file_basename)
                        else:
                            file_basename =  basename(self.current_fitimage.source)
                            log("------- file_basename 2 is : " + file_basename)
                    else: 
                        shared_dir = join("Documents",self.appname_callback,"images","notes")
                        list_files_externe = self.java_list_files(join(ROOT_FOLDER,shared_dir))
                        file_basename = list_files_externe[i-1]

                    self.source_picture = join(subfolder, file_basename)

                elif subfolder == join("images","recipes"):

                    if self.manager.current == "screen D4":
                        shared_dir = join("Documents",self.appname_callback,"images","recipes")
                        file_basename = basename(path)

                    else:
                        file_basename = self.manager.screenPicture.picture_name + ".jpg"
                        self.source_picture = join(subfolder, file_basename)
                        log("---- self.source_picture is : " + self.source_picture)
                    
                elif subfolder == "core" or subfolder == "temp":
                    log("------------subfolder ==  core or temp----------------")
                    log("------- subfolder is core : " + subfolder)
                    file_basename = "input_recettes.py"

                elif subfolder == "saison":
                    file_basename = "saison.csv"
                    subfolder = "core"

                elif subfolder == "temp_saison":
                    file_basename = "saison.csv"
                    subfolder = "temp"
                
                elif subfolder == "temp_note":
                    log("-------------subfolder == temp_note----------------")
                    file_basename = "note_data.py"
                    subfolder = "temp"

                elif subfolder == "data":
                    log("-------------subfolder == data----------------")
                    file_basename = "note_data.py"

                elif subfolder == "temp_ingredients":
                    file_basename = "input_frigo.py"
                    subfolder = "temp"

                elif subfolder == "core_ingredients":
                    file_basename = "input_frigo.py"
                    subfolder = "core"

                destination = join(app_storage_path(), "app", subfolder, file_basename)
                log("------- file_basename 5 is : " + file_basename)
                log("------- copy from_shared destination is : " + destination)
            
                try:
                    '''
                    we used replace, not rename, because replace is cross-platform
                    shutil.move(path,destination), move a file from source to destination
                    we thought shutil.move was the source of the black screen issue, but not
                    so we can go back to shutil.move after issue resoved
                    copyfile from shutil does replace the file
                    '''
                    copyfile(path, destination)
                    log("-------------succeeed to copy to ----------------" + destination)

                except Exception as e:
                    e = traceback_format_exc()
                    # there is no app folder so we create it,
                    if not exists(join(app_storage_path(), "app", subfolder)):
                        log("-------------the folder does not exists so we try to create it ----------------")
                        try:
                            log("-------------in copy from_shared creating folder " + join(app_storage_path(), "app", subfolder) + "----------------")
                            makedirs(join(app_storage_path(), "app", subfolder), exist_ok = True)
                            copyfile(path, destination)
                            log("-------------succeeed to copy to ----------------" + destination)
                        except:
                            log("--------------erroooorr moving from shared to --------------" + destination)
                            text_exception = "In app.copy uri_list_from_shared , either makedirs "  + str(subfolder) + \
                            "or copyfile failed... path is :  " + str(path) + " and destinations is : " + str(destination) 
                            self.check_exceptions(text_exception)

                # 3 remove cache 
                if exists(path):
                    remove(path)
                    log("-------------succeeed to Remove the file : " + path)
                
        except Exception as e:
            e = traceback_format_exc()
            log_warning('SharedStorageExample.chooser_callback():')
            log_warning(str(e))
            text_exception = "In app.copy uri_list_from_shared , error : "  + str(e) + \
            self.check_exceptions(text_exception)

        log("------- in copy from_shared end -------")

    def check_exceptions(self, text):
        path_interne = join("data", "check_exceptions.txt")
        current_time = self.get_current_time()
        with open(path_interne, 'a', encoding='utf-8') as f :
            f.write(text +  "current time is : " + str(current_time))
        if platform in ["android", "ios"]:
            path_externe = join("data", "check_exceptions.txt")
            self.save_to_shared(path_interne, path_externe)
            dir = "data"
            self.checkfilename(dir)

    def get_image_note_android_chooser(self,uri_list):
        folder = join("images","notes")
        #1 copy from shared to private
        self.copy_uri_list_from_shared(uri_list, folder)
        #2. reload image :
        Clock.schedule_once(lambda dt: self.load_note_image())

    def get_image_note_file_manager(self, path):
        ''' save note image selected from pc chooser '''

        if self.current_fitimage.source == source_image_default:
            picture_basename = self.generate_picture_note_name()
        else:
            picture_basename = basename(self.current_fitimage.source)

        #1. save image to private storage :
        self.source_picture = join("images","notes", picture_basename)
        copyfile(path,self.source_picture)

        #2. reload image :
        Clock.schedule_once(lambda dt: self.load_note_image())

    def check_parenthesis_filename(self,subfolder,list_names):
        ''' Code to rename the file copied by android, sometimes it adds the unwanted (), for now it is only
        file by file, if needed change this code for several files
        returns filesname_to_delete list '''
        # $deplace

        log("------------start check_parenthesis_filename")
        result = []
        for name in list_names:
            if "(" in name:
                log("parenthesis finded, we try to delete the file " + name)
                index = name.find("(")
                temp= name[:index]+name[index+3:]
                name_to_delete = temp.replace(" ", "")
                if name_to_delete in list_names:
                    result.append(name)
                    result.append(name_to_delete)
                    break
                else:
                    # name_to_delete not in list handled just in case
                    file_path_old = join(ROOT_FOLDER,"Documents", appname, subfolder, name) #"/storage/emulated/0/Documents/DeleteImage/"
                    file_path_new = join(ROOT_FOLDER,"Documents", appname, subfolder, name_to_delete) #"/storage/emulated/0/Documents/DeleteImage/"
                    self.rename_file_java(file_path_old, file_path_new)
                    break
        log("------------end check_parenthesis_filename")
        return result

    def get_shared_files_list(self, app_name, subfolder):
        '''  [-- error PermissionError while reading directory_path ]
        path that leeds to issues :
        directory_path3 = join("storage/emulated/0/Documents",app_name,subfolder) #/external/file/153/images/notes/
        path working:
        join(primary_external_storage_path(),Environment.DIRECTORY_DOCUMENTS,app_name,subfolder) '''
        # $deplace
        log("--- start get files_name_list ----")
        log("--- appname is  ---- " + appname )
        log("--- subfolder is  ---- " + subfolder)
        if platform in ["android", "ios"]:
            directory_abs_path = join(ROOT_FOLDER,"Documents",app_name,subfolder)
            log(" in get files_name_list directory_path is : " + directory_abs_path)
            dir_list = self.java_list_files(directory_abs_path)

            if not dir_list:
                try:
                    dir_list = self.get_uri_filesname_from_folder(join("Documents",app_name,subfolder))
                except Exception as e:
                    e = traceback_format_exc()
                    text_exception = "---- error while reading get_uri_filesname_from_folder : " \
                    + str(directory_abs_path) + " : " + str(e)
                    dir_list = []
                    log(text_exception)
                    self.check_exceptions(text_exception)
            
            log("dir_list :" + str(dir_list))
            log("--- end get files_name_list ----")

            return dir_list

    # def get_private_files_list(self, path):
    #     ''' needed when replacing old files for new ones, like old recipes images
    #     path must be like : DIR_NOTES_PRIVATE '''
    #     try:
    #         list_files = self.java_list_files(path)
    #     except Exception as e:
    #         e = traceback_format_exc()
    #         log("---- error while trying to read directory : " + str(e))
    #         list_files = []
    #         text_exception = "In app.chooser_callback_note , error while trying" \
    #         " to read directory " + path  + str(e)
    #         self.check_exceptions(text_exception)
    #     return list_files

    def checkfilename(self, subfolder):
        ''' This function will check for doublons when saving file to shared storage
            /storage/emulated/0/Documents/appname/subfolder
            here subfolder is images/notes or images/recipes '''
        # $deplace
        log("-------- checkfilename start ------")
        if platform in ["android", "ios"]:
            list_names = self.get_shared_files_list(appname, subfolder)
            log("list_names : " + str(list_names)) 
            if list_names:
                result = self.check_parenthesis_filename(subfolder, list_names)
            else:
                result = []
            log("list_names : " + str(list_names) + " and result : " + str(result)) 
            if result:
                file_path_old = join(ROOT_FOLDER,"Documents", appname, subfolder, result[0]) #"/storage/emulated/0/Documents/DeleteImage/"
                file_path_new = join(ROOT_FOLDER,"Documents", appname, subfolder, result[1]) #"/storage/emulated/0/Documents/DeleteImage/"
                self.delete_file_java(file_path_new)
                
                self.rename_file_java(file_path_old,file_path_new)
        log("--------- checkfilename end -------")

    def delete_all_android_dir_files(self,file_dir):
        # $deplace
        log("------ in delete_all_android_dir_files start ---- ")
        File = autoclass('java.io.File')
        if exists(file_dir):
            list_files = self.java_list_files(file_dir)
            for filename in list_files:
                file = File(join(file_dir,filename))
                file_deleted = file.delete()
                if file_deleted:
                    log("file deleted with success")
                else:
                    log("file not deleted")
                    log("fail to delete with java")
                    self.delete_file_python(join(file_dir,filename))

        log("------ in delete_all_android_dir_files end ---- ")

    def delete_file_java(self,file_path):
        # $deplace
        log("------ in delete_file_java start ---- ")
        File = autoclass('java.io.File')
        file = File(file_path) # "/storage/emulated/0/Documents/DeleteImage/subfolder" + filename
        file_deleted = file.delete()
        if file_deleted:
            log("file deleted with success")
        else:
            log("file not deleted")
            toast(self.current_lang["toast"][11])
            self.delete_file_python(file_path)

        log("------ in delete_file end ---- ")

    def delete_file_python(self,file_path):
        log("------ in delete file_python start ---- ")
        # $deplace
        if exists(file_path):
            try:
                remove(file_path)
                log("-----delete_file_python ---- The file has been removed")
                toast(self.current_lang["toast"][12])
            except Exception as e:
                e = traceback_format_exc()
                toast(self.current_lang["toast"][13])
                text_exception = "---- in delete_file_python error while deleting file with remove : " \
                " path is : " + str(file_path) + " : " + str(e)
                log(text_exception)
                self.check_exceptions(text_exception)

        else:
            log("------delete file_python------- The file does not exist")
            log("the file we want to python delete does not exist !")

        log("------ in delete file_python end ---- ")

    def rename_file_java(self,old_path,new_path):
        # $deplace
        log("--- start rename file_java----")
        File = autoclass('java.io.File')
        file_old = File(old_path)
        file_new = File(new_path)
        file_renamed = file_old.renameTo(file_new)
        if file_renamed:
            log("file renamed")
        else:
            log("file not renamed")

        log("--- end rename file_java----")

    def save_style_and_close(self, dialog):
        self.configbox.ids._configbox_field.text = self.font_style_checkbox

        if "menu" in self.configbox.ids._configbox_label.text:
            if not self.font_style_checkbox :
                self.configbox.ids._configbox_field.text = "Body2"
                self.font_style_menu = "Body2"
            else:
                self.font_style_menu= self.font_style_checkbox

            config_input["font_style_menu"] = self.font_style_menu

        if "Tiles" in self.configbox.ids._configbox_label.text:
            if not self.font_style_checkbox:
                self.configbox.ids._configbox_field.text = "Body1"
                self.font_style_tile = "Body1"
            else:
                self.font_style_tile = self.font_style_checkbox

            config_input["font_style_tile"] = self.font_style_tile
        save_config(config_input)
        dialog.dismiss()

    def java_list_files(self, path):
        ''' Tests showed that it is not working for shared file path. '''
        # <java.io.File at 0x72ee6ea930 jclass=java/io/File
        File = autoclass("java.io.File")
        directory = File(path)
        files = directory.listFiles()  # result is a list of <java.io.File at 0x72ee6ea930 jclass=java/io/File
        
        list_files = []
        if files:
            for file in files:
                if file.isFile():
                    list_files.append(file.getName())

        return list_files
    
    '''##################################################################################
                                Get uris functions
    ##################################################################################'''

    def get_uri_filesname_from_folder(self, shared_file): # xavier 0
        ''' Shared file must be like this join("Documents", "appname", "folder1", "subfolder1", etc...) '''

        path = shared_file.split('/') # ["Documents", "appname", "folder1", "subfolder1", etc...]
        root = path[0] # "Documents"
        filenames = []
        mimetype = "image/*"

        if api_version > 28:
            location = ''
            for d in path:
                location = join(location,d) # location = "Documents/appname/fold1"
            selection = MediaStoreMediaColumns.RELATIVE_PATH+"=?" # "relative_path=?"
            args = [location+'/'] # [file1.ext,"Documents/appname/fold1/"]
        else:
            selection = MediaStoreMediaColumns.DATA+"=?" # _data=?"
            args = [shared_file+"/"] # ["Documents/appname/fold1/fold2/file1.ext"]

        root_uri = self._get_root_uri(root, mimetype) #returns uri
        cursor = context.getContentResolver().query(root_uri, None,
                                                    selection, args,
                                                    None)
        if cursor: # begins at -1 so next is the first cursor
            while cursor.moveToNext():
                dn = MediaStoreMediaColumns.DISPLAY_NAME
                index = cursor.getColumnIndex(dn)
                fileName = cursor.getString(index)
                filenames.append(fileName)
            cursor.close()
        return filenames

    def _get_root_uri(self, root_directory, MIME_type):
        MediaStoreDownloads = autoclass('android.provider.MediaStore$Downloads')
        MediaStoreImagesMedia = autoclass('android.provider.MediaStore$Images$Media')
        MediaStoreVideoMedia = autoclass('android.provider.MediaStore$Video$Media')
        MediaStoreAudioMedia = autoclass('android.provider.MediaStore$Audio$Media')
        if root_directory == Environment.DIRECTORY_DOWNLOADS:
            root_uri = MediaStoreDownloads.EXTERNAL_CONTENT_URI
        else:
            root, ext = MIME_type.split('/')
            root = root.lower()
            if root == 'image':
                root_uri = MediaStoreImagesMedia.EXTERNAL_CONTENT_URI
            elif root == 'video':
                root_uri = MediaStoreVideoMedia.EXTERNAL_CONTENT_URI
            elif root == 'audio':
                root_uri = MediaStoreAudioMedia.EXTERNAL_CONTENT_URI
            else:
                root_uri = MediaStoreFiles.getContentUri('external')
        return root_uri

    def get_appname_by_uri(self, uri):
        uri_casted = cast('android.net.Uri', uri)
        path_notes_data = str(uri_casted.getPath()) #/document/home:CuistotdingoV20/data/note_data.py
        index_start =  path_notes_data.find(":")
        index_fin =  path_notes_data[index_start:].find("/")
        return path_notes_data[index_start+1:index_fin+index_start]
    
    def get_file_uri_provider(self, file_path, package_name):
        # Get the current Android activity context
        # mActivity is available in a Kivy application running on Android
        FileProvider = autoclass('androidx.core.content.FileProvider')
        File = autoclass('java.io.File')
        file_obj = File(file_path)
        # The authority must match the one defined in your AndroidManifest.xml
        authority = f"{package_name}.fileprovider"

        # Get the content URI using FileProvider.getUriForFile
        uri = FileProvider.getUriForFile(mActivity, authority, file_obj)
        
        return uri

    '''##################################################################################
                                Foreground functions
    ##################################################################################'''

    def set_default_rst_colors(self):
        # change rst color setting
        self.rstbox_paragraph_color = "202020ff"
        self.rstbox_title_color = "204a87ff"
        self.rstbox_bullet_color = "000000ff"
        self.rstbox_background_color = "ffffffcc"

    def segmented_activate(self, txt):
        match txt:
            case "Blue":
                self.change_appbar_color(self.blue_rgba_theme, self.white_rgba_80)
                self.change_nav_color(self.blue_rgba_theme, self.white_rgba_80)
                self.manager.screenA3.ids._tabs.change_tabs_color(self.blue_rgba_theme, 
                                                      self.blue_tabs_text_color_active, 
                                                      self.blue_tabs_text_color_inactive)

                # change screen backgroung
                self.main_theme_bg_color = self.white_rgba_theme
                self.mdbg_screen_edit_note = self.white_rgba_default

                # change screen textcolor
                self.change_screen_text_color(text_label_color = self.black_rgba_80, 
                                 text_textfield_color_normal = self.black_rgba_80,
                                 helper_textfield_color_focus = self.blue_rgba_theme,
                                 helper_textfield_color_normal = self.black_rgba_68,
                                 hint_textfield_color = self.black_rgba_38,
                                 speed_label_color = self.black_rgba_80,
                                 item_icon_button_color = self.black_rgba_80,
                                 unselect_icon_button_color = self.white_rgba_theme,
                                 line_textfield_color_normal = self.black_rgba_38,
                                 line_textfield_color_focus = self.blue_rgba_theme,
                                 separator_line_color = self.black_rgba_38,
                                 rvbox_rectangle_color = self.black_rgba_80,
                                 text_searchfield_color_normal= self.white_rgba_default,
                                 text_searchfield_color_focus= self.white_rgba_default,
                                 line_searchfield_color_normal= self.blue_rgba_theme,
                                 line_searchfield_color_focus= self.white_rgba_default,
                                 hint_searchfield_color_normal= self.white_rgba_80,
                                 colorpicker_icon_color = self.black_rgba_default,
                                 close_textfield_icon_color = self.white_rgba_default,
                                 text_notefield_color_normal = self.black_rgba_80)

                # change rst color setting
                self.set_default_rst_colors()

                # save config
                config_input["default_theme"] = "Blue"

            case "White":
                
                self.change_appbar_color(self.white_rgba, self.black_rgba_80)
                self.change_nav_color(self.white_rgba, self.black_rgba_80)
                self.manager.screenA3.ids._tabs.change_tabs_color(self.white_rgba, 
                                                      self.white_tabs_text_color_active, 
                                                      self.white_tabs_text_color_inactive)
            
                # change screen backgroung
                self.main_theme_bg_color = self.white_rgba_theme
                self.mdbg_screen_edit_note = self.white_rgba_default

                # change screen textcolor
                self.change_screen_text_color(text_label_color = self.black_rgba_80, 
                                 text_textfield_color_normal = self.black_rgba_80,
                                 helper_textfield_color_focus = self.blue_rgba_theme,
                                 helper_textfield_color_normal = self.black_rgba_68,
                                 hint_textfield_color = self.black_rgba_38,
                                 speed_label_color = self.black_rgba_80,
                                 item_icon_button_color = self.black_rgba_80,
                                 unselect_icon_button_color = self.black_rgba_80,
                                 line_textfield_color_normal = self.black_rgba_38,
                                 line_textfield_color_focus = self.blue_rgba_theme,
                                 separator_line_color = self.black_rgba_38,
                                 rvbox_rectangle_color = self.black_rgba_80,
                                 text_searchfield_color_normal = self.black_rgba_80,
                                 text_searchfield_color_focus = self.blue_rgba_theme,
                                 line_searchfield_color_normal= self.black_rgba_38,
                                 line_searchfield_color_focus= self.black_rgba_80,
                                 hint_searchfield_color_normal= self.black_rgba_80,
                                 colorpicker_icon_color = self.black_rgba_default,
                                 close_textfield_icon_color = self.black_rgba_default,
                                 text_notefield_color_normal = self.black_rgba_80)
                
                # change rst color setting
                self.set_default_rst_colors()

                # save config
                config_input["default_theme"] = "White"

            case "Black":
                black_rgba = hex_to_rgba(self.hex_dark_mode4)
                pink_rgba_hex = rgba_to_hex(1, 0.396078431372549, 0.8470588235294118, 1.0)

                self.change_appbar_color(black_rgba,self.white_rgba_80)
                self.change_nav_color(black_rgba,self.white_rgba_80)
                self.manager.screenA3.ids._tabs.change_tabs_color(black_rgba, 
                                                      self.blue_tabs_text_color_active, 
                                                      self.blue_tabs_text_color_inactive)

                # change screen backgroung
                self.main_theme_bg_color = self.black_rgba_theme
                self.mdbg_screen_edit_note = self.main_theme_bg_color

                self.change_screen_text_color(text_label_color = self.white_rgba_80, 
                                 text_textfield_color_normal = self.white_rgba_80,
                                 helper_textfield_color_focus = self.theme_cls.primary_dark,
                                 helper_textfield_color_normal = self.white_rgba_68,
                                 hint_textfield_color = self.white_rgba_68,
                                 speed_label_color = self.white_rgba_80,
                                 item_icon_button_color = self.white_rgba_80,
                                 unselect_icon_button_color = self.white_rgba_80,
                                 line_textfield_color_normal = self.white_rgba_38,
                                 line_textfield_color_focus = self.theme_cls.primary_dark,
                                 separator_line_color = self.white_rgba_38,
                                 rvbox_rectangle_color = self.white_rgba_68,
                                 text_searchfield_color_normal = self.white_rgba_80,
                                 text_searchfield_color_focus = self.blue_rgba_theme,
                                 line_searchfield_color_normal= self.black_rgba_theme,
                                 line_searchfield_color_focus= self.blue_rgba_theme,
                                 hint_searchfield_color_normal= self.white_rgba_80,
                                 colorpicker_icon_color = self.white_rgba_default,
                                 close_textfield_icon_color = self.white_rgba_default,
                                 text_notefield_color_normal = self.white_rgba_80)

                # change rst color setting
                self.rstbox_paragraph_color = "e5e6e9ff"
                self.rstbox_title_color = "ff65d8ff"
                self.rstbox_bullet_color = "ce5c00ff"
                self.rstbox_background_color = "262730ff" # black_rgba_theme

                # save config
                config_input["default_theme"] = "Black"


            case "French":
                self.current_lang = lang_fr
                config_input["language"] = "French"
                Clock.schedule_once(self.appbar.restore_appbar_after_language,0)

            case "English":
                self.current_lang = lang_en
                config_input["language"] = "English"
                Clock.schedule_once(self.appbar.restore_appbar_after_language,0)

        save_config(config_input)

    def change_appbar_color(self,appbar_color, action_color):
        self.appbar.md_bg_color = appbar_color
        self.appbar.specific_text_color = action_color #  for the icons button

    def change_nav_color(self,rgba_color, text_icon_color):
        self.navigation.md_bg_color = rgba_color
        icon_name = self.navigation.ids._grid_navigation.last_button
        id = "_" + icon_name
        self.navigation.ids[id].children[0].text_color = text_icon_color
        self.navigation.ids[id].children[1].text_color = text_icon_color
        NavigationRelativeLayout.icon_color_active = text_icon_color
        NavigationRelativeLayout.text_color_active = text_icon_color

    def change_screen_text_color(self,text_label_color = [0,0,0,0.8], 
                                 text_textfield_color_normal = [0,0,0,0.8],
                                 helper_textfield_color_focus = [0.12941176470588237, 0.5882352941176471, 0.9529411764705882, 1.0],
                                 helper_textfield_color_normal = [0.5, 0.5, 0.5, 1.0],
                                 hint_textfield_color = [1, 1, 1, 0.38],
                                 speed_label_color = [0,0,0,0.8],
                                 item_icon_button_color = [0,0,0,0.8],
                                 unselect_icon_button_color = [1,1,1,0.8],
                                 line_textfield_color_normal = [0.5, 0.5, 0.5, 1.0],
                                 line_textfield_color_focus = [0.12941176470588237, 0.5882352941176471, 0.9529411764705882, 1.0],
                                 separator_line_color = [0,0,0,0.38],
                                 rvbox_rectangle_color = [0,0,0,0.38],
                                 text_searchfield_color_normal = [1,1,1,0.8],
                                 text_searchfield_color_focus = [1,1,1,0.8],
                                 line_searchfield_color_normal = [1,1,1,1],
                                 line_searchfield_color_focus = [1,1,1,1],
                                 hint_searchfield_color_normal = [1,1,1,1],
                                 colorpicker_icon_color = [0,0,0,1],
                                 close_textfield_icon_color = [1,1,1,1],
                                 text_notefield_color_normal = [0,0,0,0.8] ):
                                 

        self.text_label_color = text_label_color
        self.text_textfield_color_normal = text_textfield_color_normal
        self.helper_textfield_color_focus = helper_textfield_color_focus
        self.helper_textfield_color_normal = helper_textfield_color_normal
        self.hint_textfield_color = hint_textfield_color
        self.speed_label_color = speed_label_color
        self.item_icon_button_color = item_icon_button_color
        self.unselect_icon_button_color = unselect_icon_button_color
        self.line_textfield_color_normal = line_textfield_color_normal
        self.line_textfield_color_focus = line_textfield_color_focus
        self.line_textfield_note_color_normal = self.main_theme_bg_color
        self.separator_line_color = separator_line_color
        self.rvbox_rectangle_color = rvbox_rectangle_color
        self.text_searchfield_color_normal = text_searchfield_color_normal
        self.text_searchfield_color_focus = text_searchfield_color_focus
        self.line_searchfield_color_normal = line_searchfield_color_normal
        self.line_searchfield_color_focus = line_searchfield_color_focus
        self.hint_searchfield_color_normal = hint_searchfield_color_normal  
        self.colorpicker_icon_color = colorpicker_icon_color
        self.close_textfield_icon_color = close_textfield_icon_color
        self.text_notefield_color_normal = text_notefield_color_normal

    '''##################################################################################
                                Others functions
    ##################################################################################'''

    def replace_tile(self,tile, key, instruction, title, ingredients, commentaire, nb_personne, saison, astuces, source_recette):
        ''' Was added in order to factorize all replacements '''

        tile.text = title # -n car les index sont inversés, premier ajouté = dernier dans l'arborescence
        tile.description = instruction
        tile.opacity = 1
        tile.index_picture = key
        tile.ingredients = ingredients
        tile.commentaire = commentaire
        tile.nb_personne = nb_personne
        tile.saison = saison
        tile.astuces = astuces
        tile.source_recette = source_recette

        source_after = join("images", "recipes", key + ".jpg")

        if exists(source_after):
            tile.ids.image.source = source_after #$source runtime

        # unload picture if no matching
        else:
            tile.ids.image.source = source_image_default # added to solve the image not corresponding to the tile

    @staticmethod
    def get_widgets(root: WeakProxy, class_: list):
        ''' :param root: root widget
            :param class_: which subclass are we looking for
            :returns wigets tree '''
            
        widgets = []
        for widget in root.walk(): # Iterator that walks the widget tree starting with this widget and goes forward returning widgets in the order in which layouts display them.
            if widget.__class__.__name__ in class_:
                widgets.append(widget)

        return widgets
    
    def delay_focus_true(self, instance_field, dt):
        ''' Because the color is not set when textfield is empty, we fake a click, 
        it seems to work, even if it is a bit dubious. '''

        instance_field.on_focus(self,instance_field.focus)
        Clock.schedule_once(partial(self.delay_focus_false, instance_field), 3)

    def delay_focus_false(self, instance_field, dt):
        instance_field.on_focus(self,instance_field.focus)
    
    def rule_validate(self, code_text, field_text):
        ''' Use to make rule for config widgets and concatenate the code. '''
        
        if field_text:
            match code_text:
                case "size_hint_y_appbar":
                    self.size_hint_appbar = field_text
                    config_input["size_hint_appbar"] = float(field_text)
                    # self.appbar.change_appbar_component_pos()
                    save_config(config_input)

                case "center_y_note_item":
                    self.center_y_note_item = float(field_text)
                    config_input["center_y_note_item"] = float(field_text)
                    save_config(config_input)

                case "unselect_note_x":
                    self.appbar.validate_unselect_icon_x(field_text)

                case "unselect_note_y":
                    self.appbar.validate_unselect_icon_y(field_text)

                case "search_textfield_y":
                    self.appbar.validate_search_textfield_y(field_text)

                case "ingredient_button_size":
                    self.font_size_button_ingredient = float(field_text)
                    config_input["ingredient_button"] = float(field_text)
                    save_config(config_input)

                case "size_hint_y_nav":
                    self.size_hint_navigation = float(field_text)
                    config_input["size_hint_navigation"] = float(field_text)
                    save_config(config_input)

                case "mdtabs_height":
                        self.manager.screenA3.ids._tabs.tab_bar_h = field_text + "dp"
                        config_input["tab_bar_h"] = field_text + "dp"
                        save_config(config_input)

                case "separator_padding_y":
                    self.separator_padding_y = field_text
                    config_input["separator_padding_y"] = field_text
                    save_config(config_input)

                case "font_style_menu":
                    if field_text not in theme_font_styles[5:14]:
                        self.show_font_style_dialog()
                    else:
                        self.font_style_menu = field_text
                        config_input["font_style_menu"] = self.font_style_menu
                        save_config(config_input)

                case "font_style_tile":
                    if field_text not in theme_font_styles[5:14]:
                        self.show_font_style_dialog()
                    else:
                        self.font_style_tile = field_text
                        config_input["font_style_tile"] = self.font_style_tile
                        save_config(config_input)

                case "font_size_nav":
                    self.font_size_nav = field_text
                    config_input["font_size_nav"] = field_text
                    save_config(config_input)

                case "calcul_screen":
                    self.manager.transition.direction = "up" # $transition
                    if not self.manager.screen_calcul_loaded: 
                        self.manager.load_calcul_screen()
                    self.manager.edit_full_screen()
                    self.manager.current = "screen calcul"

                case "season_screen_google":
                    
                    if platform in ["android", "ios"]:
                        path_season = join("Documents", appname, "images","season","saison_legumes_" + field_text + ".png")
                        self.open_season_pictures(path_season) 
                    else:
                        path_season = join("Documents", "CuistotDingo", "images","season","saison_legumes_" + field_text + ".png")
                        self.open_season_with_scatter()

                case "restore_inactive_note_bg_color":
                    self.manager.screenD2.ids._unselected_note_color_field.text = "#f8f5f4ff"
                    if not self.manager.screen_e1_loaded:
                        self.manager.load_E1_screen()
                    self.manager.screenE1.ids._colorpicker.label_id = "_unselected_note_color_field"
                    self.manager.screenE1.ids._colorpicker.hex_color = "#f8f5f4ff"
                    self.manager.screenE1.ids._colorpicker.change_picker_color("#f8f5f4ff")
                    toast(self.current_lang["toast"][14])

                case "restore_active_note_bg_color":
                    self.manager.screenD2.ids._selected_note_color_field.text = "#f4b5b5ff"
                    if not self.manager.screen_e1_loaded:
                        self.manager.load_E1_screen()
                    self.manager.screenE1.ids._colorpicker.label_id = "_selected_note_color_field"
                    self.manager.screenE1.ids._colorpicker.hex_color = "#f4b5b5ff"
                    self.manager.screenE1.ids._colorpicker.change_picker_color("#f4b5b5ff")
                    toast(self.current_lang["toast"][15])

                case "recipes_backup":
                    self.create_backup_recipes()

                case "notes_backup":
                    self.create_backup_note_data()

                case "ingredients_backup":
                    self.create_backup_ingredients_data()

                case "load_recipes_data":
                    self.show_load_recettes_dialog()

                case "help_section":
                    self.show_help_dialog()

                case "test_section":
                    self.test_section()

                case "load_notes_data":
                    self.show_load_notes_dialog()

                case "load_saison_data":
                    self.show_load_saison_dialog()

                case "load_ingredients_data":
                    self.show_load_ingredients_dialog()

    def generate_picture_note_name(self):
        title_note = self.manager.screenEditNote.ids["_note_box"].note_selected.title
        current_time = self.get_current_time()
        picture_basename = title_note + "_" + current_time + ".jpg"
        return picture_basename
    
    def create_backup_recipes(self):
        '''  There was a bug weird join("core","input_recettes.py") is not recognized so we try .pyc
        so we add open as f and f.write and it worked. Called whenever the user select create backup in config
        Create backup and save it to backup folder '''

        log(" ----- start create backup recipes ----")
        current_time = self.get_current_time()
        source = join("core","input_recettes.py")
        dest = join("data","backup", "input_recettes_backup_" + current_time + ".py")

        if platform in ["android", "ios"]:
            
            json_recettes = json_dumps(recettes, ensure_ascii=False, indent= 4)
            with open(join("core","input_recettes.py"), 'w',encoding='utf-8') as f:
                f.write("recettes = " + str(json_recettes))

            self.save_to_shared(source, dest)
            dir = join("data","backup")
            self.checkfilename(dir)

        else:
            try:
                copyfile(source, dest)
            except FileNotFoundError:
                # there is no app folder so we create it,
                log("in create backup recipes creating the folder " + join("data","backup") + "for strorage purpose")
                makedirs(join("data","backup"), exist_ok = True)
                copyfile(source, dest)

        log(" ----- end create backup recipes ----")

    def create_backup_note_data(self):
        ''' Called whenever the user select create backup in config
        Create backup and save it to backup folder '''

        # 1 : save the file note_data to backup folder
        current_time = self.get_current_time()
        source = join("data","note_data.py")
        dest = join("data","backup", "note_data_backup" + current_time + ".py")

        if platform in ["android", "ios"]:
            # this code whom seems dumb is needed otherwise there is no file created...
            json_note_data = json_dumps(note_data, ensure_ascii=False, indent= 4)
            with open(join("data","note_data.py"), 'w',encoding='utf-8') as f:
                f.write("CODE_NOTES = " + '"' + CODE_NOTES + '"'  + "\n" +
                        "note_data = " + str(json_note_data) + "\n" +
                            "note_index = " + str(note_index))

            self.save_to_shared(source, dest)
            dir = join("data","backup")
            self.checkfilename(dir)

        else:
            try:
                copyfile(source, dest)
            except FileNotFoundError:
                # there is no app folder so we create it,
                log("in create_backup_note creating the folder " + join("data","backup") + "for strorage purpose")
                makedirs(join("data","backup"), exist_ok = True)
                copyfile(source, dest)

        # 2 : delete backup images files
        if platform in ["win","macos","linux","unknown"]:
            backup_images_folder = join("data", "backup","images")
            if exists(backup_images_folder):
                backup_images_list = self.java_list_files(backup_images_folder)
                for filename in backup_images_list:
                    file_path = join(backup_images_folder, filename)
                    
                    # Check if it is a file (not a subdirectory)
                    if isfile(file_path):
                        remove(file_path)  # Remove the file

        elif platform in ["android", "ios"]:
            backup_images_folder = join(ROOT_FOLDER,"Documents", appname, "data", "backup","images")
            try:
                self.delete_all_android_dir_files(backup_images_folder)
            except Exception as e:
                e = traceback_format_exc()
                log("---- error in create_backup_note_data while deleting all shared files : " + str(e))
                text_exception = "---- Error in create_backup_note_data while deleting all shared files : " + str(e)
                self.check_exceptions(text_exception)

    def create_backup_ingredients_data(self):
        '''Called whenever the user select create backup in config
        Create backup and save it to backup folder'''

        log(" ----- start create backup ingredients ----")
        current_time = self.get_current_time()
        source = join("core","input_frigo.py")
        dest = join("data","backup", "input_frigo_backup_" + current_time + ".py")

        if platform in ["android", "ios"]:
            json_mydico_frigo = json_dumps(mydico_frigo, ensure_ascii=False, indent= 4)
            with open(join("core","input_frigo.py"), 'w',encoding='utf-8') as f:
                f.write("mydico_frigo = " + str(json_mydico_frigo))
           
            self.save_to_shared(source, dest)
            dir = join("data","backup")
            self.checkfilename(dir)

        else:
            try:
                copyfile(source, dest)
            except FileNotFoundError:
                # there is no app folder so we create it,
                log("in create backup ingredients creating the folder " + join("data","backup") + "for strorage purpose")
                makedirs(join("data","backup"), exist_ok = True)
                copyfile(source, dest)

        log(" ----- end create backup ingredients ----")

    def test_section(self):

        if platform in ["android", "ios"]:
            file_dir_documents = join("images","recipes")
            list_files = self.java_list_files(file_dir_documents)
            log(" files recipes in private file are : " + str(list_files))

            file_dir_documents = join(ROOT_FOLDER,"Documents", appname,"images","recipes")
            list_files = self.java_list_files(file_dir_documents)
            log(" files recipes in shared file are : " + str(list_files))      

        shared_path = join("Documents", appname, "images","recipes", "64.jpg")
        abs_shared_path = join(ROOT_FOLDER, "Documents", appname, "images","recipes", "64.jpg")
        

        uri1 = library.getUriFromAbsoluteFilePath(context, join(ROOT_FOLDER, abs_shared_path))
        uri2 = library.getMediaStoreUriFromFilePath(context, join(ROOT_FOLDER, shared_path))
        uri3 = library.getMediaStoreUriFromFilePath(context, join(ROOT_FOLDER, abs_shared_path))
        uri4 = self.get_file_uri_provider(join(ROOT_FOLDER, abs_shared_path), "cuistotdingov24")

        log("uri 1 is : " + str(uri1))
        log("uri 2 is : " + str(uri2))
        log("uri 3 is : " + str(uri3))
        log("uri 4 is : " + str(uri4))

    def get_current_time(self):
        # $deplace
        ''' This function is used to generate a unique string use like a title picture name
        we could have use datetime.now().strftime("%Y_%m_%d_etc..") but title will be maybe too long. '''

        time = datetime.today()
        year = str(time.year)
        month = str(time.month)
        day = str(time.day)
        hour = str(time.hour)
        minute = str(time.minute)
        return day + "_" + month + "_" + year + "_" + hour + "h" + "_" + minute

    def optimize_loading_A4_screen(self, nb_tiles):
        # create the invisible tiles for the A4 screen to optimise time response
        if not self.manager.screen_a4_loaded:
            self.manager.load_A4_screen()
        nb_tiles_current = len(self.manager.screenA4.ids._rvgrid.children)
        if nb_tiles_current < max_ingredient - nb_tiles -1:
            self.manager.create_invisible_a4_tile(nb_tiles)

    def get_missing_ingredient(self, tile_A0):
        stack_b1_list = []
        for ing in mydico_frigo["ingredients"].keys():
           stack_b1_list.append(ing)

        ingredients_recipe = tile_A0.ingredients
        
        for ingredient in ingredients_recipe:
            if ingredient not in stack_b1_list:
                return ingredient
        
    def set_a0_ingredient_text(self, A0_tile):
        ''' change the a0 text and color the ingredient missing screen A1 '''

        ingredients_list = A0_tile.ingredients.copy() # copy needed here to not modify original list
        
        if self.manager.current == "screen A2":
            missing_ingredient = self.get_missing_ingredient(A0_tile)
            ingredients_list.remove(missing_ingredient)
            ingredients = str(ingredients_list)[1:-1]
            if len(ingredients) > 1 :
                ingredients = f"{ingredients}, [color=#ff65d8ff][b]'{missing_ingredient}'[/b][/color]"
            else:
                ingredients = f"[color=#ff65d8ff][b]'{missing_ingredient}'[/b][/color]"

        else:
            ingredients = str(ingredients_list)[1:-1]
        
        self.manager.screenA0.ids._ingredients.text = ingredients

    def restore_screen_transition(self):
        ''' added because of the edit full_screen() generating weird transition screen behavior '''
        self.manager.transition.direction = "left"

    def nb_recipe_returned(self, nb_match):
        ''' Change the number of string match when using home made function to search a recipe '''
        nb_recipes = len(recettes["recipes"])
        if nb_recipes < nb_match :
            nb_match = nb_recipes
        return nb_match
    
CuistotDingoApp().run()
