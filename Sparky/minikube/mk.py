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

    def set_logTrace(self, trace):
        self.log_trace = trace

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
            command = str('minikube start ')
            if 'profile' in dict:
                command += ' -p ' + dict['profile'] + ' '
                self.json.add_object('profiles', 'profile', dict['profile'])
            else:
                self.json.add_object('profiles', 'profile', 'default')

            if 'driver' in dict:
                command += '  --driver=' + dict['driver']

            if 'cpus' in dict:
                command += ' --cpus=' + str(dict['cpus'])

            if 'memory' in dict:
                command += ' --memory=' + dict['memory']

            if 'namespace' in dict:
                command += ' --namespace=' + dict['namespace']

            if 'nodes' in dict:
                command += ' --nodes=' + str(dict['nodes'])
            print(command)
        # Mount a local directory in the cluster (not in the deploy of spark)
        # try to start minikube
        try:

            # start minikube
            # if log_trace is asked for
            if self.log_trace:

                # run command with trace
                process_start = subprocess.Popen(command.split(), stderr=subprocess.PIPE)
                # print(process_start.stdout.read().decode(sys.getdefaultencoding()))
                print(process_start.stderr.read().decode(sys.getdefaultencoding()))
                # process_start.stdout.close()
                process_start.stderr.close()
            # if log_trace is not asked for
            else:

                # run command without trace
                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


        # return error if it doesn't work
        except:

            # raise error
            raise Exception('Starting Minikube failed')
        # todo comprobar el lugar donde saltan las excepciones para que salgan bien
        # Hacer que falle para que se imprima por pantalla algo descriptivo o
        # se destruya el cluster
        if restart:
            rolebinding()

    def mount_volume(self, list):

        for line in list:
            pid = os.fork()
            if pid == 0:
                try:
                    command = str('minikube mount')
                    perfil = self.json.get_object('profiles')
                    command = command + ' -p ' + perfil['profile'] + ' '
                    command += line['local-path'] + ':' + line['cluster-path']

                    if self.log_trace:
                        # run command with trace
                        subprocess.call(command.split())
                    # if log_trace is not asked for
                    else:
                        subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    exit(0)
                except:

                    raise Exception('The volume has not been mounted')
            else:
                self.json.add_list_object("pid-mount", "pid", pid)

    def persistent_volume(self, dict):

        doc = {}
        try:
            with open('./templates/volume.yaml') as f:
                doc = yaml.load(f)

            # Path used to mount a local directory on the cluster
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
            if self.log_trace:

                # run command with trace
                subprocess.run(command.split())

            # if log_trace is not asked for
            else:
                subprocess.call(command.split(), stderr=None, stdout=None)

        # return error if it doesn't work
        except:

            # raise error
            raise Exception('Could not change status on minikube')

        # function to delete minikube

    def dashboard(self, arg):
        if arg == 'kill':
            dashpid = self.json.get_object('pid-dashboard')
            command = str('kill -9 ' + int(dashpid['pid']))
            try:
                if self.log_trace:

                    # run command with trace
                    subprocess.run(command.split(), capture_output=True)

                # if log_trace is not asked for
                else:
                    subprocess.call(command.split(), stdout=None, stderr=None)
            except:
                raise Exception('Can not kill dashboard process')
        else:
            pid = os.fork()
            if pid == 0:
                try:

                    profile = self.json.get_object('profiles')
                    command = str('minikube dashboard -p ' + profile['profile'])

                    if self.log_trace:

                        # run command with trace
                        subprocess.run(command.split(), capture_output=True)

                    # if log_trace is not asked for
                    else:
                        subprocess.call(command.split(), catpture_output=True)

                    # return error if it doesn't work
                    exit(0)
                except:

                    # raise error
                    raise Exception('Could not display the minikube dashboard')
            else:
                self.json.add_object('pid-dashboard', 'pid', pid)

    def delete(self):

        # try to delete minikube
        try:
            # delete minikube
            profile = self.json.get_object('profiles')
            command = str('minikube delete -p ' + profile['profile'])

            piddash = self.json.get_object('pid-dashboard')

            if piddash != {}:
                killdash = str('kill -9 ' + str(piddash['pid']))
                self.json.delete_object('pid-dashboard', 'pid')

            list_pid = self.json.get_object('pid-mount')

            if self.log_trace:
                subprocess.call(command.split())

                for pid in list_pid:
                    killcmd = str('kill -9 ' + str(pid['pid']))
                    subprocess.call(killcmd.split())
                    self.json.delete_object('pid-mount', int(pid['pid']))
                if piddash != {}:
                    subprocess.call(killdash.split())
            else:

                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

                for pid in list_pid:
                    killcmd = str('kill -9 ' + str(pid['pid']))
                    subprocess.call(killcmd.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    self.json.delete_object('pid-mount', int(pid['pid']))

                if piddash != {}:
                    subprocess.call(killdash.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            self.json.delete_object('profiles', 'profile')

        except Exception as e:
            print(e)
