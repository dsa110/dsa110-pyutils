# dsa110-pyutils

Common functions and classes to use throughout the DSA110 project.
Check the docs before spinning your own code.

```
Point browser to: file:///<path to repo>/Doc/build/html/index.html
```

All functions and classes should have a test function in the test
directory.

WORKFLOW
The development branch will contain release candidate versions of the
form vM.m.b-rc#. New features and bug fixes branch off the appropriate
version. When new features are ready, the version will be updated and
other devs will need to pull in those changes before their work is accepted
back on the development branch. master will container stable releases and
will be what the running system uses. master will always be a fast-forward
on development and development will try to be a fast-forward on user dev
branches.

If this doesn't run in your enviroment, check the pip_packages file
as it contains what is needed.

Running tests:

```
cd <TOT of repo>
pip install .
cd test
coverage run -m pytest
coverage html
```

```
Point browser to: file:///<path to repo>/test/htmlcov/index.html
```

commit htmlcov directory.
