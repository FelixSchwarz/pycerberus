# -*- coding: UTF-8 -*-
"Release information about pycerberus."

name = 'pycerberus'
version = '0.3'
description = 'Highly flexible, no magic input validation library'
long_description = '''
pycerberus is a framework to check user data thoroughly so that you can protect
your application from malicious (or just garbled) input data.

* Remove stupid code which converts input values: After values are validated, you 
  can work with real Python types instead of strings - e.g. 42 instead of '42', 
  convert database IDs to model objects transparently.
* Implement custom validation rules: Writing custom validators is 
  straightforward, everything is well documented and pycerberus only uses very 
  little Python magic.
* Focus on your value-adding application code: Save time by implementing every 
  input validation rule only once, but 100% right instead of implementing a 
  dozen different half-baked solutions.
* Ready for global business: i18n support (based on GNU gettext) is built in, 
  adding custom translations is easy.
* Tune it for your needs: You can implement custom behavior in your validators,
  e.g. fetch translations from a database instead of using gettext or define
  custom translations for built-in validators.
* Use it wherever you like: pycerberus does not depend on specific contexts
  (e.g. web development) so you can also use it in every Python application. 


Changelog
******************************

0.3 (27.03.2010)
==================
- Python 2.3 compatibility
- Schema can raise error if unknown items are processed
- Basic domain name validator
- Basic email address validator

0.2 (16.03.2010)
==================
- You now can declare custom messages as a class-level dict
- Added interface to retrieve error details from InvalidDataErrors
- Added validation schemas to validate a set of values (typically a web form).
  Schemas can also inherit from other schemas to avoid code duplication.
- Validators try to make thread-safety violations obvious
- Nicer API to retrieve error details from an InvalidDataError

0.1 (30.01.2010)
==================
 - initial release
'''
author = 'Felix Schwarz'
email = 'felix.schwarz@oss.schwarz.eu'
url = 'http://www.schwarz.eu/opensource/projects/pycerberus'
download_url = 'http://www.schwarz.eu/opensource/projects/%(name)s/download/%(version)s/%(name)s-%(version)s.tar.gz' % dict(name=name, version=version)
copyright = u'2009-2010 Felix Schwarz'
license='MIT'

