# dsa110-pyutils

Common functions and classes to use throughout the DSA110 project.
Check the docs before spinning your own code.

Point browser to: file:///<path to repo>/Doc/build/html/index.html

All functions and classes should have a test function in the test
directory. Merge to master when tests pass and coverage is acceptable.

If this doesn't run in your enviroment, check the pip_packages file
as it contains what is needed.

Running tests:

cd test
coverage run -m pytest
coverage html

Point browser to: file:///<path to repo>/test/htmlcov/index.html

commit htmlcov directory.
