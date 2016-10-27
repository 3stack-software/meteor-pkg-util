from setuptools import setup

setup(
    name='meteor_pkg_util',
    version='0.1',
    packages=['meteor_pkg_util'],
    install_requires=[
        'Click',
        'PyYAML'
    ],
    package_data={
        'meteor_pkg_util': ['default.yaml']
    },
    entry_points='''
        [console_scripts]
        mpkgutil=meteor_pkg_util:cli
    ''',
)
