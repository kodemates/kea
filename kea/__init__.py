import os
import json
from subprocess import Popen, PIPE
import re

ssh_cmd = "/usr/bin/ssh"
docker_cmd  = "/usr/bin/docker"
sudo_cmd = "/usr/bin/sudo"

class Machine(object):

    def __init__(self, name, **kwargs):
        self.data = kwargs
        self.name = name

    def getSsh(self):
        return ssh_cmd + " "  + self.name

    def getSudo(self):
        return ssh_cmd + " "  + self.name + " " + sudo_cmd

    def getDocker(self):
        return ssh_cmd + " "  + self.name + " " + sudo_cmd + " " + docker_cmd

    def getSshCheck(self):
        return [ssh_cmd + " "  + self.name + " /bin/echo \"ssh-ok\""]

    def getDockerCheck(self):
        return [ssh_cmd + " "  + self.name + " " + sudo_cmd + " " + docker_cmd + " -v"]

    def getSudoCheck(self):
        return [ssh_cmd + " "  + self.name + " " + sudo_cmd + " -v"]

    def doRunCmd(self, cmd):
        """
            TODO: Remove this method from the Machine, shuld be on the app or a coordinator/cli.
        :param cmd:
        :return:
        """
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        proc.wait()
        return proc.returncode;

class App(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.data = kwargs

    def install(self, Machie):
        """ Check if the app is installed on the Machine, return a App Object
        """
        raise NotImplementedError("Should have implemented this")

    @staticmethod
    def check(Machine):
        """ Check if the app is installed on the Machine, return a App Object
        """
        raise NotImplementedError("Should have implemented this")

    def uninstall(self, Machine):
        """
            Uninstall the app from the Machine
        :param Machine:
        :return:
        """
        raise NotImplementedError("Should have implemented this")

class Config(object):
    def init(self, path=".", domain="kea-domain.com"):
        """
                creates a config (json) file to store the app and machines info.

        :return: Config
        """

        self.file = path + "/kea.json"

        if os.path.isfile(self.file):
            raise Exception(self.file + " already exists.")

        self.data = {}
        self.data['domain'] = domain

        self.save_config()

        return self

    def load_config(self, path="."):
        file = path + "/kea.json"
        fd = open(file, "r")
        self.data = json.loads(fd.read())
        fd.close()
        self.file = file
        return self

    def save_config(self):

        fd = open(self.file, "w")
        json.dump(self.data, fd)
        fd.close()

    def add_machine(self, name, **kwargs):
        try:
            self.data['machines'][name] = kwargs
        except KeyError:
            self.data['machines'] = {name: kwargs}
        return self

    def list_machines(self):
        try:
            return self.data['machines']
        except KeyError:
            self.data['machines'] = {}
            return self.data['machines']

    def remove_machine(self, name):
        try:
            rtr = self.data['machines'][name]
            del self.data['machines'][name]
            return rtr
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
            return self.data['apps']
        except KeyError:
            self.data['apps'] = {}
            return self.data['apps']


    def add_app(self, app, **kwargs):
        try:
            self.data['apps'][app.name] = kwargs;
        except KeyError:
            self.data['apps'] = {app.name: kwargs}
        return self

    def remove_app(self, app):
        try:
            rtr = self.data['apps'][app.name]
            del self.data['apps'][app.name]
            return rtr;
        except KeyError:
            return None


class NginxProxy(App):
    def install(self, m):
        docker_install = m.getDocker() + " run -d -p 80:80 -v /var/run/docker.sock:/tmp/docker.sock zedtux/nginx-proxy"
        proc = Popen(docker_install, stdout=PIPE, stderr=PIPE, shell=True)
        (stdout, stderr) = proc.communicate()
        container = stdout
        docker_ps = m.getDocker() + " inspect " + container.decode("utf-8")
        proc = Popen(docker_ps, stdout=PIPE, stderr=PIPE, shell=True)
        (stdout, stderr) = proc.communicate()
        data = json.loads(stdout.decode("utf-8"))
        self.data = data[0];
        return proc.returncode == 0;

    @staticmethod
    def check(m):
        """ Check if the app is installed on the Machine, return a App Object
        """
        docker_ps = m.getDocker() + " ps -q"
        proc = Popen(docker_ps, stdout=PIPE, stderr=PIPE, shell=True)
        (stdout, stderr) = proc.communicate()
        proc.wait()
        rtr = []
        for container in stdout.splitlines():
            docker_ps = m.getDocker() + " inspect " + container.decode("utf-8")
            proc = Popen(docker_ps, stdout=PIPE, stderr=PIPE, shell=True)
            (stdout, stderr) = proc.communicate()
            data = json.loads(stdout.decode("utf-8"))
            try:
                if data[0]["NetworkSettings"]['Ports']['80/tcp'][0]['HostPort'] == '80' and \
                    data[0]['Config']['Image'] == 'zedtux/nginx-proxy':
                    rtr.append(NginxProxy("NginxProxy", **(data[0])))
            except TypeError :
                continue
        return rtr;

    def uninstall(self, m):
        """
            Uninstall the app from the Machine, based on uuid name.
        :param Machine:
        :return:
        """
        docker_install = m.getDocker() + " stop " + self.data['Id']
        proc = Popen(docker_install, stdout=PIPE, stderr=PIPE, shell=True)
        proc.wait()
        return proc.returncode == 0;

class MediaWiki(App):
    def install(self, m):
        docker_install = m.getDocker() + \
                        " run  -P -d -e VIRTUAL_HOST=" + self.name + "."+ self.data['domain'] + \
                         " -v /data/wiki:/data -h "+self.name + "."+ self.data['domain'] + \
                         " nickstenning/mediawiki"

        proc = Popen(docker_install, stdout=PIPE, stderr=PIPE, shell=True)
        (stdout, stderr) = proc.communicate()
        container = stdout
        docker_ps = m.getDocker() + " inspect " + container.decode("utf-8")
        proc = Popen(docker_ps, stdout=PIPE, stderr=PIPE, shell=True)
        (stdout, stderr) = proc.communicate()
        data = json.loads(stdout.decode("utf-8"))
        self.data = data[0];
        return proc.returncode == 0;

    @staticmethod
    def check(m, **kwargs):
        docker_ps = m.getDocker() + " ps -q"
        proc = Popen(docker_ps, stdout=PIPE, stderr=PIPE, shell=True)
        (stdout, stderr) = proc.communicate()
        proc.wait()
        rtr = []
        for container in stdout.splitlines():
            docker_ps = m.getDocker() + " inspect " + container.decode("utf-8")
            proc = Popen(docker_ps, stdout=PIPE, stderr=PIPE, shell=True)
            (stdout, stderr) = proc.communicate()
            data = json.loads(stdout.decode("utf-8"))
            try:
                for env in data[0]['Config']['Env']:
                    if env.startswith("VIRTUAL_HOST="):
                        m_domain = env[13:env.find("." + kwargs['domain'])]
                        rtr.append(MediaWiki(m_domain, **(data[0])))
            except TypeError :
                continue
        return rtr;

    def uninstall(self, m):
        """
            Uninstall the app from the Machine, based on uuid name.
        :param Machine:
        :return:
        """
        docker_install = m.getDocker() + " stop " + self.data['Id']
        proc = Popen(docker_install, stdout=PIPE, stderr=PIPE, shell=True)
        proc.wait()
        return proc.returncode == 0;



class MariaDB(App):
    def install(self, m):
        docker_install = m.getDocker() + " run  -P -d -h "+self.name + "."+ self.data['domain'] + \
                         " dockerfile/mariadb"
        proc = Popen(docker_install, stdout=PIPE, stderr=PIPE, shell=True)
        (stdout, stderr) = proc.communicate()
        container = stdout
        docker_ps = m.getDocker() + " inspect " + container.decode("utf-8")
        proc = Popen(docker_ps, stdout=PIPE, stderr=PIPE, shell=True)
        (stdout, stderr) = proc.communicate()
        data = json.loads(stdout.decode("utf-8"))
        self.data = data[0];
        return proc.returncode == 0;

    @staticmethod
    def check(m, **kwargs):
        docker_ps = m.getDocker() + " ps -q"
        proc = Popen(docker_ps, stdout=PIPE, stderr=PIPE, shell=True)
        (stdout, stderr) = proc.communicate()
        proc.wait()
        rtr = []
        for container in stdout.splitlines():
            docker_ps = m.getDocker() + " inspect " + container.decode("utf-8")
            proc = Popen(docker_ps, stdout=PIPE, stderr=PIPE, shell=True)
            (stdout, stderr) = proc.communicate()
            data = json.loads(stdout.decode("utf-8"))
            try:
                print (data[0]['Config']['Hostname'])
                print (data[0]['Config']['Image'])

                if data[0]['Config']['Image'] == 'dockerfile/mariadb' :
                    m_domain = data[0]['Config']['Hostname'][0:data[0]['Config']['Hostname'].find("." + kwargs['domain'])]
                    rtr.append(MediaWiki(m_domain, **(data[0])))
            except TypeError :
                continue
        return rtr;

    def uninstall(self, m):
        """
            Uninstall the app from the Machine, based on uuid name.
        :param Machine:
        :return:
        """
        docker_install = m.getDocker() + " stop " + self.data['Id']
        proc = Popen(docker_install, stdout=PIPE, stderr=PIPE, shell=True)
        proc.wait()
        return proc.returncode == 0;
