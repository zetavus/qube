from setuptools import setup, find_packages
import os

# Read README
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qube",
    version="0.1.0",
    author="QyTum Developer",
    author_email="developer@qube.org",
    description="A comprehensive quantum programming language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qube-lang/qube",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qube=qube.cli:main",
        ],
    },
    package_data={
        "qube": ["examples/*.qyt"],
    },
    include_package_data=True,
    keywords="quantum computing programming language compiler interpreter",
    project_urls={
        "Bug Reports": "https://github.com/zetavus/qube/issues",
        "Source": "https://github.com/zetavus/qube",
        "Documentation": "https://qube.readthedocs.io/",
    },
)