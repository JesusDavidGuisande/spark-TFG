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
mk = minikube(var.get('verbose'))
if var.get('File'):
    yaml = parser_yaml(var.get('File'))
    #mk.start(yaml['MiniKube'])
    json = JsonController()
    json.add_object('pid-mount', 'pid', 12)
    res = json.get_object('pid-mount')
    print(res)
    json.delete_object('pid-mount', 'pid')
    print(json.get_object('pid-mount'))

if var.get('Cluster'):
    print('Adios')
