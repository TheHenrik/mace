from setuptools import setup
import os


def fast_scandir(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


def get_subdir(dirname):
    subdir = fast_scandir(dirname)
    blacklist = ['__pycache__']
    subfolders = ['mace']
    for subfolder in subdir:
        check = True
        for test in blacklist:
            if test in subfolder:
                check = False
        if check:
            subfolders.append(subfolder.replace('\\','.'))
    return subfolders


setup(name='mace',
        version='0.1.0',
        author='Tjalf Stadel',
        packages=get_subdir('mace'),
        scripts=['bin/test.py'],
        description='A package for analysing modell airplanes',
        long_description=open('README.md').read(),
        package_data={'MACE': ['data/mace_data.txt']},
        install_requires= [
            'numpy',
            'dataclasses>=0.6',
            ]
      )
