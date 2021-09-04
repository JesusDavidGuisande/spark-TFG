import os

import yaml
from kubernetes_control.kubernetes_control import *
import subprocess
from multiprocessing import Process


class Minikube:

    def __init__(self, trace, json):
        # define the slots
        self.description = 'local kubernetes cluster'
        self.wd = os.getcwd()
        self.verbose = trace
        self.__check_installed()
        self.json = json
        self.ncores = None
        self.memory = None
        self.isStarted = False
        self.profile = None
        self.namespace = None
        self.list_persistent_volume = []

    # Getter y setter de verbose
    def get_log_trace(self):
        return self.verbose

    def set_log_trace(self, log):
        self.verbose = log

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

    def get_namespace(self):
        return self.namespace

    def get_pv(self):
        return self.list_persistent_volume

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
                raise Exception(
                    'Obligatory parameter "driver" in minikube template ex. => driver: {docker, virtualbox}')

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

        if not restart:
            ServiceConfig()
        self.isStarted = True

    def mount_volume(self, dict):
        def find(key, value, list):
            rtr = False
            for i in list:
                if i[key] == value:
                    rtr = True
                    break
            return rtr

        if not find('name', dict['name'], self.list_persistent_volume):
            proc = Process(target=self.__mount_volume, args=(dict,))
            self.list_persistent_volume.append({'name': dict['name'], 'proc': proc})
            proc.start()

    def __mount_volume(self, dict):
        """Funcion que permite montar un directorio del equipo local en el cluster de kubernetes
            se inicia en un nuevo proceso dado que necesita estar activo para el montaje y esto es bloqueante"""
        try:
            command = str('minikube mount')
            # todo ver porque a veces falla este json
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
            exit('The volume has not been mounted \n' + str(e))

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
                print('Applying default options in the capacity attribute: 2Gi')
                doc['spec']['capacity']['storage'] = '2Gi'

            if 'accessModes' in dict:
                doc['spec']['accessModes'][0] = dict['accessModes']
            else:
                print('Applying default options in the accessModes attribute: ReadWriteMany')
                doc['spec']['accessModes'][0] = 'ReadWriteMany'

            if 'storageClassName' in dict:
                doc['spec']['storageClassName'] = dict['storageClassName']
            else:
                print('Applying default options in the storageClassName attribute: manual')
                doc['spec']['storageClassName'] = 'manual'

            with open(output_file, 'w') as fw:
                yaml.dump(doc, fw, default_flow_style=False)

        except Exception as e:
            print('Error building a volume template: ' + str(e))

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
        cmd_check_dir_mount = str('minikube ssh -p ' + profile + ' "test -d ' + directory + '" && echo Existe $$ exit')
        while True:
            try:
                res = subprocess.Popen(cmd_check_dir_mount, shell=True, stdout=subprocess.PIPE)
                stdout_string = str(res.stdout.read().decode(sys.getdefaultencoding()))
                res.stdout.close()
                i = 0
                if i == 10:
                    raise Exception('Wait 20 secs for volume mount')
                if 'Existe' in stdout_string:
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
            if not profile:
                print('The cluster has already been deleted or does not exist')
                return
            command = str('minikube delete -p ' + profile['profile'])
            self.clean_pv_mount('ALL')
            if self.verbose:

                subprocess.call(command.split())


            else:

                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            self.json.delete_object('profiles', 'profile')



        except Exception as e:
            print(e)

    def clean_pv_mount(self, name):
        basePath = './templates/volumes/'
        files = os.listdir(basePath)
        for f in files:
            os.remove(basePath + f)

        for pv in self.list_persistent_volume[:]:
            # Se eliminan todos los procesos que montan los directorios locales en el cluster
            if name == 'ALL':
                delete_volumes(pv['name'])
                pv['proc'].kill()
                self.list_persistent_volume.remove(pv)

            # Se eliminan el proceso asociado a un volumen persistente que introduce el usuario
            elif name == pv['name']:
                delete_volumes(pv['name'])
                pv['proc'].kill()
                self.list_persistent_volume.remove(pv)
