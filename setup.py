from setuptools import setup
from dsautils.version import get_git_version

setup(name='dsa110-pyutils',
      version=get_git_version(),
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
