import json


class JsonController:
    def __init__(self):
        self.__path_to_json = './data/data.json'
        self.__data = None

    def __reader(self):
        with open(self.__path_to_json) as file:
            self.__data = json.load(file)

    def __writer(self):
        with open(self.__path_to_json, 'w') as file:
            json.dump(self.__data, file, indent=4)

    def delete_list_object(self, object, property, value):
        self.__reader()
        for i in range(len(self.__data[object])):
            if self.__data[object][i][property] == value:
                self.__data[property].pop(i)
                self.__writer()
                break

            else:
                print('No encontrado')
        print(self.__data)

    def add_list_object(self, object, property, value):
        self.__reader()
        self.__data[object].append({
            property: value
        })
        self.__writer()

        """"
                por si en un futuro hay que añadir mas de una propiedad al json (no va bien)
                for p, v in properties, values:
                    self.__data[object].append({
                        p: v
                    })
                """

    def add_object(self, object, property, value):
        self.__reader()
        self.__data[object][property] = value
        self.__writer()

    def delete_object(self, object, property):
        self.__reader()
        self.__data[object].pop(property)
        self.__writer()

    def get_object(self,object):
        self.__reader()
        return self.__data[object]

