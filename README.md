Fontforge plugin helper
=======================

A collection of common routines for Fontforge plugins

This module is intended to be called from Fontforge plugins.
This module itself is not a Fontforge plugin.

Install
-------

```shell
pip3 install fontforge_plugin_helper
```

Usage
-----

### Bézier-related features

#### fontforge_plugin_helper.getInterpolatedCoord()

```python
contour = font['A'].layers[1][0]
x, y = fontforge_plugin_helper.getInterpolatedCoord(contour, 1.5)
```

#### fontforge_plugin_helper.getTangentAngle()

```python
contour = font['A'].layers[1][0]
tangentAngle = fontforge_plugin_helper.getTangentAngle(contour, 1.5)
```

### Hook-related features

#### fontforge_plugin_helper.addSystemHook()

```python
def myNewFontHook(font):
    do_something


def myLoadFontHook(font):
    do_something


def fontforge_plugin_init(**kw):
    fontforge_plugin_helper.addSystemHook('newFontHook', myNewFontHook)
    fontforge_plugin_helper.addSystemHook('loadFontHook', myLoadFontHook)
```

#### fontforge_plugin_helper.addFontGenerateHook()

```python
def myPreGenerationHook(font):
    do_something


def myPostGenerationHook(font):
    do_something


def myNewOrLoadFontHook(font):
    fontforge_plugin_helper.addFontGenerateHook(font,
                                                'generateFontPreHook',
                                                myPreGenerationHook)
    fontforge_plugin_helper.addFontGenerateHook(font,
                                                'generateFontPostHook',
                                                myPostGenerationHook)


def fontforge_plugin_init(**kw):
    fontforge_plugin_helper.addSystemHook('newFontHook', myNewOrLoadFontHook)
    fontforge_plugin_helper.addSystemHook('loadFontHook', myNewOrLoadFontHook)
```

#### fontforge_plugin_helper.generationHookSetter()

```python
def myPreGenerationHook(font):
    do_something


def myPostGenerationHook(font):
    do_something


def fontforge_plugin_init(**kw):
    fontforge_plugin_helper.addSystemHook(
        'newFontHook',
        fontforge_plugin_helper.generationHookSetter(
            myPreGenerationHook,
            myPostGenerationHook,
        )
    )
    fontforge_plugin_helper.addSystemHook(
        'loadFontHook',
        fontforge_plugin_helper.generationHookSetter(
            myPreGenerationHook,
            None,  # if not needed
        )
    )
```

### Translation-related features

#### class fontforge_plugin_helper.Translations

```python
tr = fontforge_plugin_helper.Translations()

def spam(u, font):
    pass

def fontforge_plugin_init(**kw):
    tr.set('fr', '_Open', '_Ouvrir')
    tr.setTranslations('fr', {
        '_Open': '_Ouvrir',
        '_Close': '_Fermer',
        '_MyMenu': '_MonMenu',
    })
    tr.setTranslations('de', {
        '_Open': 'Ö_ffnen',
        '_Close': 'S_chließen',
        '_MyMenu': '_MeinMenü',
    })
    fontforge.registerMenuItem(
        callback=spam,
        context="Font",
        name=tr.get('_MyMenu')
    )
```
