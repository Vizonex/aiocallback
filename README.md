# aiocallback:
[![PyPI version](https://badge.fury.io/py/aiocallback.svg)](https://badge.fury.io/py/aiocallback)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aiocallback)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)


An asynchronous helper for writing custom event wrapper class functions and is a good framework for library development made with good typehinting that is built around [aiosignal](https://github.com/aio-libs/aiosignal) under the hood with a few modifications added onto it for better typehinting and easy usage. You will find this to be simillarly inspired to the way aiohttp's traceconfig is used but made a bit easier.


One of my biggest pet peves of all time is when **callbacks are not being properly hinted at**. This library aims to fix that for vscode and other ides such as when calling the send() function.

<img src="https://raw.githubusercontent.com/Vizonex/aiocallback/main/Typehinting-Example.png" width="500px"/>



# Usage:

## Dependencies

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
    # This uses aiosignal under the hood so remember to freeze the callbacks when your setup is complete
    cfg.on_print.freeze()
    cfg.on_nonabstract.freeze()

    await cfg.on_print.send("Hello world")
    await cfg.on_nonabstract.send("Hello world")

if __name__ == "__main__":
    asyncio.run(main())

```

# TODO:

- [X] pypi release
