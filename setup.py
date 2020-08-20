from setuptools import setup
from version import get_git_version

try:
    version = get_git_version()
    assert version is not None
except (AttributeError, AssertionError):
    version = '2.1.1'

setup(name='dsa110-pyutils',
      version=version,
      url='http://github.com/dsa110/dsa110-pyutils',
      packages=['dsautils'],
      package_data = {
          'dsautils': ['conf/*', 'test/etcdConfig.yml'],
          },
      tests_require=[
          'coverage'
          ],
      entry_points='''
          [console_scripts]
          dsamon=dsautils.cli:mon
          dsacon=dsautils.cli:con
      ''',      
      zip_safe=False)
