import subprocess
import sys
import re
from kubernetes import *

ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')


def master_ip():
    command = str('kubectl cluster-info')
    try:

        resultado = subprocess.Popen(command.split(),
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        string = ansi_escape.sub('', resultado.stdout.read().decode(sys.getdefaultencoding()))
        resultado.stdout.close()

        ip = ''
        string = string.splitlines()
        for i in range(len(string)):
            if 'Kubernetes control plane is running at' in string[i]:
                ip = string[i].replace('Kubernetes control plane is running at ', '')
                break

    except Exception as e:
        raise Exception('kubectl can not run: Error trying to get master ip')

    return ip


def apply_file(path):
    command = str('kubectl apply -f ')
    command += path
    print(command)
    #todo ver si hay que meter esto dentro de un try catch
    resultado = subprocess.Popen(command.split(),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    res_string = str(resultado.stdout.read().decode(sys.getdefaultencoding()))
    err_string = str(resultado.stderr.read().decode(sys.getdefaultencoding()))
    resultado.stdout.close()
    resultado.stderr.close()
    if 'created' not in res_string and 'unchanged' not in res_string and err_string != '':
        raise Exception(err_string)

def rolebinding():
    command = str('kubectl create clusterrolebinding default \
  --clusterrole=edit --serviceaccount=default:default --namespace=default')

    resultado = subprocess.Popen(command.split(),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    res_string = str(resultado.stdout.read().decode(sys.getdefaultencoding()))
    err_string = str(resultado.stderr.read().decode(sys.getdefaultencoding()))
    resultado.stdout.close()
    resultado.stderr.close()
    print(res_string)
    if err_string != '':
        print(err_string)
        raise Exception(err_string)

