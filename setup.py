from setuptools import setup, find_packages
from aiocallback import __version__, __author__
import pathlib


def main():
    try:
        long_description = (
            (pathlib.Path("aiocallback").parent / "readme.md").open("r").read()
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
