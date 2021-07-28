import os
import sys
import time

import yaml
from kubernetes_control.kubernetes_control import *
from parsers.jsoncontroller import JsonController
import subprocess


class minikube:

    def __init__(self, trace):
        # define the slots
        self.description = 'local kubernetes cluster'
        self.wd = os.getcwd()
        self.log_trace = trace
        self.__check_installed()
        self.json = JsonController()

    def __check_installed(self):

        # check if virtualbox is installed
        not_installed_list = []
        try:
            # check if cli is recognized
            command = str('virtualbox --help')
            subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            # installed if not crashed
        # handle exception
        except:

            # not installed
            not_installed_list.append('VirtualBox')

        # check if kubectl is already installed
        try:

            # check if cli is recognized
            command = str('kubectl config view')
            subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            # installed if not crashed
            kc_installed = True

        # handle exception
        except:

            # not installed
            kc_installed = False

        # check if minikube is installed
        try:

            # check if cli is recognized
            command = str('minikube version')
            subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            # installed if not crashed
            mk_installed = True

        # handle exception
        except:

            # not installed
            not_installed_list.append('MiniKube')

        # check if docker is installed
        try:

            # check if cli is recognized
            command = str('docker ps -a')
            subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            # installed if not crashed
            dk_installed = True

        # handle exception
        except:

            # not installed
            not_installed_list.append('Docker')

        # store info in object
        if not_installed_list:
            raise Exception('The following programs are not installed ' + ' '.join(not_installed_list))

    # function to start minikube
    def start(self, dict={}, restart=False):
        if restart:
            profile = self.json.get_object('profiles')
            command = str('minikube start -p ' + profile['profile'])
        else:
            command = str('minikube start --driver=' + dict['driver'] +
                          ' --cpus=' + str(dict['cpus']) + ' --memory=' + dict['memory'])
            if 'namespace' in dict:
                command += ' --namespace ' + dict['namespace']

            if 'profile' in dict:
                command += ' -p ' + dict['profile']
                self.json.add_object('profiles', 'profile', dict['profile'])
            else:
                self.json.add_object('profiles', 'profile', 'default')
            if 'nodes' in dict:
                command += ' --nodes=' + str(dict['nodes'])

        # Mount a local directory in the cluster (not in the deploy of spark)
        # try to start minikube
        try:

            # start minikube
            # if log_trace is asked for
            if self.log_trace:

                # run command with trace
                process_start = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(process_start.stdout.read().decode(sys.getdefaultencoding()))
                print(process_start.stderr.read().decode(sys.getdefaultencoding()))
                process_start.stdout.close()
                process_start.stderr.close()
            # if log_trace is not asked for
            else:

                # run command without trace
                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


        # return error if it doesn't work
        except:

            # raise error
            raise Exception('Starting Minikube failed')
        #todo comprobar el lugar donde saltan las excepciones para que salgan bien
        #Hacer que falle para que se imprima por pantalla algo descriptivo o
        #se destruya el cluster
        if 'mount' in dict:
            pid = os.fork()
            if pid == 0:
                self.__mount_volume(dict)
            else:
                self.json.add_object('pid-mount', 'pid', pid)
        if 'persistent-volume' in dict:
            time.sleep(5)
            self.persistent_volume(dict)
        rolebinding()
    def __mount_volume(self, dict):
        try:
            command = str('minikube mount ' + dict['mount']['Host'] + ':' + dict['mount']['Cluster'])
            if 'profile' in dict:
                command = command + ' -p ' + dict['profile']

            if self.log_trace:
                # run command with trace
                resultado = subprocess.Popen(command.split(),
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                res_string = str(resultado.stdout.read().decode(sys.getdefaultencoding()))
                err_string = str(resultado.stderr.read().decode(sys.getdefaultencoding()))
                resultado.stdout.close()
                resultado.stderr.close()

                print(res_string)
                if err_string != '':
                    raise Exception(err_string)
            # if log_trace is not asked for
            else:
                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        except:

            raise Exception('The volume has not been mounted')

    def persistent_volume(self, dict):

        doc = {}
        try:
            with open('./templates/volume.yaml') as f:
                doc = yaml.load(f)

            #Path used to mount a local directory on the cluster
            doc['spec']['hostPath']['path'] = dict['mount']['Cluster']

            if 'persistent-volume' in dict:
                data = dict['persistent-volume']

            if 'name' in data:
                doc['metadata']['name'] = data['name']

            if 'capacity' in data:
                doc['spec']['capacity']['storage'] = data['capacity']

            if 'accessModes' in data:
                doc['spec']['accessModes'][0] = data['accessModes']

            if 'storageClassName' in data:
                doc['spec']['storageClassName'] = data['storageClassName']

            with open('./templates/volume.yaml', 'w') as f:
                yaml.dump(doc, f, default_flow_style=False)

            apply_file('./templates/volume.yaml')

        except Exception as e:
            print(e)

    def status(self, status):

        # try to apply new status changer minikube
        try:

            # apply status minikube
            profile = self.json.get_object('profiles')
            command = str('minikube ' + status + ' -p ' + profile['profile'])
            # todo Recoger la stdout del comando en una variable para
            # analizar el estado del cluster en el restart
            if self.log_trace:

                # run command with trace
                subprocess.run(command.split(), capture_output=True)

            # if log_trace is not asked for
            else:
                subprocess.call(command.split(), catpture_output=True)

        # return error if it doesn't work
        except:

            # raise error
            raise Exception('Could not change status on minikube')

        # function to delete minikube

    def delete(self):

        # try to delete minikube
        try:
            # delete minikube
            profile = self.json.get_object('profiles')
            command = str('minikube delete -p ' + profile['profile'])

            pid = self.json.get_object('pid-mount')
            killcmd = str('kill -9 ' + str(pid['pid']))
            if self.log_trace:
                subprocess.call(command.split())

                subprocess.call(killcmd.split())
            else:

                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

                subprocess.call(killcmd.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            self.json.delete_object('pid-mount', 'pid')
            self.json.delete_object('profiles', 'profile')

        except:

            # raise error
            raise Exception('Could not delete minikube cluster')
