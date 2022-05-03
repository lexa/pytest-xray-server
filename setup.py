from setuptools import setup, find_packages
import os

XRAY_SETUP_DIR = os.path.abspath(os.path.dirname(__file__))


def long_description():
    filepath = os.path.join(XRAY_SETUP_DIR, "README.md")
    with open(filepath) as f:
        return f.read()


PKG_INSTALL_REQS = ["pytest >= 5.3.1", "requests >= 2.21.4"]


setup(
    name="pytest_xray_server",
    author="Neville Tummon",
    author_email="nt.devs@gmail.com",
    maintainer='Yuliya Sharkadiy',
    maintainer_email='yuliya@sharky.email',
    version="1.6",
    python_requires=">=3.6.6",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests",)),
    download_url="https://github.com/lexa/pytest-xray-server/archive/v1.4.tar.gz",
    install_requires=PKG_INSTALL_REQS,
    summary="py.test Xray integration plugin, using markers",
    entry_points={"pytest11": ["pytest_xray_server = pytest_xray_server.plugin"]},
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)

