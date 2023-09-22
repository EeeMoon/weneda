from setuptools import setup, find_packages


VERSION = '0.0.1' 
DESCRIPTION = 'Module for editing and styling text.'
LONG_DESCRIPTION = 'Module for editing and styling text.'

setup(
    name="weneda", 
    version=VERSION,
    author="EeeMoon",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['fonttools'],
    keywords=['text', 'utils', 'misc', 'tools', 'style', 'color'],
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)