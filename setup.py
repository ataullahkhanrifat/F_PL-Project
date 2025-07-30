#!/usr/bin/env python3
"""
Setup script for FPL Squad Optimizer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fpl-squad-optimizer",
    version="2.0.0",
    author="Md Ataullah Khan Rifat",
    author_email="your.email@example.com",
    description="A comprehensive Fantasy Premier League assistant using machine learning and mathematical optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fpl-squad-optimizer",
    packages=[],
    py_modules=["src.fetch_fpl_data", "src.optimizer"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "jupyter>=1.0.0",
            "pytest>=7.4.4",
            "black>=23.12.1",
            "flake8>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fpl-fetch-data=src.fetch_fpl_data:main",
            "fpl-optimize=src.optimizer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.csv"],
    },
)
