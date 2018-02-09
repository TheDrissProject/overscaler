#!/bin/bash -eu
usage="Usage: init.sh (create|delete|reset)"

# FUNCTIONS
create() {
    echo "Creating statefulsets with files..."
     kubectl apply -f ubuntu-test/

}

delete () {
    echo "Deleting statefulsets with files..."
     kubectl delete -f ubuntu-test/
}


# SCRIPT
if [ $# -lt 1 ]; then
    echo $usage
    exit 1
fi

if [ $1 == "create" ]; then
    create
    exit 0
fi

if [ $1 == "delete" ]; then
    delete
    exit 0
fi

if [ $1 == "reset" ]; then
    delete
    create
    exit 0
fi
