# Release securiCAD Vanguard SDK

This file describes how to make release builds of `securicad-vanguard-sdk` and how to publish them to [PyPI](https://pypi.org).

To make a release, perform the following steps:

1. Make a release commit and push it to a new branch
2. Make a pull request to `master` and get it approved and merged
3. Make a release tag for the merged pull request
4. Build distribution files
5. Publish distribution files

### 1. Make a release commit and push it to a new branch

The release commit shall contain the following changes:

- Updated version number in `securicad/vanguard/__init__.py`
- Updated dependencies in `requirements.txt` and `dev-requirements.txt`

Test that everything still works with the new dependencies.

The name of the new branch doesn't matter, since it will be deleted after the release commit has been merged to `master`, but the convention for branch names is `<user-name>/<branch-name>`, e.g. `max/release`.

The commit message shall be `Release <version>`, e.g. `Release 0.0.2`.

```
$ git checkout -b max/release
$ sed -i 's/^__version__ = "[^"]*"$/__version__ = "0.0.2"/' securicad/vanguard/__init__.py
$ ./tools/scripts/create_requirements.sh
$ git add securicad/vanguard/__init__.py requirements.txt dev-requirements.txt
$ git commit -m "Release 0.0.2"
$ git push origin max/release
```

### 2. Make a pull request to `master` and get it approved and merged

Go to the repository on GitHub, click `Pull requests`, and then `New pull request`. Make sure that `base` is set to `master`, and set `compare` to your branch. Click `Create pull request`, add appropriate `Reviewers`, and add yourself as `Assignees`.

### 3. Make a release tag for the merged pull request

Once your pull request has been merged, you need to fetch the new merged commit in `master` to create the release tag:

```
$ git checkout master
$ git fetch
$ git merge --ff-only
$ git tag release/0.0.2
$ git push origin release/0.0.2
```

### 4. Build distribution files

Make sure that the repo is clean:

```
git status --ignored
```

Create and activate a virtual Python environment:

```
./tools/scripts/create_venv.sh
. venv/bin/activate
```

Build source distribution:

```
python setup.py sdist
```

Build wheel distribution:

```
python setup.py bdist_wheel
```

There should now be two files under the directory `dist/`: `securicad-vanguard-0.0.2.tar.gz` and `securicad_vanguard-0.0.2-py3-none-any.whl`.

### 5. Publish distribution files

Create `~/.pypirc` with the following content:

```
[distutils]
index-servers =
  securicad-vanguard
  securicad-vanguard-test

[securicad-vanguard]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-****

[securicad-vanguard-test]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-****
```

Publish distribution files to testpypi:

```
twine upload --repository securicad-vanguard-test dist/*
```

Publish distribution files to pypi:

```
twine upload --repository securicad-vanguard dist/*
```
