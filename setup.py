import setuptools


setuptools.setup(
    name="utpy", 
    version="0.0.1",
    author="Taregh Naderi",
    install_requires=['docutils>=0.3'],
    author_email="taregh.n@gmail.com",
    description="A small example package",
    long_description="long description goes here",
    long_description_content_type="text/markdown",
    url="https://github.com/iamvee/test",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
