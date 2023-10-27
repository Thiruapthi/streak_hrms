from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in streak_hrms/__init__.py
from streak_hrms import __version__ as version

setup(
	name="streak_hrms",
	version=version,
	description="Customizing The HR Modules",
	author="Suneet Sharma",
	author_email="suneet@korecent.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
