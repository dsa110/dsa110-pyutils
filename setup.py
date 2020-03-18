from setuptools import setup

setup(name='dsa110-pyutils',
      version='1.0.3',
      url='http://github.com/dsa110/dsa110-pyutils',
      packages=['dsautils'],
      package_data = {
          'dsautils': ['conf/*', 'test/etcdConfig.yml'],
          },
      entry_points='''
          [console_scripts]
          dsamon=dsautils.cli:mon
          dsacon=dsautils.cli:con
      ''',      
      zip_safe=False)
