import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xslha",
    version="1.0.0",
    author="Florian Staub",
    author_email="florian.staub@gmail.com",
    description="A python package to read (big/many) SLHA files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fstaub/xSLHA",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS"
    ],
)
