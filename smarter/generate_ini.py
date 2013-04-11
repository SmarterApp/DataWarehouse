'''
Reads a yaml file and generate an ini file according to an environment parameter.
@author:     aoren

@copyright:  2013 Wireless Generation. All rights reserved.

@contact:    edwaredevs@wgen.net
@deffield    updated: Updated
'''
import argparse
import yaml
from smarter.reports.exceptions.parameter_exception import InvalidParameterException

__all__ = []
__version__ = 0.1
__date__ = '2013-02-02'
__updated__ = '2013-02-02'

DBDRIVER = "postgresql+pypostgresql"
DEBUG = 0
VERBOSE = False


def flatten_yaml(aDict, result, path=""):
    '''
    This method runs recursively and traversing the dictionary to flatten in an ini format
    '''
    for k in aDict:
        if type(aDict[k]) != dict:
            value = "" if aDict[k] is None else str(aDict[k])
            result = result + path + k + " = " + value + "\n"
        else:
            if k.startswith('[') and k.endswith(']'):
                result = result + k + "\n"
                result = flatten_yaml(aDict[k], result, path)
            else:
                result = flatten_yaml(aDict[k], result, path + k + ".")
    return result


def generate_ini(env, input_file='settings.yaml'):
    try:
        with open(input_file, 'r') as f:
            settings = f.read()
    except:
        raise InvalidParameterException(str.format("could not find or open file {0} for read", input_file))

    settings = yaml.load(settings)

    if env not in settings:
        raise InvalidParameterException(str.format("could not find settings for {0} in the yaml file", env))
    env_settings = settings[env]
    common_settings = settings['common']

    groups = {}
    for group in env_settings:
        groups[group] = groups.get(group, "") + flatten_yaml(env_settings[group], "", "")
    for group in common_settings:
        groups[group] = groups.get(group, "") + flatten_yaml(common_settings[group], "", "")
    result = ''.join([group + "\n" + groups[group] for group in groups])

    output_file = env + ".ini"
    try:
        with open(output_file, 'w') as f:
            f.write(result)
        print(result)
    except:
        raise IOError(str.format('could not open file {0} for write', output_file))

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create New Schema for EdWare')
    parser.add_argument("-e", "--env", default='dev', help="set environment name.")
    parser.add_argument("-i", "--input", default="settings.yaml", help="set input yaml file name default[settings.yaml]")
    args = parser.parse_args()

    if args.env is None:
        print("Please specifiy --env option")
        exit(-1)
    try:
        generate_ini(args.env, args.input)
    except Exception as ipe:
        print(ipe)
