from setuptools import setup
setup(
    name='gnatr',
    packages=['src'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    tests_require=[
        'pytest',
    ],
)