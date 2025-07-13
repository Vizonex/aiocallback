# aiocallback:
[![PyPI version](https://badge.fury.io/py/aiocallback.svg)](https://badge.fury.io/py/aiocallback)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aiocallback)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)



An asynchronous helper framework for writing custom event wrapper class functions made with good typehinting that is based off [aiosignal](https://github.com/aio-libs/aiosignal) with better modifications added for better typehinting and easier usage with tools such as pyright or mypy allowing for arguments to be properly typehinted at when performing any created callback which ultimately means less confusion and more action.

One of my biggest pet peves of all time is when **static type-checkers don't pick up what functions parameters are being used**. This library aims to fix static typecheckers when send() functions are being used, 
 so that developers aren't second guessing what different paremeters are needed. This is a big advantage over aiosignal and was the main reson behind it's creation.
 
<img src="https://raw.githubusercontent.com/Vizonex/aiocallback/main/Typehinting-Example.png" width="500px"/>






# Usage:
Aiocallback should be used when dealing with creating custom context objects or callbacks. An example might be scraping an api by a given hour 
and calling for that data that can be defined by multiple functions. However, there are many more creative ways to use this library.

## Dependencies
- [frozenlist](https://github.com/aio-libs/frozenlist) we dropped aiosignal in favor of frozenlist temporarly until aiosignal plans to support __ParamSpec__ There isn't much demand for it yet but I did help revive that library recently. 
- [typing-extensions](https://github.com/python/typing_extensions) Typehinting for Python 3.9, plan to drop typing-extensions when 3.9 hits End of Life so that __ParamSpec__ can be utilized to it's fullest potential.


## Installing

The easiest way is to install **aiocallback** is from PyPI using pip:

```sh
pip install aiocallback
```

## Running

First, import the library.

```python
from aiocallback import event, subclassevent, contextevent
import asyncio

class Config:
    """an example of configuring callbacks"""

    # NOTE: Typehinting will be passed to other objects 
    # Thanks in largepart to ParamSpec and Concatenate
    
    # NOTE: @event considers the function to be an abstract method, However you can use a subclassevent to retain typechecking if you need something that isn't so abstract
    @event
    async def on_print(self, cb:str):
        """callbacks for a print method"""

    @subclassevent
    async def on_nonabstract(self, cb:str):
        """a nonabstract method can be called with other events as being part of the signal"""
        print(f"I am callable! \"{cb}\"")




cfg = Config()
# You can also call the append method just like with aiosignal as ours is primarly a subclass of it.
@cfg.on_print
async def test(cb:str):
    print(f"called test {cb}")



async def main():
    # This uses aiosignal under the hood so remeber to freeze the callbacks when your setup is complete
    cfg.on_print.freeze()
    cfg.on_nonabstract.freeze()

    await cfg.on_print.send("Hello world")
    await cfg.on_nonabstract.send("Hello world")

if __name__ == "__main__":
    asyncio.run(main())

```

## Using EventLists
There's an alternative way to use aiocallback where you don't need to freeze many Configurable event descriptors at a time. You should use it if your not planning to use a dataclass although we plan to implement a special EventList for msgspec.

```python
from aiocallback import EventList, event

class MyEvents(EventList):
    @event
    async def on_event(self, item:str):...

events = MyEvents()
# all events get frozen for you and this method is built-in.
events.freeze()

```

## Links
- [Tutorial](https://youtu.be/Ly_G1CstOfA)

## Alternatives
- [aiosignal](https://github.com/aio-libs/aiosignal) I am a contributor over there as well and we're making some intresting imporvements over there so keep your eyes peeled.


# TODOS
- [ ] Trusted Publishing
- [ ] Smaller improvements to aiocallback like documentation for future readthedocs page.
