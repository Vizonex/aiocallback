
aiocallback documentation
===============================

**aiocallback** is made for being simple yet effective. It is a backend library for 
**aioplugin** but has some lower level code to work with.


What makes aiocallback different from aiosignal?
------------------------------------------------
- **aiocallback** is more or less a toolbag containing useful objects. This can also be used 
   alongside aiosignal if needed.

-  **aiocallback** uses :py:class:`typing.ParamSpec` for it's typehints with the ``ParentSignal``
   which allows you to get more useful typehints. ``ParentSignal`` However is better for writing your own
   event wrappers and function properties.
 
-  **aiocallback** uses :py:class:`aiocallback.Hook` to customize opening and exiting from different 
   context managers.



Installation
------------

.. code-block:: bash

   $ pip install aiocallback

The library requires Python 3.10 or newer.

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

