# Getting Started
Documentation covering all test jobs and what they are and do

## Building the documentation

### Prereqs

Ability to create a virtualenv, install `virtualenvwrapper` from the archives.

### Build

```console
> mkvirtualenv k8s
> pip install -rrequirements_doc.txt
> ogc --spec maintainer-spec.yml --debug execute -t build-docs && mkdocs serve
```

### Deploying

> Note: The necessary _aws_ credentials are required to upload the website to the S3 bucket.

```console
> aws s3 sync site/ s3://jenkaas/docs
```

