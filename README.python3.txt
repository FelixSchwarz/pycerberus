I'm not using Python 3 for any project in production right now. However I'd like to support the Python 3 transition. Therefore I ensure that all tests also pass on Python 3 and I believe you can use pycerberus on Python 3 just fine. I'm testing Python 3 using the latest version of Fedora. As the Python 3 userbase is so small currently, I won't make any effort to maintain compatibility for older versions of Python 3 (e.g. Python 3.0).

Python 3 support for pycerberus is done by the help of the wonderful '2to3' tool which can do all required syntax changes for Python 3. By doing that,  I can maintain a single source tree and all fixes for Python 2 are automatically in the Python 3 version.

However there are some shortcomings that you should be aware of::

1. Full i18n support requires Babel and there is no version of Babel with Python 3 support yet. Therefore I don't use Babel on Python 3. However you can get localized error messages if you use Babel with Python 2 to compile the catalog files. After the initial generation of the mo files (done at install time), Babel is not required anymore. For the most recent status of Babel with Python 3, please read http://babel.edgewall.org/ticket/209

2. nosetests also does not have a stable version with Python 3 support. There is a unofficial fork of nose which supports at least basic functionality on Python 3: https://bitbucket.org/foogod/python-nose3 . Support for Python 3 in nose is done by using 2to3 so the library needs to be installed somewhere (just 'setup.py develop' won't do the trick). You only need nosetests to run the unit tests, so most people can ignore this limitation.

3. The 2to3 support in distutils causes some issues which I'll fix eventually:
    - Only installed files will be converted. Therefore you neither can run the tests nor build the docs without using 2to3 explicitely.


IMPORTANT:
If you're using pycerberus on Python 3, please tell me how it works for you! :-)

