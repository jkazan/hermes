import os
import sys
from terminal import Write, Color
import subprocess
import re
import requests
from distutils.version import LooseVersion
import subprocess

class HInstall(object):
    def install(self, tool, dest, opt=None):
        """Install software tool.

        param tool: Name of tool to install
        param args: Input arguments needed for installation
        """
        sudo = False
        path = os.path.dirname(os.path.abspath(__file__)) # Path to hermes dir
        dest = os.path.expanduser(dest)

        # Check privileges
        priv_dest = dest
        while not os.path.exists(priv_dest):
            priv_dest = os.path.split(priv_dest)[0]
        if not os.access(priv_dest, os.W_OK):
            Write().write('You need sudo privileges to write in {}\n'
                           .format(priv_dest))

            q_sudo = input('Would you like to run as sudo? [Y/n]: ').lower()
            if q_sudo == "y":
                sudo = True
            else:
                return

        # Check if destination directory exists
        if not os.path.exists(dest):
            create = input('Directory does not exist, '
                           +'would you like to create it? [Y/n]: ').lower()
            if create == "y":
                os.makedirs(dest)
            else:
                return

        if tool == 'e3':
            # Check if already installed
            if os.path.exists(dest+'/e3'):
                overwrite = input('E3 found in the destination directory. '
                                   +'Overwrite existing E3? [Y/n]: ').lower()
                if not overwrite == "y":
                    return

            try:
                Write().write('Installing {}\n' .format(tool), 'task')
                ret_code = subprocess.check_call('sudo {}/e3.install {}'
                                                     .format(path, dest),
                                                     shell=True)
            except subprocess.CalledProcessError as e:
                Write().write(e, 'warning')
                return

        elif tool == 'plcfactory':
            # Check if already installed
            existing = False
            if os.path.exists(dest+'/ics_plc_factory'):
                overwrite = input('PLCFactory found in the destination directory. '
                                   +'Update PLCFactory? [Y/n]: ').lower()
                if overwrite == "y":
                    existing = True
                else:
                    return

            repo_url = 'https://bitbucket.org/europeanspallationsource/ics_plc_factory.git'

            if existing:
                cmd = 'git -C ' + dest + '/ics_plc_factory pull ' + repo_url
            else:
                cmd = 'git clone ' + repo_url + ' ' + dest + '/ics_plc_factory'

            if sudo:
                cmd = 'sudo ' + cmd

            try:
                ret_code = subprocess.check_call(cmd, shell=True)
            except Exception as e:
                ret_code = 1

        elif tool == 'beast':
            # Check if already installed
            existing = False
            if os.path.exists(dest+'/beast-config'):
                overwrite = input('BEAST found in the destination directory. '
                                   +'Update BEAST? [Y/n]: ').lower()
                if overwrite == "y":
                    existing = True
                else:
                    return

            repo_url = 'https://gitlab.esss.lu.se/ics-infrastructure/beast-config.git'

            if existing:
                cmd = 'git -C ' + dest + '/beast-config pull ' + repo_url
            else:
                cmd = 'git clone ' + repo_url + ' ' + dest + '/beast-config'

            if sudo:
                cmd = 'sudo ' + cmd

            try:
                ret_code = subprocess.check_call(cmd, shell=True)
            except Exception as e:
                ret_code = 1

        elif tool == 'css':
            if opt is None:
                opt = 'development'
            elif opt != "development" and opt != "production":
                Write().write('\'{}\' is an invalid option\n' .format(opt), 'warning' )
                return

            url = 'https://artifactory.esss.lu.se/artifactory/CS-Studio/'
            url += opt+'/'
            if opt == 'development':
                pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+b[0-9]+")
            elif opt == 'production':
                pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")

            params = {'q': 'ISOW7841FDWER'}
            headers = {'User-Agent': 'Mozilla/5'}
            r = requests.get(url, params=params, headers=headers)

            # Cast to set and back to list to make it unique
            versions = set(pattern.findall(r.text))
            versions = list(versions)


            versions.sort(key=LooseVersion)
            Write().write('{} versions:\n' .format(opt), 'header')
            for v in versions:
                print(v)

            # Check if already installed
            if os.path.exists(dest+'/cs-studio'):
                current_version = ''
                with open(dest+'/cs-studio/ess-version.txt', 'r') as cv:
                    current_version = cv.read().rstrip()

                overwrite = input('CSS version '
                                    + current_version
                                    + ' found in the destination directory. '
                                    + 'Overwrite? [Y/n]: ').lower()

            version = input('Which version would you like to install? ')
            while version not in pattern.findall(r.text):
                Write().write('\'{}\' is not a valid version\n'
                               .format(version), 'warning')
                version = input('Which version would you like to install? ')

            Write().write('Downloading {} version {}\n'
                           .format(opt, version), 'task')

            if sys.platform == 'linux':
                file_name = 'cs-studio-ess-'+version+'-linux.gtk.x86_64.tar.gz'

            url += version+'/'+file_name

            with open(path+'/'+file_name, 'wb') as f:
                response = requests.get(url, stream=True)
                total_length = int(response.headers.get('content-length'))
                dl = 0
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    progress = int(100 * dl / total_length)
                    Write().write('\r{}%' .format(progress), 'task')
                    sys.stdout.flush()

            Write().write("\nInstalling\n", 'task')


            cmd = 'sudo tar xzf ' + path+'/'+file_name + ' -C ' + dest
            cmd += ' && rm -rf ' + path+'/'+file_name


            if sudo:
                cmd = 'sudo ' + cmd

            ret_code = subprocess.check_call(cmd, shell=True)

            Write().write("Done\n", 'task')

            Write().write('Tip: If you want to be able to start CSS from '
                           +'anywhere in your terminal by just\ntyping "css"'
                           +', put the following line in your ~/.bashrc file:\n'
                           +'alias css=\'{}/cs-studio/ESS\ CS-Studio\'\n'
                           .format(dest), 'tip')

        else:
            Write().write('\'{}\' is not available for installation\n'
                           .format(tool), 'warning')
            return

        if ret_code != 0:
            Write().write('\'{}\' installation failed\n' .format(tool), 'warning')
            return
