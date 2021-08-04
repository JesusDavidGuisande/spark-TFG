import cmd
import os
from minikube.mk import minikube
from spark.spark import spark
from cmd import Cmd
import yaml
from parsers.jsoncontroller import JsonController


def parser_yaml(Path):
    with open(Path) as yaml_data:
        yaml_parsed = yaml.load(yaml_data, Loader=yaml.Loader)
    return yaml_parsed


Debug = True


class SparkyShell(cmd.Cmd):
    Intro = " Type help or ? to list commands.\n"
    prompt = "Sparky >"

    def __init__(self):
        self.cmd = Cmd.__init__(self)

        self.json = JsonController()
        self.sparkHome = self.json.get_object('spark-home')
        self.mk = minikube(True)
        if not self.sparkHome:
            raise Exception('First you need to get the path for spark')

    # commands fro minikube

    def do_mkStart(self, arg):

        """Start the cluster with the configurations provided in a yaml template, if it is not provided,\n
        a default one will be used"""
        if arg == '':
            yaml_template = parser_yaml('./templates/default-mk.yaml')
            mk_template = yaml_template['MiniKube']
        else:
            yaml_template = parser_yaml(arg)
            mk_template = yaml_template['MiniKube']

        self.mk.start(mk_template)

    def do_mkDashboard(self, arg):
        pid = os.fork()
        if pid == 0:
            self.mk.dashboard()
            exit(0)
        else:
            self.json.add_object('pid-dashboard', 'pid', pid)

    def do_mkApply_status(self, arg):
        status = arg
        print(status)
        try:
            if status == 'stop' or status == 'pause' \
                    or status == 'unpause' or status == 'status':
                self.mk.status(status)
            elif status == 'restart':
                self.mk.start(restart=True)
            else:
                print('Not status allowed')
        except Exception as e:
            print(e)

    def do_mkDelete(self, arg):
        """Stops and deletes the cluster that are running"""
        try:
            self.mk.delete()
        except Exception as e:
            print(e)

    def do_e(self, arg):
        self.do_exit(arg)

    def do_exit(self, arg):
        """Exits the program"""
        exit(0)

#todo Probar el delete
#todo Probar las salidas de los estados
#todo verificar salida de un objeto json vacio
#todo checkear en start que se introduce un path valido ¿?

if __name__ == '__main__':
    SparkyShell().cmdloop()
"""
    if Debug:
        print(args)
    
    var = vars(args)
    
    
    
    if var.get('sparkHome'):
        j.add_object('spark-home', 'path', var.get('sparkHome'))
        exit(0)
    
    if sparkHome:
        print(sparkHome)
        print(var)
        if var.get('test'):
            None
    
    
        if var.get('File'):
    
            if var.get('fs'):
    
                spark_template = parser_yaml(var.get('File'))['Spark']
    
            else:
                full_template = var.get('File')
                mk_template = full_template['MiniKube']
                spark_template = full_template['Spark']
    
            mk.start(mk_template)
            time.sleep(20)
            sp = spark(spark_template)
            sp.submit()
    
    
        if var.get('cluster'):
            status = var.get('cluster')
            print(status)
    
            if status == 'stop' or status == 'pause' \
                    or status == 'unpause':
                mk.status(status)
    
            elif status == 'restart':
                mk.start(restart=True)
    
            elif status == 'delete':
                print('Deleting...')
                mk.delete()
    
    
    else:
        print('First you need to get the path for spark') 
"""
