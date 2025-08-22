
aiocallback documentation
===============================

**aiocallback** is made for being simple but when needing highly documented callbacks 
for by transforming class methods to member descriptors for other developers or 
yourself having to memorize everything done can be tricky and costly.
When chaining together multiple callbacks like you may consider doing with 
`aiosignal <https://aiosignal.aio-libs.org/en/stable/>`__ typehinting keyword arguments 
is still one of it's weaknesses. My goal was to provide users more options with creating
and chaining callbacks together without murduring any rich documentation that you may
wish to tell other developers or users about.

What makes aiocallback different from aiosignal?
------------------------------------------------
-  **aiocallback** is more beginner friendly and is primarly an alternative resource for users
   who want to create prettier libraries or software and are not worried about the amount of 
   time it takes to write such a task.

-  **aiocallback** uses :py:class:`typing.ParamSpec` for it's typehints which means the sending 
   events will retain these typehints. If your utilizing tools like VsCode with the pyright extension 
   this can come in handy as your ide will hint the functions needed for sendoff. 

-  **aiocallback** is inspired by the approch that `discordpy <https://discordpy.readthedocs.io>`__ takes except made a bit easier than 
   when you would go to configure a discord bot in python.

-  When needing to freeze hundereds of events aiosignal can become quite the hassle to freeze all of them. **aiocallback**'s :class:`EventList` 
   class could help you freeze these items if they are instead transformed into member descriptors which means that you no longer have to setup
   these items with an ``__init__`` function.

-  **aiocallback** has what I would consider a `FastAPI <https://fastapi.tiangolo.com>`__ like experience where the frontend is kept clean and neat. 
   if you like `FastAPI <https://fastapi.tiangolo.com>`__ and decorators you'll enjoy **aiocallback** as well. 

When is aiosignal a better choice?
----------------------------------
-  `aiosignal <https://aiosignal.aio-libs.org/en/stable/>`__ has recently been revived and I also am one of the newer maintainers of this library
   who helped with it's revival. If your all about being quick and dirty and aren't needing 
   complete safety that **aiocallback** may provide and you don't want to stress over heavy 
   documentation go ahead and use it. 
   
-  I help maintain this one and there's zero competition between the two
   libraries. They both serve different purposes and needs that a developer or user may wish on having. 

-  `aiosignal <https://aiosignal.aio-libs.org/en/stable/>`__ is a bit quicker and dirtier than this library and 
   if you don't need all the bells and whistles that **aiocallback** may offer it's a better choice over it. 

-  If you don't care about being impressive it's a neat little alternative to this library and I hope you are successful with both 
   this library and the other one.



Installation
------------

.. code-block:: bash

   $ pip install aiocallback

The library requires Python 3.9 or newer.

API
---


.. automodule:: aiocallback
   :members:
   :special-members: __call__
   


.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _GitHub: https://github.com/Vizonex/aiocallback

