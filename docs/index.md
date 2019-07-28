# CI Documentation

Documentation covering all test jobs and what they are and do

## Building the documentation

### Prereqs

Ability to create a virtualenv, install `virtualenvwrapper` from the archives.

### Build

```
> mkvirtualenv k8s
> pip install -rrequirements.txt
> pip install -rrequirements_doc.txt
> ogc --spec maintainer-spec.toml --debug execute -t docs && mkdocs serve
```


