import glob
import os
import time

import yaml
from kubernetes_control.kubernetes_control import *
from parsers.jsoncontroller import JsonController
import subprocess


class Minikube:

    def __init__(self, trace):
        # define the slots
        self.description = 'local kubernetes cluster'
        self.wd = os.getcwd()
        self.verbose = trace
        self.__check_installed()
        self.json = JsonController()
        self.ncores = None
        self.memory = None
        self.isStarted = False
        self.profile = None
    #Getter y setter de verbose
    def get_log_trace(self):
        return self.verbose

    def set_log_trace(self, log):
        self.verbose=log

    def get_profile(self):
        if self.profile is not None:
            return self.profile
        else:
            profile = self.json.get_object('profiles')
            self.profile = profile
            return profile

    def get_cores(self):
        return self.ncores

    def get_memory(self):
        return self.memory

    def __check_installed(self):
        """Se comprueba que docker, virtualbox, minikube y kubernetes"""
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

        # handle exception
        except:

            # not installed
            not_installed_list.append('kubectl')

        # check if Minikube is installed
        try:

            # check if cli is recognized
            command = str('minikube version')
            subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


        # handle exception
        except:

            # not installed
            not_installed_list.append('minikube')

        # check if docker is installed
        try:

            # check if cli is recognized
            command = str('docker ps -a')
            subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


        # handle exception
        except:

            # not installed
            not_installed_list.append('Docker')

        # store info in object
        if not_installed_list:
            raise Exception('The following programs are not installed ' + ' '.join(not_installed_list))

    # function to start Minikube



    def start(self, dict, restart=False):
        """Se define las opciones con las que se ejecuta el cluster de kubernetes en minikube"""
        if restart:
            profile = self.get_profile()
            command = str('minikube start -p ' + profile)
        else:
            command = str('minikube start ')


            """Se define el perfil en el que se quiere operar el cluster"""
            if 'profile' in dict:
                self.profile = dict['profile']
                command += ' -p ' + dict['profile'] + ' '
                self.json.add_object('profiles', 'profile', dict['profile'])
            else:
                self.profile = 'default'
                self.json.add_object('profiles', 'profile', 'default')
            """Se define el driver sobre el que se ejecuta minikube"""
            if 'driver' in dict:
                command += '  --driver=' + dict['driver']
            else:
                raise Exception('Obligatory parameter "driver" in minikube template ex. => driver: {docker, virtualbox}')

            """Numero de cores asignados al cluster"""
            if 'cpus' in dict:
                command += ' --cpus=' + str(dict['cpus'])
                self.ncores = dict['cpus']
            else:
                raise Exception('Obligatory parameter "cpus" in minikube template ex. => cpus: 2')

            """Memoria asignada al cluster"""
            if 'memory' in dict:
                command += ' --memory=' + dict['memory']
                self.memory = dict['memory']
            else:
                raise Exception('Obligatory parameter "memory" in minikube template ex. => memory: 2g')

            """Namespace personal del cluster"""
            if 'namespace' in dict:
                command += ' --namespace=' + dict['namespace']

            """Numero de nodos del cluster"""
            if 'nodes' in dict:
                command += ' --nodes=' + str(dict['nodes'])

        try:

            if self.verbose:

                # run command with trace
                process_start = subprocess.Popen(command.split(), stderr=subprocess.PIPE)
                print(process_start.stderr.read().decode(sys.getdefaultencoding()))
                process_start.stderr.close()
            # if verbose is not asked for
            else:

                # run command without trace
                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


        # return error if it doesn't work
        except Exception as e:
            print('Minikube cluster do not start \n' + str(e))
        # todo comprobar el lugar donde saltan las excepciones para que salgan bien

        if not restart:
            rolebinding()
        self.isStarted = True

    def mount_volume(self, dict):
        """Funcion que permite montar un directorio del equipo local en el cluster de kubernetes
            se inicia en un nuevo proceso dado que necesita estar activo para el montaje y esto es bloqueante"""
        pid = os.fork()
        if pid == 0:
            try:
                command = str('minikube mount')
                perfil = self.json.get_object('profiles')
                command = command + ' -p ' + perfil['profile'] + ' '
                command += dict['local-path'] + ':/mnt/data/' + dict['name']

                if self.verbose:
                    # run command with trace
                    subprocess.call(command.split())
                # if verbose is not asked for
                else:
                    subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                exit(0)

            except Exception as e:
                raise Exception('The volume has not been mounted \n' + str(e))

        else:
            self.json.add_list_object("pid-mount", "pid", pid)

    def persistent_volume(self, dict):
        """Se crea un volumen persistente en el cluster con las indicaciones que se le facilitan
        con el submit de spark, que permiten usar los ficheros compartidos con el cluster"""

        """Se parte de una plantilla por defecto vacia que se completa con los datos que pasa el usuario"""
        doc = {}
        output_file = './templates/volumes/volume' + dict['name'] + '.yaml'
        try:
            with open('./templates/volume.yaml') as f:
                doc = yaml.load(f)

            # Path used to mount a local cluster directory in the volume
            doc['spec']['hostPath']['path'] = '/mnt/data/' + dict['name']

            if 'name' in dict:
                doc['metadata']['name'] = dict['name']
            else:
                raise Exception('Obligatory parameter "name" in spark template, mount ex. => name: pv0001')

            if 'capacity' in dict:
                doc['spec']['capacity']['storage'] = dict['capacity']
            else:
                print('Applying default options in the capacity attribute 2Gi')
                doc['spec']['capacity']['storage'] = '2Gi'

            if 'accessModes' in dict:
                doc['spec']['accessModes'][0] = dict['accessModes']
            else:
                print('Applying default options in the accessModes attribute ReadWriteMany')
                doc['spec']['accessModes'][0] = 'ReadWriteMany'

            if 'storageClassName' in dict:
                doc['spec']['storageClassName'] = dict['storageClassName']
            else:
                print('Applying default options in the storageClassName attribute')
                doc['spec']['storageClassName'] = 'manual'

                # todo comprobar que creo los ficheros de los volumenes
            with open(output_file, 'w') as fw:
                yaml.dump(doc, fw, default_flow_style=False)

        except Exception as e:
            print(e)

    def status(self, status):
        """ Aplica un estado al cluster de los que permite minikube"""
        # try to apply new status changer Minikube
        try:

            # apply status Minikube
            profile = self.json.get_object('profiles')
            command = str('minikube ' + status + ' -p ' + profile['profile'])
            if self.verbose:

                # run command with trace
                subprocess.run(command.split())

            # if verbose is not asked for
            else:
                subprocess.call(command.split(), stderr=None, stdout=None)

        # return error if it doesn't work
        except Exception as e:

            # raise error
            raise Exception('Could not change status on Minikube: ' + str(e))

        # function to delete Minikube

    def check_directory_exist(self, directory):
        profile = self.get_profile()
        cmd_check_dir_mount = str('minikube ssh -p ' + profile + ' "test -d ' + directory + ' && echo Existe"')
        while True:
            try:
                res = subprocess.Popen(cmd_check_dir_mount.split(), stdout=subprocess.PIPE)
                stdout_string = str(res.stdout.read().decode(sys.getdefaultencoding()))
                res.stdout.close()
                i = 0
                if stdout_string == 'Existe' or i == 30:
                    break
                else:
                    i += 1
                    time.sleep(2)
            except Exception as e:
                print('Error ocurred when directory mout check: ' + str(e))


    def delete(self):
        """ Detencion y borrado del cluster, asi como el borrado de los pid de los procesos auxiliares"""
        # try to delete Minikube
        try:
            # delete Minikube
            profile = self.json.get_object('profiles')
            command = str('minikube delete -p ' + profile['profile'])

            piddash = self.json.get_object('pid-dashboard')

            if piddash != {}:
                killdash = str('kill -9 ' + str(piddash['pid']))
                self.json.delete_object('pid-dashboard', 'pid')

            list_pid = self.json.get_object('pid-mount')


            files = glob.glob('./templates/volumes/*')
            for f in files:
                os.remove(f)

            if self.verbose:

                subprocess.call(command.split())


                for line in list_pid:
                    pid = line['pid']
                    killcmd = str('kill -9 ' + str(pid))
                    self.json.delete_list_object('pid-mount', 'pid', int(pid))
                    try:
                        subprocess.call(killcmd.split())
                    except Exception as e:
                        print(str(e))

                if piddash != {}:
                    subprocess.call(killdash.split())
            else:

                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

                for line in list_pid:
                    pid = line['pid']
                    killcmd = str('kill -9 ' + str(pid))
                    self.json.delete_list_object('pid-mount', 'pid', pid)
                    try:
                        subprocess.call(killcmd.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    except Exception as e:
                        print(str(e))

                if piddash != {}:
                    subprocess.call(killdash.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            self.json.delete_object('profiles', 'profile')

        except Exception as e:
            print(e)
