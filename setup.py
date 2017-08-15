import io
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup

PROJECT_URL = 'https://github.com/melexis/warnings-plugin'


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


requires = ['junitparser>=1.0.0', 'setuptools-scm']

setup(
    name='mlx.warnings',
    url=PROJECT_URL,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author='Bavo Van Achte',
    author_email='bavo.van.achte@gmail.com',
    description='Command-line alternative for https://github.com/jenkinsci/warnings-plugin. Useable with plugin-less CI systems.',
    long_description=open("README.rst").read(),
    zip_safe=False,
    license='Apache License, Version 2.0',
    platforms='any',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points = {'console_scripts': ['mlx-warnings = mlx.warnings:main']},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['mlx'],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: PyPy',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],
    keywords = ['Gitlab CI', 'warnings', 'CI'],
)
