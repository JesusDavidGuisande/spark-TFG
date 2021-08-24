import time

from parsers.jsoncontroller import JsonController
from kubernetes_control.kubernetes_control import *
import subprocess
import os


class Spark:

    def __init__(self, minikube, cloud, json):
        self.dict = None
        self.mk = minikube
        self.json = json
        self.volumes = []
        self.cloud = cloud

    def dump_volumes(self):
        self.volumes = []

    def submit(self, dict):
        """Construccion del comando spark-submit con sus opciones correspondientes"""
        self.dict = dict
        end = ' '
        command = str(self.json.get_object('spark-home')['path'])
        command += str('/bin/spark-submit') + end
        command += str('--master k8s://') + master_ip() + end
        command += str('--deploy-mode cluster') + end
        command += str('--name ') + dict['name'] + end
        command += str('--class ') + dict['class'] + end
        command += str('--conf spark.kubernetes.driver.pod.name=sparky-driver') + end

        if 'executor-instances' in dict:
            nexec = dict['executor-instances']
            command += str('--conf spark.executor.instances=') + str(dict['executor-instances']) + end
        else:
            raise Exception('Obligatory parameter "executor-instances" in spark template ex. => executor-instances: 2')
        if 'driver-conf' in dict:
            if 'driver-cpus' in dict['driver-conf']:
                command += str('--conf spark.driver.cores=') + str(dict['driver-conf']['driver-cpus']) + end
            else:
                raise Exception('Obligatory parameter "driver-cpus" inside optional parameter "driver-conf" in '
                                'spark template ex.=> driver-cpus: 1')
            if 'driver-memory' in dict['driver-conf']:
                command += str('--conf spark.driver.memory=') + dict['driver-conf']['driver-memory'] + end
            else:
                raise Exception('Obligatory parameter "driver-memory" inside optional parameter "driver-conf" in '
                                'spark template ex.=> driver-memory: 1g')

        if 'executor-conf' in dict:
            if 'executor-cpus' in dict['executor-conf']:
                command += str('--conf spark.executor.cores=') + str(dict['executor-conf']['executor-cpus']) + end

            else:
                raise Exception('Obligatory parameter "executor-cpus" inside optional parameter "executor-conf" in '
                                'spark template ex.=> executor-cpus: 1')

            if 'executor-memory' in dict['executor-conf']:
                command += str('--conf spark.executor.memory=') + dict['executor-conf']['executor-memory'] + end
            else:
                raise Exception('Obligatory parameter "executor-memory" inside optional parameter "executor-conf" in '
                                'spark template ex.=> executor-memory: 1g')





        if 'mount' in dict:
            for pv in dict['mount']:
                try:
                    self.volumes.append(pv['name'])
                    self.mk.mount_volume(pv)
                    time.sleep(5)
                    self.mk.persistent_volume(pv)
                    file = './templates/volumes/volume' + pv['name'] + '.yaml'
                    while True:
                        if os.path.exists(file):
                            break
                        else:
                            time.sleep(2)
                    apply_file('./templates/volumes/volume' + pv['name'] + '.yaml')
                except Exception as e:
                    pass



            for place in ('driver', 'executor'):
                command += str('--conf spark.kubernetes.') + place + str('.volumes.hostPath.') + \
                           pv['name'] + str('.mount.path=') + '/mnt/data/' + pv['name'] + end

                command += str('--conf spark.kubernetes.') + place + str('.volumes.hostPath.') + \
                           pv['name'] + str('.options.path=') + '/mnt/data/' + pv['name'] + end
        if 'conf' in dict:
            for line in dict['conf']:
                command += str('--conf ') + line + end
            # todo seleccion de version de imagen // poder pasar una imagen xx prueba con una + \
            #  imagen distinta
        if 'image' in dict:

            """Permitimos seleccionar una imagen en un repositorio publico o una version de
             una imagen por defecto"""

            if 'image' in dict['image']:
                command += str('--conf spark.kubernetes.container.image=') + str(dict['image']['image']) + end
            elif 'version' in dict['image']:
                command += str('--conf spark.kubernetes.container.image=jesusdavidguisande/spark:') + \
                           dict['image']['version']
            else:
                raise Exception('Parameters image or version must be specify inside image parameter.'
                                'ex => image: repor/image:tag  or version: tag')
        if 'jars' in dict:
            if 'mode' in dict['jars']:
                if 'path' in dict['jars']:

                    if dict['jars']['mode'] == 'local':
                        command += dict['jars']['mode'] + ':///mnt/data/' + dict['jars']['path']
                    else :
                        command += dict['jars']['mode'] + '://' + dict['jars']['path']
                else:
                    raise Exception('Obligatory parameter "path" inside obligatory parameter "jars" '
                                    'in spark template ex.=> path: pv0001/spark-examples_2.12-3.1.2.jar')
            else:
                raise Exception('Obligatory parameter "mode" inside obligatory parameter "jars"'
                                'in spark template ex.=> mode: {local, https}')
        else:
            raise Exception('Obligatory paramter "jars" in spark template')


        if 'input-args' in dict:
            command += end
            for line in dict['input-args']:
                command += line + ' '

        print(command)
        #todo borrar sleep
        #time.sleep(20)
        try:
            subprocess.call(command.split())
            get_log()
        except Exception as e:
            print(e)

