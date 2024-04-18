import setuptools


with open("README.md", "rb") as fh:
    long_description = fh.read().decode()
with open("imgsvc/version.py", "r") as fh:
    exec(fh.read())
    __version__: str


def packages():
    return setuptools.find_packages(include=['imgsv*'])


setuptools.setup(
    name="imgsvc",
    version=__version__,
    author="flandre.info",
    author_email="flandre@scarletx.cn",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eliphatfs/imgsvc",
    packages=packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='~=3.7',
    entry_points=dict(
        console_scripts=[
            "imgsvc-server=imgsvc.server:main"
        ]
    )
)
