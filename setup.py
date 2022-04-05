from setuptools import setup
from dsautils.version import get_git_version

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
          'dsautils': ['conf/*', 'test/etcdConfig.yml', 'data/faraday2020v2.hdf5'],
          },
      install_requires = [
          'pyyaml',
          'structlog>=21.1.0',
          'numpy',
          'influxdb'
      ],
      tests_require=[
          'coverage'
          ],
      entry_points='''
          [console_scripts]
          dsamon=dsautils.cli:mon
          dsacon=dsautils.cli:con
          dsatm=dsautils.cli:tm
          dsacand=dsautils.cli:cand
      ''',      
      zip_safe=False)
