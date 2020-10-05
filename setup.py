import os
import re
import setuptools

ROOT = os.path.dirname(__file__)
REQUIREMENTS = os.path.join(ROOT, "requirements.in")
README = os.path.join(ROOT, "README.md")
INIT = os.path.join(ROOT, "securicad", "vanguard", "__init__.py")

STRING_RE = r"\s*=\s*['\"]([^'\"]+)['\"]"
AUTHOR_RE = re.compile(fr"__author__{STRING_RE}")
VERSION_RE = re.compile(fr"__version__{STRING_RE}")


def get_author():
    with open(INIT, encoding="utf-8") as f:
        init = f.read()
        return AUTHOR_RE.search(init).group(1)


def get_version():
    with open(INIT, encoding="utf-8") as f:
        init = f.read()
        return VERSION_RE.search(init).group(1)


def get_requirements():
    requirements = []
    with open(REQUIREMENTS, encoding="utf-8") as f:
        for requirement in f:
            requirements.append(requirement.strip())
    return requirements


def get_readme():
    with open(README, encoding="utf-8") as f:
        return f.read()


setuptools.setup(
    name="securicad-vanguard",
    version=get_version(),
    description="A Python SDK for foreseeti's securiCAD Vanguard",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/foreseeti/securicad-vanguard-sdk",
    author=get_author(),
    license="The Apache Software License, Version 2.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Security",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="securicad vanguard threat modeling",
    packages=["securicad.vanguard"],
    install_requires=get_requirements(),
    python_requires=">=3.6",
)
