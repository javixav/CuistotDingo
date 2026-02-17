# CuistotDingo
A minimalist kivy app, that allows you to save recipes, search by name, take notes, find recipes by ingredient, and find recipes depending on what you have in your fridge

<img align="right" height="256" src="https://github.com/javixav/CuistotDingo/tree/main/images/CuistotDingo.png"/>

### Dependencies:
The app was tested on android API 29 with those dependencies (works also on desktop tested on Winwdows 10).

- [Kivy](https://github.com/kivy/kivy) = 2.3.1 ([Installation](https://kivy.org/doc/stable/gettingstarted/installation.html))
- [Python 3.7+](https://www.python.org/)
- [Pillow](https://github.com/python-pillow/Pillow/)
- [MaterialColor](https://github.com/T-Dynamos/materialyoucolor-python)
- [asynckivy](https://github.com/asyncgui/asynckivy)
- [filetype](https://pypi.org/project/filetype/)
- [docutils](https://pypi.org/project/docutils/)
- [gestures4kivy](https://pypi.org/project/gestures4kivy/)
- [camera4kivy](https://github.com/Android-for-Python/Camera4Kivy)
- [androidstorage4kivy](https://github.com/Android-for-Python/Androidstorage4kivy)
- [unidecode](https://pypi.org/project/Unidecode/)

### How to install
1. You need to generate the apk file with buildozer. Follow procedure [here](https://www.youtube.com/watch?v=BDdQJ0zHSW0)
2. When you'll generate the first apk, you need to edit the AndroidManifest.tmpl.xml file located in \.buildozer\android\platform\build-arm64-v8a\dists\cuistotdingov24\templates\AndroidManifest.tmpl.xml and add android:requestLegacyExternalStorage="true" to the <application tag.This ensure that you will be able to have Write access to android storage. Then if you want you're app not to be killed when memory is needed, or at least rebuild your app if it was killed by android, you'll need to open PythonService.java loacated in
.buildozer\android\platform\build-arm64-v8a\dists\cuistotdingov24\src\main\java\org\kivy\android\PythonService.java

and change START_NOT_STICKY to START_STICKY
public int startType() {
    return START_STICKY; 
}
4. Rebuild the app doing buildozer -v android debug and install the new apk generated.

## About the app
  The home screen is the screen A1, where are shown recipes that you can cook from what you have in your fridge. You can then navigate to the screen called A2, that shows recipes that you can cook with one more ingredient. The screen A3 is the screen where you can see all your recipes. For performance purpose and because rendering a lot of widget, images, is time consuming I tried to divide the number of visible recipes. The A4 screen is the screen where you can find a recipe depending on what ingredient you wanna cook. The A5 screen is the screen where you can add a new recipe.
  You can take picture, piture image is downgraded for performance purpose, but you can still view the full screen image with a good resolution thanks to java and opening an intent with google picture.
  
  Screen B1 is opened clicking in the navigation bar ans is the Stock screen where you can edit you're sotck ingredient.
  Screen C1 is the screen where you can take notes, about you're culinary experiences, and add some nice features like RST Text.
  Screen D1-D2-D3-D4 are setting screens, where you can edit the language, the theme color, and other settings.

  In the TopApp bar, you'll find a magnifying glass icon that allows you to filter recipes by name.

## About the code and author
  The app's main code and app structure is a bit messy as you'll see if you analyse it deeply or not... Why because it is my first python project, and fist programming project and I'm not a professionnal developer, just a cook that wanted to record nice recipes. To this point it took me like 5 years or more to develop this app (yeaah I know), but I am glad I can publish it in open source and let the community improve it and enjoy it. Some word are in french because it is my native language and english is not my strength.

## Contributing
I'll be happy if you want to contribute : still there is a lot to do to improve the app like :  
    - make the last seen note be at the top  
    - check saison.csv translate for english versions...  
    - make the app IOS compatible thanks to [kivyschool](https://kivyschool.com/kivy-on-ios/) and [kivy-ios](https://kivy.org/doc/stable/guide/packaging-ios.html)  
    - check android api compatibility, this one is compatible with Api 29, the one I use for the tests, if you know a way to test it for others api or make it compatible, be my guest.  
    - Add to each recipe, the data ingredients quantity : The ingredient quantity are in the corpus of the recipe, a big improvement would be to make it independent.  
    - add an icon to reset all ingredients in stack screen.  
    - Make code smarter : Factorize code, Check for unused code, make it prettier and faster.  




