# aiocallback:
[![PyPI version](https://badge.fury.io/py/aiocallback.svg)](https://badge.fury.io/py/aiocallback)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aiocallback)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)


An asynchronous helper toolbag for writing callback systems at a medeium level. For now many things are being moved to aioplugin but soon as the project stablizies this library will be getting some old/newer features back. For now if you still need a few things I recommend trying aioplugin for now...

# Usage:
Aiocallback should be used when dealing with creating custom context objects or callbacks. An example might be scraping an api by a given hour 
and calling for that data that can be defined by multiple functions. However, there are many more creative ways to use this library.

## Dependencies
- [frozenlist](https://github.com/aio-libs/frozenlist) we dropped aiosignal in favor of frozenlist since it's funtionality is not yet needed
and can simply being copied over and modified.
- [typing-extensions](https://github.com/python/typing_extensions) Typehinting for Python 3.9, plan to drop typing-extensions when 3.9 hits End of Life so that __ParamSpec__ can be utilized to it's fullest potential.


## Installing

The easiest way is to install **aiocallback** is from PyPI using pip:

```sh
pip install aiocallback
```

## Links
- [Tutorial](https://youtu.be/Ly_G1CstOfA) **Obsolete** Items descussed are being deprecated.

## Alternatives
- [aiosignal](https://github.com/aio-libs/aiosignal) I am a contributor over there and I revived this project pretty recently. It's a very good replacement if you want speed and don't require anything fancy from here.
- [aioplugin](https://github.com/Vizonex/aioplugin) A Promising rewrite of this library meant to provide an upper level for this library
in the future. EventLists are essentially being renamed to plugins which is pretty neat :)
