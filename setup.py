from setuptools import setup, find_packages

PROJECT_URL = 'https://github.com/melexis/warnings-plugin'
VERSION = '0.0.1'

setup(
    name='warnings-plugin',
    version=VERSION,
    url=PROJECT_URL,
    download_url=PROJECT_URL + '/tarball/' + VERSION,
    license='MIT license',
    author='Bavo Van Achte',
    author_email='bavo.van.achte@gmail.com',
    description='Command-line alternative for https://github.com/jenkinsci/warnings-plugin. Useable with plugin-less CI systems.',
    long_description=open("README.md").read(),
    zip_safe=False,
    classifiers=[],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=None,
    namespace_packages=['ci'],
    keywords = ['Gitlab CI', 'warnings','CI'],
)
