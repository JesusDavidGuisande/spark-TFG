#!/usr/bin/python3
import cmd
import os

from minikube.mk import Minikube
from spark.spark import Spark
from cmd import Cmd
import yaml
from parsers.jsoncontroller import JsonController
from multiprocessing import Lock


def parser_yaml(Path):
    with open(Path) as yaml_data:
        yaml_parsed = yaml.load(yaml_data, Loader=yaml.Loader)
    return yaml_parsed


Debug = True


class SparkyShell(cmd.Cmd):
    Intro = "Escribe help o ? para listar los comandos.\n"
    prompt = "Sparky> "

    def __init__(self):
        self.cmd = Cmd.__init__(self)
        self.lock = Lock()
        self.json = JsonController(self.lock)
        self.sparkHome = self.json.get_object('spark-home')
        self.mk = Minikube(True, self.json)
        self.sp = Spark(self.mk, None, self.json)
        if not self.sparkHome:
            raise Exception('First you need to get the path for spark')

    # commands fro Minikube
    def do_setVorbosity(self, arg):
        """Indica si la verbosidad esta activa o no, activa por defecto; {show, True, False}"""
        if arg == 'show':
            print(self.mk.get_log_trace())
        elif arg == 'True' or arg == 'False':
            self.mk.set_log_trace(arg)
        else:
            print('Argument not allowed')

    def do_mkStart(self, arg):

        """Inicia el clúster con las configuraciones proporcionadas en una plantilla yaml, si no se proporciona, \n
        se usará uno predeterminado"""
        if arg == '':
            yaml_template = parser_yaml('./templates/default-mk.yaml')
            mk_template = yaml_template['MiniKube']
        else:
            if os.path.exists(arg):
                yaml_template = parser_yaml(arg)
                mk_template = yaml_template['MiniKube']
            else:
                print('The path is invalid')
        try:
            self.mk.start(mk_template)
        except Exception as e:
            print(e)

    def do_mkApply_state(self, arg):
        """Aplica un estado al cluster {stop, pause, unpause, status, restart}"""
        status = arg
        try:
            if status == 'stop' or status == 'pause' \
                    or status == 'unpause' or status == 'status':
                self.mk.status(status)
            elif status == 'restart':
                self.mk.start(dict=None, restart=True)
            else:
                print('Not status allowed')
        except Exception as e:
            print(e)
    def do_mkRemoveVolume(self, arg):
        # todo
        list = self.mk.get_pv()
        if arg == 'show':
            for pv in list:
                print('Nombre: ' + pv['name'] + '   Process pid:' + pv['process'].pid)
        else:
            print(arg)

    def do_mkDelete(self, arg):
        """Detiene y borra el cluster que se encuentra en ejecución"""
        try:
            self.sp.dump_volumes()
            self.mk.delete()
        except Exception as e:
            print(e)

    def do_spSubmit(self, arg):
        """Envia un trabajo de Spark al cluster """
        print(arg)
        if os.path.exists(arg):
            try:
                yaml_template = parser_yaml(arg)
            except Exception as e:
                print('Template error: ' + str(e))
            try:

                sp_template = yaml_template['Spark']
                self.sp.submit(sp_template)

            except Exception as e:
                print('Submit execution error: ' + str(e))
        else:
            print('Invalid path to spark file')

    def do_clean(self,arg):
        """Limpia la pantalla"""
        print('\n' * 10)


    def do_e(self, arg):
        """Finaliza Sparky"""
        self.do_exit(arg)

    def do_exit(self, arg):
        """Finaliza Sparky """
        exit(0)



if __name__ == '__main__':
    SparkyShell().cmdloop()
