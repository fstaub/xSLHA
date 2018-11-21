import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xSLHA",
    version="0.0.1",
    author="Florian Staub",
    author_email="florian.staub@gmail.com",
    description="A python package to read (big/many) SLHA files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fstaub/xSLHA",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2,3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux, MacOS",
    ],
)
