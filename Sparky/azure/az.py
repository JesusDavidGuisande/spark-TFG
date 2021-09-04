import yaml

from kubernetes_control.kubernetes_control import *
import subprocess
import sys


class Azure:

    def __init__(self, trace, json):
        self.verbose = trace
        self.json = json
        self.resG = ''
        self.storage = ''

    def start(self, subs, resG, name):
        """Funcion que enlaza kubernetes con el cloud de azure para poder aplicar configuraciones"""
        self.resG = resG
        cmd_account_set = str('az account set --subscription ' + subs)
        cmd_aks_credentials = str('az aks get-credentials --resource-group ' + resG + ' --name ' + name + ' --overwrite-existing')

        try:
            if self.verbose:

                # run command with trace
                process_account = subprocess.Popen(cmd_account_set.split(), stderr=subprocess.PIPE)
                err_account = process_account.stderr.read().decode(sys.getdefaultencoding())
                if not err_account:
                    print(err_account)
                process_account.stderr.close()

                process_credentials = subprocess.Popen(cmd_aks_credentials.split(), stderr=subprocess.PIPE)
                err_credentials = process_credentials.stderr.read().decode(sys.getdefaultencoding())
                if not err_credentials:
                    print(err_credentials)
                process_credentials.stderr.close()
            # if verbose is not asked for
            else:

                # run command without trace
                subprocess.call(cmd_account_set.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                subprocess.call(cmd_aks_credentials.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            ServiceConfig()
        except Exception as e:
            print('Error set up: ' + str(e))

    def __getStrConn(self, storagename):
        cmd_str_conn = str('az storage account show-connection-string --resource-group ' + self.resG +
                           ' --name ' + storagename + ' -o tsv')

        try:
            print('Getting connection string...')
            # command create account on azure storage
            cmd_out = subprocess.Popen(cmd_str_conn.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            err = cmd_out.stderr.read().decode(sys.getdefaultencoding())
            str_conn = cmd_out.stdout.read().decode(sys.getdefaultencoding())
            cmd_out.stderr.close()
            cmd_out.stdout.close()
            print(str_conn)
            self.str_conn = str_conn
            if err != '':
                print('Error connection string:   ' + err)
                return

        except Exception as e:
            print('Error set up: ' + str(e))

    def storage_config(self, arg):
        if arg[0] == 'create':
            self.resG = self.json.get_object('resource-group')['resg']
            storagename = arg[1]
            containername = arg[2]
            sku = 'Standard_LRS'
            self.__getStrConn(storagename)
            cmd_acc_c = str('az storage account create --resource-group ' + self.resG + ' --name ' + storagename +
                            ' --sku ' + sku)
            # command create account on azure storage
            try:
                if self.verbose:
                    # command create account on azure storage
                    cmd_out = subprocess.Popen(cmd_acc_c.split(), stderr=subprocess.PIPE)
                    err = cmd_out.stderr.read().decode(sys.getdefaultencoding())
                    cmd_out.stderr.close()
                    if err != '':
                        print('Error create account:   ' + err)
                        return

                else:

                    # run command without trace
                    subprocess.call(cmd_acc_c.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except Exception as e:
                print('Error set up: ' + str(e))



            cmd_cont_cre = str('az storage container create --name ' + containername + ' --connection-string '
                               + self.str_conn)
            cmd_per_cont = str('az storage container set-permission --name ' + containername + ' --public-access blob'
                               + ' --connection-string ' + self.str_conn)

            try:
                if self.verbose:
                    # command create container
                    print('Creating a container...')
                    cmd_out = subprocess.Popen(cmd_cont_cre.split(), stderr=subprocess.PIPE)
                    err = cmd_out.stderr.read().decode(sys.getdefaultencoding())
                    cmd_out.stderr.close()
                    if err != '':
                        print('Error container create:   ' + err)
                        return

                    # command create container
                    print('Setting container permisions...')
                    cmd_out = subprocess.Popen(cmd_per_cont.split(), stderr=subprocess.PIPE)
                    err = cmd_out.stderr.read().decode(sys.getdefaultencoding())
                    cmd_out.stderr.close()
                    if err != '':
                        print('Error container set permission:   ' + err)
                        return
                    print('Done!')
                else:

                    # run command without trace
                    subprocess.call(cmd_cont_cre.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    subprocess.call(cmd_per_cont.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except Exception as e:
                print('Error set up: ' + str(e))

        elif arg[0] == 'upload':
            container = arg[1]
            file_local = arg[2]
            blob_name = arg[3]

            cmd_upload = str('az storage blob upload --container-name ' + container +
                             ' --file ' + file_local + ' --name ' + blob_name + ' --connection-string '
                               + self.str_conn)

            try:
                if self.verbose:
                    # command upload file
                    cmd_out = subprocess.Popen(cmd_upload.split(), stderr=subprocess.PIPE)
                    err = cmd_out.stderr.read().decode(sys.getdefaultencoding())
                    cmd_out.stderr.close()
                    if not err:
                        print('Error:   ' + err)
                        return

                else:

                    # run command without trace
                    subprocess.call(cmd_upload.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except Exception as e:
                print('Error set up: ' + str(e))

    def getUrlBlob(self, storage, container, blob_name):
        self.__getStrConn(storage)
        cmd_url = str('az storage blob url --container-name ' + container + ' --name ' + blob_name +
                      ' --connection-string ' + self.str_conn)
        print('adios')
        try:
            # command url file
            cmd_out = subprocess.Popen(cmd_url.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            std = cmd_out.stdout.read().decode(sys.getdefaultencoding())
            err = cmd_out.stderr.read().decode(sys.getdefaultencoding())
            cmd_out.stderr.close()
            cmd_out.stdout.close()
            if err != '':
                print(err)
                return

            return std[1:-2]
        except Exception as e:
            print('Error set up url: ' + str(e))


