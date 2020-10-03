# -*- coding: utf-8 -*-
import setuptools
import uniswap

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uniswap-v2-asynctomatic",  # TODO remove username suffix before PyPI distribution
    version=uniswap.__version__,
    author="Asynctomatic",
    author_email="asynctomatic@gmail.com",
    description="A unofficial wrapper for Uniswap V2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asynctomatic/uniswap-v2-py",
    packages=setuptools.find_packages(),
    package_data={"uniswap": ["assets/*"]},
    install_requires=["web3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    test_suit="tests"
)
