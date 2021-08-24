import json
from multiprocessing import Lock

class JsonController:
    def __init__(self, lock):
        self.__path_to_json = './data/data.json'
        self.lock = lock
        self.__data = None

    def __reader(self):
        self.lock.acquire()
        try:
            with open(self.__path_to_json) as file:
                self.__data = json.load(file)
        except Exception as e:
            self.lock.release()
            print('Json reader error:' + str(e))
        self.lock.release()

    def __writer(self):
        self.lock.acquire()
        try:
            with open(self.__path_to_json, 'w') as file:
                json.dump(self.__data, file, indent=4)
        except Exception as e:
            self.lock.release()
            print('Json writer error:' + str(e))
        self.lock.release()

    def delete_list_object(self, object, property, value):
        self.__reader()
        for i in range(len(self.__data[object])):
            if self.__data[object][i][property] == value:
                self.__data[object].pop(i)
                self.__writer()
                break

    def add_list_object(self, object, property, value):
        dict = {}
        for obj in zip(property, value):
            dict[obj[0]] = obj[1]
        self.__reader()
        self.__data[object].append(
            dict
        )
        self.__writer()

    def add_object(self, object, property, value):
        self.__reader()
        self.__data[object][property] = value
        self.__writer()

    def delete_object(self, object, property):
        self.__reader()
        self.__data[object].pop(property)
        self.__writer()

    def get_object(self, object):
        self.__reader()
        return self.__data[object]
