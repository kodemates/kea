import unittest
import os
import json

class Machine(object):

    def __init__(self, name, **kwargs):
        self.data = kwargs
        self.name = name

    def getSshCheck(self):
        """
            TODO : ssh
        :return:
        """

    def getDockerCheck(self):
        """
            TODO : docker -v
        :return:
        """
        pass

    def getSudoCheck(self):
        """
            TODO : sudo -l
        :return:
        """
        pass

    def doRunCommand(self, cmd):
        pass

    def



class App(object):
    def __init__(self, name):
        self.name = name

    @staticmethod
    def isInstalled(self, Machine):
        """ Check if the app is installed on the Machine, return a App Object
        """
        raise NotImplementedError("Should have implemented this")


class Config(object):
    def init(self, path=".", domain="kea-domain.com"):
        """
                creates a config (json) file to store the app and machines info.

        :return: Config
        """

        self.file = path + "/kea.json";
        if os.path.isfile(self.file):
            raise Exception(self.file + " already exists.")

        self.data = {}
        self.data['domain'] = domain

        self.save_config();

        return self

    def load_config(self, path="."):
        file = path + "/kea.json";
        fd = open(file, "r")
        self.data = json.loads(fd.read());
        fd.close()
        self.file = file
        return self;

    def save_config(self):

        fd = open(self.file, "w")
        json.dump(self.data, fd)
        fd.close()

    def add_machine(self, name, **kwargs):
        try:
            self.data['machines'][name] = kwargs;
        except KeyError:
            self.data['machines'] = {name: kwargs}
        return self

    def list_machines(self):
        try:
            return self.data['machines'];
        except KeyError:
            self.data['machines'] = {}
            return self.data['machines']

    def remove_machine(self, name):
        try:
            rtr = self.data['machines'][name];
            return rtr;
        except KeyError:
            return None


    @staticmethod
    def list_avalaible_apps(cls):
        """ TODO : List all registred Apps.
        :return:
        """
        return ["MediaWiki"]

    def list_apps(self):
        try:
            return self.data['apps'];
        except KeyError:
            self.data['apps'] = {}
            return self.data['apps']


    def add_app(self, App, **kwargs):
        try:
            self.data['apps'][App.name] = kwargs;
        except KeyError:
            self.data['apps'] = {App.name: kwargs}
        return self

    def remove_app(self, App):
        try:
            rtr = self.data['apps'][App.name];
            return rtr;
        except KeyError:
            return None


class NginxProxy(App):
    @staticmethod
    def isInstalled(Machine):
        pass


class MediaWiki(App):
    @staticmethod
    def isInstalled(Machine):
        pass


if __name__ == '__main__':

    class MockApp(App):
        pass

    class Config_Test(unittest.TestCase):
        def setUp(self):
            try:
                os.remove("test/result/kea.json")
            except:
                pass

        def test_init(self):
            config = Config();
            config.init("./test/result", "my-domain.com")
            # must exists a file named test/result/kea.json, and must be json valid
            filename = "test/result/kea.json"
            self.assertTrue(os.path.isfile(filename))
            file_data = open(filename, "r")
            try:
                data = json.load(file_data)
            except ValueError:
                self.assertTrue(False, "No JSON Object")
            file_data.close()
            self.assertRaises(Exception, config.init, domain="my-domain.com", path="./test/result")

            config = Config();
            self.assertRaises(IOError, config.load_config, path="./test/result-no-exist");
            config.load_config("./test/result");

            self.assertEqual(config.list_machines(), {});
            config.add_machine('localhost', cmd='/bin/bash')

            self.assertEqual(config.list_machines(), {'localhost': {'cmd': '/bin/bash'}});
            self.assertEqual(config.remove_machine('localhost'), {'cmd': '/bin/bash'});
            self.assertEqual(config.remove_machine('non-localhost'), None);

            config.add_app(MockApp("mock-app"), cmd="docker run mediawiki");
            self.assertEqual(config.list_apps(), {'mock-app': {'cmd': 'docker run mediawiki'}});
            self.assertEqual(config.remove_app(MockApp('mock-app')), {'cmd': 'docker run mediawiki'});

            os.remove("test/result/kea.json")

if __name__ == '__main__':
    unittest.main()

