#!/usr/bin/env python
import os
import sys
from subprocess import call
import shutil

try:
    WindowsError
except NameError:
    IS_WIN = False
    PIP = '/bin/pip'
    KDR = '/bin/kdr'
else:
    IS_WIN = True
    PIP = '/Scripts/pip.exe'
    KDR = '/Scripts/kdr.exe'

DEFAULT_KDR_HOME = os.path.expanduser('~/.local/venvs')
DEFAULT_KDR_BIN_DIR = os.path.expanduser('~/.local/bin')
virtualenv_bin = 'virtualenv'

def echo(msg=''):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def fail(msg):
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()
    sys.exit(1)


def succeed(msg):
    echo(msg)
    sys.exit(0)


def command_exists(cmd):
    with open(os.devnull, 'w') as null:
        try:
            return call(
                [cmd, '--version'],
                stdout=null, stderr=null) == 0
        except OSError:
            return False


def publish_script(venv, bin_dir):

    echo('Installing kdr binary to ' + bin_dir)
    if IS_WIN:
        for name in os.listdir(venv + '/Scripts'):
            if 'kdr' in name.lower():
                shutil.copy(venv + '/Scripts/' + name, bin_dir)
    else:
        os.symlink(venv + '/bin/kdr', bin_dir + '/kdr')

def install_files(venv, bin_dir, install):
    try:
        os.makedirs(bin_dir)
    except OSError:
        pass

    def _cleanup():
        try:
            shutil.rmtree(venv)
        except (OSError, IOError):
            pass

    if call([global virtualenv_bin, venv]) != 0:
        _cleanup()
        fail('Could not create virtualenv for kdr :(')

    if call([venv + PIP, 'install', install]) != 0:
        _cleanup()
        fail('Could not install kdr :(')

    publish_script(venv, bin_dir)


def main():
    if command_exists('kdr'):
        succeed('You already have kdr installed')
    else:
        echo('Installing kdr')

    if not command_exists(global virtualenv_bin):
        global virtualenv_bin = "%s/.local/bin/virtualenv" % os.path.expanduser("~")
        if not command_exists(virutalenv_bin):
            fail('You need to have virtualenv installed to bootstrap kdr.')

    bin_dir = os.environ.get('KDR_BIN_DIR', DEFAULT_KDR_BIN_DIR)
    venv = os.path.join(os.environ.get('KDR_HOME', DEFAULT_KDR_HOME),
                        'kdr')
    install_files(venv, bin_dir, 'kdr')

    if not command_exists('kdr') != 0:
        echo()
        echo('=' * 60)
        echo()
        echo('Warning:')
        echo('  It looks like {0} is not on your PATH so kdr will'.format(bin_dir))
        echo('  not work out of the box.  To fix this problem make sure to')
        echo('  add this to your .bashrc / .profile file:')
        echo()
        echo('  export PATH={0}:$PATH'.format(bin_dir))
        echo()
        echo('=' * 60)
        echo()

    succeed('kdr is now installed.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # we are being tested
        install_files(*sys.argv[1:])
    else:
        main()
