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

### fontforge_plugin_helper.addSystemHook()

```python
def myNewFontHook(font):
    do_something


def myLoadFontHook(font):
    do_something


def fontforge_plugin_init(**kw):
    fontforge_plugin_helper.addSystemHook('newFontHook', myNewFontHook)
    fontforge_plugin_helper.addSystemHook('loadFontHook', myLoadFontHook)
```
