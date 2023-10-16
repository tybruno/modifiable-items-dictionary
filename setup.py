"""Setup.py"""
import setuptools

__version__ = "v2.0.2"
__author__ = "Tyler Bruno"
_description = ("Typed and Tested Modifiable Items Dict which allows keys and "
                "values to be modified at run time.")

with open("README.md", "r", encoding="utf-8") as file:
    README = file.read()

setuptools.setup(
    name="modifiable-items-dictionary",
    version=__version__,
    author=__author__,
    description=_description,
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="python dict dictionary mapping key-mangling",
    url="https://github.com/tybruno/modifiable-items-dictionary",
    license="MIT",
    package_data={"modifiable-items-dictionary": ["py.typed"]},
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: " "Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)
