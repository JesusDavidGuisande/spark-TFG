import subprocess
import sys
import re
import time

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
    resultado = subprocess.Popen(command.split(), stderr=subprocess.PIPE)

    err_string = str(resultado.stderr.read().decode(sys.getdefaultencoding()))
    resultado.stderr.close()
    if err_string != '':
        raise Exception(err_string)


def rolebinding():
    command = str(
        'kubectl create clusterrolebinding default --clusterrole=edit --serviceaccount=default:default --namespace=default')
    print(command)
    resultado = subprocess.Popen(command.split(), stderr=subprocess.PIPE)

    err_string = str(resultado.stderr.read().decode(sys.getdefaultencoding()))
    resultado.stderr.close()

    if err_string != '':
        print(err_string)
        raise Exception(err_string)

def delete_volumes(name, profile):
    command = 'kubectl delete persistentvolume ' + name + ' -p ' + profile
    try:
        subprocess.call(command)
    except Exception as e:
        print('Error trying to delete persistent volume: ' + name + '    ' + str(e))

def __current_timestamp():
    secondsSinceEpoch = time.time()
    timeObj = time.localtime(secondsSinceEpoch)
    return str('%d-%d-%d %d:%d:%d' % (
        timeObj.tm_mday, timeObj.tm_mon, timeObj.tm_year, timeObj.tm_hour, timeObj.tm_min, timeObj.tm_sec))

def get_log():
    command = str('kubectl logs sparky-driver')
    try:
        resultado = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        std = resultado.stdout.read().decode(sys.getdefaultencoding())

        file = open('./output/test-' + __current_timestamp() + '.txt', 'w')
        file.write(std)
        file.close()

    except Exception as e:
        print(e)
