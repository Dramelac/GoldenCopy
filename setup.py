from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='GoldenCopy',
    version='1.0',
    license='GNU',
    author="Dramelac",
    author_email='dramelac@pm.me',
    description='Copy the properties and groups of a user from neo4j (bloodhound) to create an identical golden ticket.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6, <4',
    url='https://github.com/Dramelac/GoldenCopy',
    keywords='pentest redteam goldenticket',
    install_requires=[
          'py2neo>=2021.2.3',
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