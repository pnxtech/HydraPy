import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

with open("./hydrapy/VERSION") as f:
    version = f.read()

setuptools.setup(
    name="hydra-py",
    version=version,
    description="Hydra for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnxtech/HydraPy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=install_requires
)
