import os
from setuptools import setup

version_txt = os.path.join(os.path.dirname(__file__), 'lc4', 'version.txt')
with open(version_txt, 'r') as f:
    version = f.read().strip()

setup(
    author='Daniel Steinberg',
    author_email='ds@dannyadam.com',
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
        'Programming Language :: Python :: 3',
    ],
    description='A Python implementation of ElsieFour (LC4)',
    entry_points={
        'console_scripts': ['lc4=lc4.lc4:main'],
    },
    keywords=['cryptography', 'lc4', 'elsie-four'],
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    name='lc4',
    package_data={'lc4': ['version.txt']},
    packages=['lc4'],
    python_requires='>=3.5',
    install_requires=['numpy'],
    url='https://github.com/dstein64/lc4',
    version=version,
)
