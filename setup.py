import os
from distutils.core import setup

version_txt = os.path.join(os.path.dirname(__file__), 'lc4', 'version.txt')
with open(version_txt, 'r') as f:
    version = f.read().strip()

setup(
    name='lc4',
    packages=['lc4'],
    package_data={'lc4': ['version.txt']},
    scripts=['bin/lc4'],
    license='MIT',
    version=version,
    description='A Python implementation of ElsieFour (LC4)',
    long_description=open('README.rst').read(),
    author='Daniel Steinberg',
    author_email='ds@dannyadam.com',
    url='https://github.com/dstein64/lc4',
    keywords=['cryptography', 'lc4', 'elsie-four'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    requires=['numpy']
)
