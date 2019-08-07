# Charm Engineering - Kubernetes CI

This project contains the scripts used to build and test the CDK.

# Documentation

## Prereqs

Ability to create a virtualenv, install `virtualenvwrapper` from the archives.

## Build

To build the docs do the following:

```
> mkvirtualenv k8s
> pip install -rrequirements.txt
> pip install -rrequirements_doc.txt
> ogc --spec maintainer-spec.yml --debug execute --phase plan
```

To deploy documentation (requires AWS credentials):

```
> ogc --spec maintainer-spec.yml execute --phase publish
```
