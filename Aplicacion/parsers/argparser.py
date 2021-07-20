import argparse

class argparser:

    def __init__(self):
        my_parser = argparse.ArgumentParser(add_help=True,
                                            description='Automatization tool for minikube and Spark submit')
        #Input files control
        subparser = my_parser.add_subparsers()
        parser_files = subparser.add_parser('file')
        parser_files.add_argument('File', type=str, help='Template with the Minikube and/or Spark submit config to deploy')


        parser_files.add_argument('-fs', action='store_true', help='Indicates that the template '+
                                                                   'to be applied is only for Spark submit')





        #Minikube control
        parser_cluster = subparser.add_parser('cluster')

        #parser_cluster.add_argument('Cluster', help='Profile that references a cluster')


        parser_cluster.add_argument('cluster', choices=('stop', 'restart', 'delete', 'pause', 'unpause'),
                               help='Change the state of the cluster ', nargs='?')


        #Free control
        my_parser.add_argument('-v', '--Verbose', action='store_true',
                               help='Enbales the std and sterr output')

        self.args = my_parser.parse_args()

    def getArgs(self):
        return self.args