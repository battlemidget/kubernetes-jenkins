#!/usr/bin/env bash
# Deploy the local charms (built in a prevous step) and since they are local
# charms we do have to attach local resources (also built in previous step).

set -o errexit  # Exit when an individual command fails.
set -o pipefail  # The exit status of the last command is returned.
set -o xtrace  # Print the commands that are executed.

# The cloud is an option for this script, default to gce.
CLOUD=${CLOUD:-"gce"}

# The path to the archive of the JUJU_DATA directory for the specific cloud.
JUJU_DATA_TAR="/var/lib/jenkins/juju/juju_${CLOUD}.tar.gz"
# Uncompress the file that contains the Juju data to the workspace directory.
tar -xvzf ${JUJU_DATA_TAR} -C ${WORKSPACE}

CHARMS_BUILDS=${WORKSPACE}/charms/builds
# Expand all the charm archives to the charms/builds directory.
tar -xzf ${CHARMS_BUILDS}/easyrsa.tar.gz -C ${CHARMS_BUILDS}
tar -xzf ${CHARMS_BUILDS}/etcd.tar.gz -C ${CHARMS_BUILDS}
tar -xzf ${CHARMS_BUILDS}/flannel.tar.gz -C ${CHARMS_BUILDS}
tar -xzf ${CHARMS_BUILDS}/kubeapi-load-balancer.tar.gz -C ${CHARMS_BUILDS}
tar -xzf ${CHARMS_BUILDS}/kubernetes-e2e.tar.gz -C ${CHARMS_BUILDS}
tar -xzf ${CHARMS_BUILDS}/kubernetes-master.tar.gz -C ${CHARMS_BUILDS}
tar -xzf ${CHARMS_BUILDS}/kubernetes-worker.tar.gz -C ${CHARMS_BUILDS}

# Set the JUJU_DATA directory for this jenkins workspace.
export JUJU_DATA=${WORKSPACE}/juju
export JUJU_REPOSITORY=${WORKSPACE}/charms
# Define a unique model name for this run.
export MODEL=${MODEL:-${BUILD_TAG}}

# Create a model, deploy, expose, relate all the Kubernetes charms.
./juju-deploy-local-charms.sh ${MODEL}

# Attach the resources built from a previous step.
./juju-attach-resources.sh resources

echo "Charms deployed and resources attached to ${MODEL} at `date`."

source ./define-juju.sh
juju status