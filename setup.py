import setuptools



long_description = open('README.md').read()

setuptools.setup(
    name="utpy", 
    version="0.7.0",
    author="Taregh Naderi",
    install_requires=[],
    author_email="taregh.n@gmail.com",
    description="youtube downloader python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tare9n/utpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
