import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='parallelprocs',
    version='0.1.4',
    author='Ken Youens-Clark',
    author_email='kyclark@gmail.com',
    description='Run command lines via (GNU) parallel',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kyclark/parallelprocs',
    #packages=setuptools.find_packages(),
    packages='.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
