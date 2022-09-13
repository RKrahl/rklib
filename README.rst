A collection of Python library modules
======================================

This package provides a collection of small helper functions and
classes.


System requirements
-------------------

Python:

+ Python 3.4 or newer.

Required library packages:

+ `setuptools`_

Optional library packages:

+ `setuptools_scm`_

  The version number is managed using this package.  All source
  distributions add a static text file with the version number and
  fall back using that if `setuptools_scm` is not available.  So this
  package is only needed to build out of the plain development source
  tree as cloned from GitHub.

+ `pytest`_ >= 3.0

  Only needed to run the test suite.

+ `distutils-pytest`_

  Only needed to run the test suite.


Copyright and License
---------------------

- Copyright 2017–2019
  Helmholtz-Zentrum Berlin für Materialien und Energie GmbH
- Copyright 2019–2022 Rolf Krahl

Licensed under the `Apache License`_, Version 2.0 (the "License"); you
may not use this package except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.


.. _setuptools: https://github.com/pypa/setuptools/
.. _setuptools_scm: https://github.com/pypa/setuptools_scm/
.. _pytest: https://pytest.org/
.. _distutils-pytest: https://github.com/RKrahl/distutils-pytest
.. _Apache License: https://www.apache.org/licenses/LICENSE-2.0
