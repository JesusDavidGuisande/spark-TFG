from parsers.jsoncontroller import JsonController
from kubernetes_control.kubernetes_control import *
import subprocess
import sys

class spark:

    def __init__(self, dict):
        self.dict = dict
        self.json = JsonController()

    def submit(self):
        dict = self.dict
        end = ' '
        command = str(self.json.get_object('spark-home')['path'])
        command += str('/bin/spark-submit') + end
        command += str('--master k8s://') + master_ip() + end
        command += str('--deploy-mode cluster') + end
        command += str('--name ') + dict['name'] + end
        command += str('--class ') + dict['class'] + end
        if 'mount' in dict:
            for place in ('driver', 'executor'):
                command += str('--conf spark.kubernetes.') + place + str('.volumes.hostPath.') + \
                           dict['mount']['name'] + str('.mount.path=') + dict['mount']['path'] + end

                command += str('--conf spark.kubernetes.') + place + str('.volumes.hostPath.') + \
                           dict['mount']['name'] + str('.options.path=') + dict['mount']['path'] + end

        for line in dict['conf']:
            command += str('--conf ') + line + end
        #todo seleccion de version de imagen // poder pasar una imagen
        if 'image' in dict:
            command += str('--conf spark.kubernetes.container.image=') + dict['image'] + end

        command += dict['jars']['mode'] + '://' + dict['jars']['path']

        if 'input-args' in dict:
            command += end
            for line in dict['input-args']:
                command += line + ' '

        print(command)

        #todo ver si salida a fichero o por pantalla, es muchas lineas!!

        try:
            resultado = subprocess.Popen(command.split(), stderr=subprocess.PIPE)

            err_string = str(resultado.stderr.read().decode(sys.getdefaultencoding()))
            resultado.stderr.close()

            # print(res_string)
            if err_string != '':
                #todo revisar mensaje de excepcion
                raise Exception(err_string)
        except Exception as e:
            print(e)

