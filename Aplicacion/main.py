from minikube.mk import minikube
from parsers.argparser import argparser
import yaml
from parsers.jsoncontroller import JsonController


def parser_yaml(Path):
    with open(Path) as yaml_data:
        yaml_parsed = yaml.load(yaml_data, Loader=yaml.Loader)

    return yaml_parsed

Debug = True
#Argument parser call
arp = argparser()

args = arp.getArgs()




if Debug:
    print(args)

var = vars(args)
mk = minikube(var.get('Verbose'))
if var.get('File'):
    yaml = parser_yaml(var.get('File'))
    print(yaml['MiniKube'])
    print(yaml['MiniKube']['mount']['Host'])
    mk.start(yaml['MiniKube'])

if var.get('Cluster'):
    print('Adios')
