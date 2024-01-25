from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in hyde_app/__init__.py
from hyde_app import __version__ as version

setup(
	name="hyde_app",
	version=version,
	description="abc",
	author="hyde",
	author_email="hyde.k@korecent.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
