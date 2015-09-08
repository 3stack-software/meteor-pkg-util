from setuptools import setup

setup(
    name='meteor_pkg_util',
    version='0.1',
    py_modules=['meteor_pkg_util'],
    install_requires=[
        'Click',
        'PyYAML'
    ],
    package_data={
        '': ['default.yaml']
    },
    entry_points='''
        [console_scripts]
        mpkgutil=meteor_pkg_util:cli
    ''',
)
