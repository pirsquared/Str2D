"""setup.py.

This setup.py file is included to support editable installations using pip's `-e`
option. The primary project configuration is specified in the pyproject.toml file. This
setup.py is only used for development installations and ensures compatibility with tools
and workflows that rely on setup.py.
"""

from setuptools import setup, find_packages

setup(
    name="Str2D",
    version="0.1.1",  # Update this version number before releasing a new version
    description="Manipulate 2D strings in Python.",
    author="Sean Smith",
    author_email="pirsquared.pirr@gmail.com",
    url="https://github.com/pirsquared/Str2D",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "build",
            "twine",
            "black",
            "pre-commit",
            "pylint",
            "sphinx",
            "ipython",
        ],
    },
)
