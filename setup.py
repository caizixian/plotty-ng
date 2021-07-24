from setuptools import setup, find_packages
from codecs import open
from os import path

NAME = 'plotty'
REQUIRED = ["jupyterlab", "matplotlib", "pandas", "seaborn", "ipywidgets"]

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

about = {}
with open(path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)

setup(
    name="plotty-ng",
    version=about["__VERSION__"],
    description='Plotty: Next Generation',
    long_description=long_description,
    url='https://github.com/caizixian/plotty-ng',
    author='Zixian Cai',
    author_email='u5937495@anu.edu.au',
    license='Apache',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System :: Benchmark',
        'Programming Language :: Python :: 3',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=REQUIRED,
    extras_require={},
)
