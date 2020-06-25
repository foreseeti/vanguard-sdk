# Release securiCAD Vanguard SDK

This file describes how to make a release build of
securicad-vanguard-sdk and how to publish it to pip.

#### Make sure that the repo is clean
```
git status --ignored
```
#### Update the version number in `securicad/vanguard/__init__.py`
#### Generate a new `requirements.txt`
```
./generate_requirements.sh
```
#### Test that everything works with the new `requirements.txt`
#### Commit `__init__.py` and `requirements.txt` with the message `Release version X.Y.Z`
```
git add securicad/vanguard/__init__.py requirements.txt
git commit -m "Release version X.Y.Z"
```
#### Tag the commit with the tag `release/X.Y.Z`
```
git tag "release/X.Y.Z"
```
#### Push the release commit and tag to github
```
git push origin master
git push origin release/X.Y.Z
```
#### Create and activate release venv
```
python3 -m venv release-venv
. release-venv/bin/activate
pip install --upgrade pip
pip install wheel twine
```
#### Build distribution files
##### Build a source distribution
```
python setup.py sdist
```
##### Build a wheel distribution
```
python setup.py bdist_wheel
```
#### Create `~/.pypirc` with the following content
```
[distutils]
index-servers =
  pypi
  testpypi

[pypi]
username = __token__
password = pypi-****

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-****
```
#### Publish to testpypi
```
twine upload --repository testpypi dist/*
```
#### Publish to pypi
```
twine upload dist/*
```
