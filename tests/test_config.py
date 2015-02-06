from kea import *
import unittest

class MockApp(App):
    pass

class Config_Test(unittest.TestCase):
    def setUp(self):
        try:
            os.remove("result/kea.json")
        except:
            pass

    def test_init(self):
        config = Config()
        config.init("./result", "my-domain.com")
        # must exists a file named test/result/kea.json, and must be json valid
        filename = "result/kea.json"
        self.assertTrue(os.path.isfile(filename))
        file_data = open(filename, "r")
        try:
            data = json.load(file_data)
        except ValueError:
            self.assertTrue(False, "No JSON Object")
        file_data.close()
        self.assertRaises(Exception, config.init, domain="my-domain.com", path="./test/result")

        config = Config()
        self.assertRaises(IOError, config.load_config, path="./result-no-exist")
        config.load_config("./result")

        self.assertEqual(config.list_machines(), {})
        config.add_machine('localhost', cmd='/bin/bash')

        self.assertEqual(config.list_machines(), {'localhost': {'cmd': '/bin/bash'}})
        self.assertEqual(config.remove_machine('localhost'), {'cmd': '/bin/bash'})
        self.assertEqual(config.remove_machine('non-localhost'), None)

        config.add_app(MockApp("mock-app"), cmd="docker run mediawiki")
        self.assertEqual(config.list_apps(), {'mock-app': {'cmd': 'docker run mediawiki'}})
        self.assertEqual(config.remove_app(MockApp('mock-app')), {'cmd': 'docker run mediawiki'})

        os.remove("result/kea.json")

class  Machine_Test(unittest.TestCase):
    def test_getSshCheck(self):
        """
            for now we relay on a simplified ssh config (usually from 'vagrant ssh-config') to make enable to
             connect a host with 'ssh default'
        :return:
        """
        m = Machine('default')
        self.assertEqual('default', m.name)
        self.assertEqual(m.getSshCheck(), ['/usr/bin/ssh default /bin/echo "ssh-ok"'])
        self.assertEqual(m.getSudoCheck(), ['/usr/bin/ssh default /usr/bin/sudo -v'])
        self.assertEqual(m.getDockerCheck(), ['/usr/bin/ssh default /usr/bin/sudo /usr/bin/docker -v'])

        #self.assertEqual(m.doRunCmd('/bin/echo "ssh-ok"'), 0)
        #self.assertEqual(m.doRunCmd('/bin/cat some-non-existing-file'), 1)
        #self.assertEqual(m.doRunCmd('/bin/non-existing-command'), 127)


class testAppInstall(unittest.TestCase):
    def test_install_proxy(self):
        """
            to run this test you need a ssh config that allows you to connect with the ssh default,
                also the ssh user must be sudo (with out a password) and docket shuld be already installed.
        :return:
        """
        m = Machine('default')
        np = NginxProxy('base-proxy')
        np.install(m)
        print (np.check(m))
        np.uninstall(m)

    def test_install_mediawiki(self):
        m = Machine('default')
        np = NginxProxy('base-proxy')
        mw = MediaWiki('wiki', domain="my-domain.com")
        mw.install(m)