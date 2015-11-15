from setuptools import find_packages, setup
# import versioneer


def read_md(filename):
    try:
        from pypandoc import convert
        return convert(filename, 'rst')
    except ImportError:
        print("warning: pypandoc module not found, could not convert Markdown to RST")
        return open(filename, 'r').read()


setup(
    name='pytest-check_mk',
    version=0.1,  # versioneer.get_version(),
    url='https://github.com/tom-mi/python-pytest-check_mk/',
    license='GPLv2',
    author='Thomas Reifenberger',
    install_requires=['pytest'],
    author_email='tom-mi at rfnbrgr.de',
    description='pytest plugin to test check_mk checks',
    long_description=read_md('README.md'),
    packages=find_packages(),
    platforms='any',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: System :: Monitoring',
        ],
    # cmdclass=versioneer.get_cmdclass(),
    entry_points={
        'pytest11': [
            'pytest_check_mk = pytest_check_mk.plugin',
        ],
    },
)
