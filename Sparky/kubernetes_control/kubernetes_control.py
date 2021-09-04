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


def ServiceConfig():
    #todo comprobar si existen antes de crearlos
    cmd_account = str('kubectl create serviceaccount spark')
    cmd_rolbinding = str(
        'kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default')

    outtcome_account = subprocess.Popen(cmd_account.split(), stderr=subprocess.PIPE)

    err_account = str(outtcome_account.stderr.read().decode(sys.getdefaultencoding()))
    outtcome_account.stderr.close()


    outtcome_role = subprocess.Popen(cmd_rolbinding.split(), stderr=subprocess.PIPE)

    err_role = str(outtcome_role.stderr.read().decode(sys.getdefaultencoding()))
    outtcome_role.stderr.close()

    if err_role != '':
        print(err_role)
        raise Exception(err_role)

    if err_account != '':
        print(err_account)
        raise Exception(err_account)


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
                    raise Exception(
                        'The persistentVolume ' + nameVol + ' is not available after 20 secs, please try again')

    except Exception as e:
        print(e)


def get_log(name):
    command = str('kubectl logs ' + name)
    try:
        resultado = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        std = resultado.stdout.read().decode(sys.getdefaultencoding())

        file = open('./output/' + name + '--' + __current_timestamp() + '.txt', 'w')
        file.write(std)
        file.close()

    except Exception as e:
        print(e)


def delete_pod(name):
    command = str('kubectl delete pod ' + name)

    try:
        subprocess.call(command.split())

    except Exception as e:
        print('Pod not deleted: ' + e)
