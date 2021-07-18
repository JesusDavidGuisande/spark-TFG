import os
import sys

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
    def start(self, dict):

        command = str('minikube start --driver=' + dict['driver'] +
                      ' --cpus=' + str(dict['cpus']) + ' --memory=' + dict['memory'])
        if 'namespace' in dict:
            command += ' --namespace ' + dict['namespace']

        if 'profile' in dict:
            command += ' -p ' + dict['profile']


        #Mount a local directory in the cluster (not in the deploy of spark)
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


        if 'mount' in dict:
            pid = os.fork()
            if pid == 0:
               self.__mount_volume(dict)
            else:
                self.json.add_object('pid-mount', 'pid', pid)

    def __mount_volume(self, dict):
        try:
            command = str('minikube mount ' + dict['mount']['Host'] + ':' + dict['mount']['Cluster'])
            if 'profile' in dict:
                command += command + ' -p ' + dict['profile']

            if self.log_trace:

                # run command with trace
                subprocess.call(command.split())

            # if log_trace is not asked for
            else:
                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        except:

            raise Exception('The volume has not been mounted')

    def stop(self):

        # try to stop minikube
        try:

            # stop minikube
            command = str('minikube stop')

            if self.log_trace:

                # run command with trace
                subprocess.call(command.split())

            # if log_trace is not asked for
            else:
                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        # return error if it doesn't work
        except:

            # raise error
            raise Exception('I could not stop minikube')

        # function to delete minikube

    def delete(self):

        # try to delete minikube
        try:
            # delete minikube
            command = str('minikube delete')
            pid = self.json.get_object('pid-mount')
            killcmd = str('kill -9 ' + pid)

            if self.log_trace:
                subprocess.call(command.split())

                subprocess.call(killcmd.split())
            else:

                subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

                subprocess.call(killcmd.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            self.json.delete_list_object('pid-mount', 'pid', pid)

        except:

            # raise error
            raise Exception('Could not delete minikube cluster')
