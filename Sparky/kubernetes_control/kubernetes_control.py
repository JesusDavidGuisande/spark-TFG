from datetime import datetime
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

def delete_volumes(name):
    command = 'kubectl delete persistentvolume ' + name
    try:
        subprocess.call(command.split())
    except Exception as e:
        print('Error trying to delete persistent volume: ' + name + '    ' + str(e))

def __current_timestamp():
    secondsSinceEpoch = time.time()
    timeObj = time.localtime(secondsSinceEpoch)
    return str('%d-%d-%d %d:%d:%d' % (
        timeObj.tm_mday, timeObj.tm_mon, timeObj.tm_year, timeObj.tm_hour, timeObj.tm_min, timeObj.tm_sec))

def check_volume(nameVol):
    command = "kubectl get pv " + nameVol
    before = datetime.now()
    timestampBefore = datetime.timestamp(before)
    try:
        while True:
            resultado = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            std = resultado.stdout.read().decode(sys.getdefaultencoding())
            print(std)
            if std.find('Available') != -1:
                break
            else:
                after = datetime.now()
                timestampAfter = datetime.timestamp(after)
                if timestampAfter - timestampBefore >= 20:
                    raise Exception('The persistentVolume '+ nameVol + ' is not available after 20 secs, please try again')

    except Exception as e:
        print(e)

def get_log(index):
    command = str('kubectl logs sparky-driver'+ str(index))
    try:
        resultado = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        std = resultado.stdout.read().decode(sys.getdefaultencoding())

        file = open('./output/sparky-driver'+ str(index) + '--' + __current_timestamp() + '.txt', 'w')
        file.write(std)
        file.close()

    except Exception as e:
        print(e)
