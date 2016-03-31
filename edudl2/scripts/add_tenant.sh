#!/bin/bash
# (c) 2014 Amplify Education, Inc. All rights reserved, subject to the license
# below.
#
# Education agencies that are members of the Smarter Balanced Assessment
# Consortium as of August 1, 2014 are granted a worldwide, non-exclusive, fully
# paid-up, royalty-free, perpetual license, to access, use, execute, reproduce,
# display, distribute, perform and create derivative works of the software
# included in the Reporting Platform, including the source code to such software.
# This license includes the right to grant sublicenses by such consortium members
# to third party vendors solely for the purpose of performing services on behalf
# of such consortium member educational agencies.


set -e # Exit on errors

function create_tenant_schema {
    # initialize edware star schema for the tenant
    python -m edschema.metadata_generator --metadata edware -s edware_$1 -d edware --host=localhost:5432 -u edware -p edware2013
}

function drop_tenant_schema {
    # drop edware star schema for the tenant
    python -m edschema.metadata_generator --metadata edware -a teardown -s edware_$1 -d edware --host=localhost:5432 -u edware -p edware2013
}

function create_tenant_directories {
    # landing directories
    sudo -u root -s mkdir -p /opt/wgen/edware-udl/zones/landing/arrivals/$1
    sudo -u root -s mkdir -p /opt/wgen/edware-udl/zones/landing/work/$1
    sudo -u root -s mkdir -p /opt/wgen/edware-udl/zones/landing/history/$1

    #pickup directories
    sudo -u root -s mkdir -p /opt/wgen/edware-udl/zones/pickup/work/$1
    sudo -u root -s mkdir -p /opt/wgen/edware-udl/zones/pickup/departures/$1
    sudo -u root -s mkdir -p /opt/wgen/edware-udl/zones/pickup/history/$1

    # landing-work subdirectores
    sudo -u root -s mkdir -p /opt/wgen/edware-udl/zones/pickup/landing/work/$1/arrived
    sudo -u root -s mkdir -p /opt/wgen/edware-udl/zones/pickup/landing/work/$1/expanded
    sudo -u root -s mkdir -p /opt/wgen/edware-udl/zones/pickup/landing/work/$1/subfiles

}

function update_permissions {
     # landing directories
    sudo -u root -s chmod 777 /opt/wgen/edware-udl/zones/landing/arrivals/$1
    sudo -u root -s chmod 777 /opt/wgen/edware-udl/zones/landing/work/$1
    sudo -u root -s chmod 777 /opt/wgen/edware-udl/zones/landing/history/$1

    #pickup directories
    sudo -u root -s chmod 777 /opt/wgen/edware-udl/zones/pickup/work/$1
    sudo -u root -s chmod 777 /opt/wgen/edware-udl/zones/pickup/departures/$1
    sudo -u root -s chmod 777 /opt/wgen/edware-udl/zones/pickup/history/$1

    # landing-work subdirectores
    sudo -u root -s chmod 777 /opt/wgen/edware-udl/zones/pickup/landing/work/$1/arrived
    sudo -u root -s chmod 777 /opt/wgen/edware-udl/zones/pickup/landing/work/$1/expanded
    sudo -u root -s chmod 777 /opt/wgen/edware-udl/zones/pickup/landing/work/$1/subfiles
}

function remove_tenant_directories {
    # landing directories
    sudo -u root -s rm -rf /opt/wgen/edware-udl/zones/landing/arrivals/$1
    sudo -u root -s rm -rf /opt/wgen/edware-udl/zones/landing/work/$1
    sudo -u root -s rm -rf /opt/wgen/edware-udl/zones/landing/history/$1

    #pickup directories
    sudo -u root -s rm -rf /opt/wgen/edware-udl/zones/pickup/work/$1
    sudo -u root -s rm -rf /opt/wgen/edware-udl/zones/pickup/departures/$1
    sudo -u root -s rm -rf /opt/wgen/edware-udl/zones/pickup/history/$1

    # landing-work subdirectores
    sudo -u root -s rm -rf /opt/wgen/edware-udl/zones/pickup/landing/work/$1/arrived
    sudo -u root -s rm -rf /opt/wgen/edware-udl/zones/pickup/landing/work/$1/expanded
    sudo -u root -s rm -rf /opt/wgen/edware-udl/zones/pickup/landing/work/$1/subfiles
}

function get_opts {
    if ( ! getopts ":t:hcr" opt); then
        echo "Usage: `basename $0` options (-t tenant_name) (-c) (-r) -h for help"
        exit $E_OPTERROR;
    fi

    MODE='CREATE'
    while getopts "t:hcr" opt; do
        case $opt in
            t)
                # we may want to validate this value
                TENANT=$OPTARG 
                echo "Tenent:" $TENANT
                ;;
            c)
                echo "create mode"
                MODE="CREATE"
                ;;
            r)
                echo "remove mode"
                MODE="REMOVE"
                ;;
            h)
                show_help
                ;;
            ?)
                echo "invalid args"
                echo "Usage: `basename $0` options (-t tenant_name) -h for help"
                ;;
        esac
    done

}

function show_help {
    echo "#To add a tenant's relevant directories"
    echo "add_tenant.sh -t tenant_name"
}

function main {
    get_opts $@
    if [ ${MODE:=""} == "CREATE" ]; then
        create_tenant_directories $TENANT
        update_permissions $TENANT
        create_tenant_schema $TENANT
    elif [ ${MODE:=""} == "REMOVE" ]; then
        remove_tenant_directories $TENANT
        drop_tenant_schema $TENANT
    fi
}

main $@
