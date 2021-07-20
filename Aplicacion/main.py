import time

from minikube.mk import minikube
from parsers.argparser import argparser
from parsers.jsoncontroller import JsonController
from kubernetes_control.kubernetes_control import kubernetes_control
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
j = JsonController()
if var.get('File'):

    if var.get('fs'):
        mk_template_path = ('./templates/default-mk.yaml')
        spark_template = parser_yaml(var.get('File'))
    else:
        mk_template_path = var.get('File')

    j.add_object('template-path', 'path', mk_template_path)

    mk_template = parser_yaml(mk_template_path)
    mk.start(mk_template['MiniKube'])
    time.sleep(5)
    kb = kubernetes_control(mk_template['MiniKube']['namespace'])
    print(kb.master_ip())

if var.get('cluster'):
    status = var.get('cluster')
    print(status)

    if status == 'stop' or status == 'pause' \
            or status == 'unpause':
        mk.status(status)

    elif status == 'restart':
        mk.start(restart=True)

    elif status == 'delete':
        print('Deleting...')
        mk.delete()


