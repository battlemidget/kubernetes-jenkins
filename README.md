# Charm Engineering - Kubernetes CI

This project contains the scripts used to build and test the CDK.

# Documentation

## Prereqs

Ability to create a virtualenv, install `virtualenvwrapper` from the archives.

Running the tests locally can be accomplished easily with tox. The tests expect
certain environment variables to be set. These can be found by looking at the
Jenkinsfile for each test. For example, the [jobs/validate/Jenkinsfile](
https://github.com/juju-solutions/kubernetes-jenkins/blob/master/jobs/validate/Jenkinsfile)
file has:

```
sh "CONTROLLER=${juju_controller} MODEL=${juju_model} CLOUD=${params.cloud} ${utils.pytest} \
    --junit-xml=validate.xml integration/test_cdk.py::test_validate"
```

This tells us what the commandline is to run this test and what parameters we
need to pass to it. These are passed to pytest running in tox. By default, the
working directory for tox is in /var/lib/jenkins, which probably doesn't exist
on development machines, so --workdir is used to specify a new directory to use.

```
CONTROLLER=aws-us-east-1 MODEL=cdk CLOUD=aws tox --workdir .tox -e py36 -- \
    pytest -v -s \
    --junit-xml=validate.xml \
    integration/test_cdk.py::test_validate 2>&1 | tee ~/log.txt
```

## Developing new tests

Jenkins Job Builder is used to generate jobs for Jenkins programmatically. No
jobs are created by hand in the Jenkins UI.

To add a new test into Jenkins, it is necessary to create a Jenkinsfile that is
a script to run for the job and then a yaml file to describe the job to Jenkins
Job Builder. Example job:

[validate Jenkinsfile](https://github.com/juju-solutions/kubernetes-jenkins/blob/master/jobs/validate/Jenkinsfile)

[validate yaml](https://github.com/juju-solutions/kubernetes-jenkins/blob/master/jobs/validate.yaml)


# Documentation

## Prereqs

Ability to create a virtualenv, install `virtualenvwrapper` from the archives.

## Build

To build the docs do the following:

```
> mkvirtualenv k8s
> pip install -rrequirements.txt
> pip install -rrequirements_doc.txt
> ogc --spec maintainer-spec.yml --debug execute -t build-docs
```

To deploy documentation (requires AWS credentials):

```
> ogc --spec maintainer-spec.yml execute -t deploy-docs
```
