from setuptools import setup
from goldencopy import __version__
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='GoldenCopy',
    version=__version__,
    license='GNU',
    author="Dramelac",
    author_email='dramelac@pm.me',
    description='Copy the properties and groups of a user or computer from neo4j (bloodhound) to create an identical golden ticket.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6, <4',
    url='https://github.com/Dramelac/GoldenCopy',
    keywords='pentest redteam goldenticket goldencopy',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'py2neo>=2021.2.3'
      ],
    py_modules=["goldencopy"],
    entry_points={
    'console_scripts': [
        'goldencopy=goldencopy:main',
    ],
},

    project_urls={
        'Bug Reports': 'https://github.com/Dramelac/GoldenCopy/issues',
        'Source': 'https://github.com/Dramelac/GoldenCopy',
    },

)