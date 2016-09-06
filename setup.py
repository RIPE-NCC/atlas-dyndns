import os
from os.path import abspath, dirname, join
from setuptools import setup

__version__ = None
exec(open("ripe/atlas/dyndns/version.py").read())

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Get proper long description for package
current_dir = dirname(abspath(__file__))
description = open(join(current_dir, "README.rst")).read()
changes = open(join(current_dir, "CHANGES.rst")).read()
long_description = '\n\n'.join([description, changes])

# Get the long description from README.md
setup(
    name="ripe.atlas.dyndns",
    version=__version__,
    packages=["ripe", "ripe.atlas", "ripe.atlas.dyndns"],
    namespace_packages=["ripe", "ripe.atlas"],
    include_package_data=True,
    license="GPLv3",
    description="RIPE Atlas dyndns server",
    long_description=long_description,
    url="https://github.com/RIPE-NCC/atlas-dyndns",
    download_url="https://github.com/RIPE-NCC/atlas-dyndns",
    author="The RIPE Atlas team",
    author_email="atlas@ripe.net",
    maintainer="The RIPE Atlas team",
    maintainer_email="atlas@ripe.net",
    install_requires=[
        "requests>=2.7.0",
        "IPy>=0.8"
    ],
    tests_require=[
        "nose",
        "coverage",
        "setuptools"
    ],
    test_suite="nose.collector",
    entry_points={
        "console_scripts": [
            "atlas-pdns-pipe=ripe.atlas.dyndns.scripts:atlas_pdns_pipe_main",
            "create-routed-list=ripe.atlas.dyndns.scripts:create_routed_list_main"
        ]
    },
    keywords=['RIPE', 'RIPE NCC', 'RIPE Atlas', 'PowerDNS', 'dyndns'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: DNS",
    ],
)
