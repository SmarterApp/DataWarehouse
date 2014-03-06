import logging
from edudl2.json_util.json_util import get_value_from_json
from edudl2.udl2.celery import udl2_conf

__author__ = 'tshewchuk'

logger = logging.getLogger(__name__)
load_types = udl2_conf['load_type'].values()


def get_load_type(json_file_dir):
    """
    Get the load type for this UDL job from the json file
    @param json_file_dir: A directory that houses the json file
    @return: UDL job load type
    @rtype: string
    """

    load_type = get_value_from_json(json_file_dir, udl2_conf['load_type_key']).lower()

    if load_type not in load_types:
        raise ValueError('No valid load type specified in json file --')

    return load_type
