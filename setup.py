from setuptools import find_namespace_packages, setup

PROJECT_URL = 'https://github.com/melexis/warnings-plugin'

requires = [
    'junitparser>=1.0.0,<2.0',
    'ruamel.yaml>=0.17.21',
]

setup(
    name='mlx.warnings',
    url=PROJECT_URL,
    use_scm_version={
        'write_to': 'src/mlx/warnings/__version__.py'
    },
    author='Bavo Van Achte',
    author_email='bavo.van.achte@gmail.com',
    description='Command-line alternative for https://github.com/jenkinsci/warnings-plugin. '
                'Useable with plugin-less CI systems.',
    long_description=open("README.rst", encoding="utf-8").read(),
    long_description_content_type='text/x-rst',
    project_urls={
        'Documentation': 'https://melexis.github.io/warnings-plugin',
        'Source': 'https://github.com/melexis/warnings-plugin',
        'Tracker': 'https://github.com/melexis/warnings-plugin/issues',
    },
    zip_safe=False,
    license='Apache License, Version 2.0',
    platforms='any',
    packages=find_namespace_packages(where='src', include=['mlx.warnings']),
    package_dir={'': 'src'},
    entry_points={'console_scripts': ['mlx-warnings = mlx.warnings.warnings:main']},
    install_requires=requires,
    python_requires='>=3.8',
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        # 'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: PyPy',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],
    keywords=['Gitlab CI', 'warnings', 'CI'],
)
