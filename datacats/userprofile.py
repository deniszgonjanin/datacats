# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import expanduser, exists, isdir
from os import makedirs
from ConfigParser import SafeConfigParser
from socket import gethostname
from getpass import getuser

from datacats.docker import web_command, WebCommandError

DATACATS_USER_HOST = 'ssh@command.datacats.com'

class UserProfile(object):
    """
    DataCats user profile settings object
    """
    def __init__(self):
        self.profiledir = expanduser('~/.datacats/user-profile')
        config = self.profiledir + '/config'
        if isdir(self.profiledir) and exists(config):
            cp = SafeConfigParser()
            cp.read([config])
            self.ssh_private_key = cp.get('ssh', 'private_key')
            self.ssh_public_key = cp.get('ssh', 'public_key')
        else:
            self.ssh_private_key = None
            self.ssh_public_key = None

    def save(self):
        """
        Save profile settings into user profile directory
        """
        config = self.profiledir + '/config'
        if not isdir(self.profiledir):
            makedirs(self.profiledir)

        cp = SafeConfigParser()

        cp.add_section('ssh')
        cp.set('ssh', 'private_key', self.ssh_private_key)
        cp.set('ssh', 'public_key', self.ssh_public_key)

        with open(config, 'w') as cfile:
            cp.write(cfile)

    def generate_ssh_key(self):
        """
        Generate a new ssh private and public key
        """
        web_command(
            command=["ssh-keygen", "-q", "-t", "rsa", "-N", "", "-C",
                "datacats generated {0}@{1}".format(getuser(), gethostname()),
                "-f", "/output/id_rsa"],
            rw={self.profiledir: '/output'},
            )

    def test_ssh_key(self):
        """
        Return True if this key is accepted by DataCats.com
        """
        try:
            web_command(
                command=["ssh", "-i", "/input/id_rsa", DATACATS_USER_HOST,
                    'test'],
                ro={self.profiledir: '/input'},
                clean_up=True
                )
            return True
        except WebCommandError:
            return False
