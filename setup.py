import sys
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


version = sys.version_info[:2]
if version < (3, 10):
    print(
        "resources requires Python version 3.10 or later"
        + f" (you are using Python {version[0]}.{version[1]})."
    )
    sys.exit(-1)


VERSION = "0.1.0"

install_requires = ["requests", "pandas", "BeautifulSoup4"]

setup(
    name="Crow Scraper",
    version=VERSION,
    description="A Simple Scraper to collect prices on Computer Hardware.",
    long_description=long_description,
    author="Caleb Farrell",
    author_email="caleb.farrell@valhallahosting.com",
    url="https://github.com/cfarrell987/crowScrape",
    license="GPLv3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
)