from setuptools import setup, find_packages
from pathlib import Path
import re

# Taught from my past work on aiothreading how to do this...

this_directory = Path(__file__).parent

__author__ = re.search(
    r'__author__\s*=\s*"(.*?)"',
    (this_directory / "aiocallback" / "__init__.py").read_text(),
)[1]

__version__ = re.search(
    r'__version__\s*=\s*"(.*?)"',
    (this_directory / "aiocallback" / "__version__.py").read_text(),
)[1]



def main():
    try:
        long_description = (
            (this_directory / "README.md").open("r").read()
        )
    except Exception:
        long_description = ""
 
    setup(
        name="aiocallback",
        author=__author__,
        version=__version__,
        packages=find_packages(),
        install_requires=["aiosignal", "typing_extensions"],
        include_package_data=True,
        description="A library for helping configure callbacks with asyncio and aiosignal",
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords=["event callbacks", "callbacks", "asyncio"],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Framework :: AsyncIO",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
        ],
    )


if __name__ == "__main__":
    main()
