import time

from minikube.mk import minikube
from parsers.argparser import argparser
from spark.spark import spark
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
sparkHome = j.get_object('spark-home')
if var.get('sparkHome'):
    j.add_object('spark-home', 'path', var.get('sparkHome'))
    exit(0)

if sparkHome:
    print(sparkHome)
    print(var)
    if var.get('test'):
        sp = spark()
        sp.submit()


    if var.get('File'):

        if var.get('fs'):
            yaml_template = parser_yaml('./templates/default-mk.yaml')
            mk_template = yaml_template['MiniKube']
            spark_template = parser_yaml(var.get('File'))['Spark']

        else:
            full_template = var.get('File')
            mk_template = full_template['MiniKube']
            spark_template = full_template['Spark']

        mk.start(mk_template)
        #sp = spark(spark_template)
        #sp.submit()


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


else:
    print('First you need to get the path for spark')