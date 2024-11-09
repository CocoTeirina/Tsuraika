from setuptools import setup, find_packages

setup(
    name="tsuraika",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
    ],
    entry_points={
        'console_scripts': [
            'tsuraika=tsuraika.cli:app',
        ],
    },
    python_requires=">=3.7",
    author="CocoTeirina",
    author_email="cocoteirina@proton.me",
    description="A simple FRP (Fast Reverse Proxy) implementation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CocoTeirina/Tsuraika",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3 License",
        "Operating System :: OS Independent",
    ],
)