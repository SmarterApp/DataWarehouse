#!/bin/bash

set -e # Exit on errors

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

function remove_tenant_directories {
    # landing directories
    sudo -u -s rm -rf /opt/wgen/edware-udl/zones/landing/arrivals/$1
    sudo -u -s rm -rf /opt/wgen/edware-udl/zones/landing/work/$1
    sudo -u -s rm -rf /opt/wgen/edware-udl/zones/landing/history/$1

    #pickup directories
    sudo -u -s rm -rf /opt/wgen/edware-udl/zones/pickup/work/$1
    sudo -u -s rm -rf /opt/wgen/edware-udl/zones/pickup/departures/$1
    sudo -u -s rm -rf /opt/wgen/edware-udl/zones/pickup/history/$1

    # landing-work subdirectores
    sudo -u -s rm -rf /opt/wgen/edware-udl/zones/pickup/landing/work/$1/arrived
    sudo -u -s rm -rf /opt/wgen/edware-udl/zones/pickup/landing/work/$1/expanded
    sudo -u -s rm -rf /opt/wgen/edware-udl/zones/pickup/landing/work/$1/subfiles
}

function get_opts {
    if ( ! getopts "t:hcr" opt); then
        echo "Usage: `basename $0` options (-t tenant_name) -h for help"
        echo $E_OPTERROR;
    fi

    MODE='CREATE'
    while getopts "t:hcr" opt; do
        case $opt in
            t)
                TENANT=$OPTARG
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
    elif [ ${MODE:=""} == "REMOVE" ]; then
        remove_tenant_directories $TENANT
    fi
}

main $@
