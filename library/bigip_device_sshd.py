#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 F5 Networks Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {
    'status': ['preview'],
    'supported_by': 'community',
    'metadata_version': '1.0'
}

DOCUMENTATION = '''
---
module: bigip_device_sshd
short_description: Manage the SSHD settings of a BIG-IP.
description:
  - Manage the SSHD settings of a BIG-IP.
version_added: "2.2"
options:
  allow:
    description:
      - Specifies, if you have enabled SSH access, the IP address or address
        range for other systems that can use SSH to communicate with this
        system.
    choices:
      - all
      - IP address, such as 172.27.1.10
      - IP range, such as 172.27.*.* or 172.27.0.0/255.255.0.0
  banner:
    description:
      - Whether to enable the banner or not.
    required: False
    choices:
      - enabled
      - disabled
    default: None
  banner_text:
    description:
      - Specifies the text to include on the pre-login banner that displays
        when a user attempts to login to the system using SSH.
    required: False
    default: None
  inactivity_timeout:
    description:
      - Specifies the number of seconds before inactivity causes an SSH
        session to log out.
    required: False
    default: None
  log_level:
    description:
      - Specifies the minimum SSHD message level to include in the system log.
    choices:
      - debug
      - debug1
      - debug2
      - debug3
      - error
      - fatal
      - info
      - quiet
      - verbose
    required: False
    default: None
  login:
    description:
      - Specifies, when checked C(enabled), that the system accepts SSH
        communications.
    choices:
      - enabled
      - disabled
    required: False
    default: None
  port:
    description:
      - Port that you want the SSH daemon to run on.
    required: False
    default: None
notes:
  - Requires the f5-sdk Python package on the host This is as easy as pip
    install f5-sdk.
  - Requires BIG-IP version 12.0.0 or greater
extends_documentation_fragment: f5
requirements:
  - f5-sdk
author:
  - Tim Rupp (@caphrim007)
'''

EXAMPLES = '''
- name: Set the banner for the SSHD service from a string
  bigip_device_sshd:
      banner: "enabled"
      banner_text: "banner text goes here"
      password: "secret"
      server: "lb.mydomain.com"
      user: "admin"
  delegate_to: localhost

- name: Set the banner for the SSHD service from a file
  bigip_device_sshd:
      banner: "enabled"
      banner_text: "{{ lookup('file', '/path/to/file') }}"
      password: "secret"
      server: "lb.mydomain.com"
      user: "admin"
  delegate_to: localhost

- name: Set the SSHD service to run on port 2222
  bigip_device_sshd:
      password: "secret"
      port: 2222
      server: "lb.mydomain.com"
      user: "admin"
  delegate_to: localhost
'''

RETURN = '''
allow:
    description: >
        Specifies, if you have enabled SSH access, the IP address or address
        range for other systems that can use SSH to communicate with this
        system.
    returned: changed
    type: string
    sample: "192.0.2.*"
banner:
    description: Whether the banner is enabled or not.
    returned: changed
    type: string
    sample: "true"
banner_text:
    description: >
        Specifies the text included on the pre-login banner that
        displays when a user attempts to login to the system using SSH.
    returned: changed and success
    type: string
    sample: "This is a corporate device. Connecting to it without..."
inactivity_timeout:
    description: >
        The number of seconds before inactivity causes an SSH.
        session to log out
    returned: changed
    type: int
    sample: "10"
log_level:
    description: The minimum SSHD message level to include in the system log.
    returned: changed
    type: string
    sample: "debug"
login:
    description: Specifies that the system accepts SSH communications or not.
    return: changed
    type: bool
    sample: true
port:
    description: Port that you want the SSH daemon to run on.
    return: changed
    type: int
    sample: 22
'''


from ansible.module_utils.f5_utils import (
    AnsibleF5Client,
    AnsibleF5Parameters,
    HAS_F5SDK,
    F5ModuleError,
    iControlUnexpectedHTTPError
)


class Parameters(AnsibleF5Parameters):
    api_map = {
        'bannerText': 'banner_text',
        'inactivityTimeout': 'inactivity_timeout',
        'logLevel': 'log_level'
    }

    api_attributes = [
        'allow', 'banner', 'bannerText', 'inactivityTimeout', 'logLevel',
        'login', 'port'
    ]

    updatables = [
        'allow', 'banner', 'banner_text', 'inactivity_timeout', 'log_level',
        'login', 'port'
    ]

    returnables = [
        'allow', 'banner', 'banner_text', 'inactivity_timeout', 'log_level',
        'login', 'port'
    ]

    def to_return(self):
        result = {}
        for returnable in self.returnables:
            result[returnable] = getattr(self, returnable)
        result = self._filter_params(result)
        return result

    def api_params(self):
        result = {}
        for api_attribute in self.api_attributes:
            if self.api_map is not None and api_attribute in self.api_map:
                result[api_attribute] = getattr(self, self.api_map[api_attribute])
            else:
                result[api_attribute] = getattr(self, api_attribute)
        result = self._filter_params(result)
        return result

    @property
    def inactivity_timeout(self):
        if self._values['inactivity_timeout'] is None:
            return None
        return int(self._values['inactivity_timeout'])

    @property
    def port(self):
        if self._values['port'] is None:
            return None
        return int(self._values['port'])

    @property
    def allow(self):
        if self._values['allow'] is None:
            return None
        allow = self._values['allow']
        return list(set([str(x) for x in allow]))


class ModuleManager(object):
    def __init__(self, client):
        self.client = client
        self.have = None
        self.want = Parameters(self.client.module.params)
        self.changes = Parameters()

    def _update_changed_options(self):
        changed = {}
        for key in Parameters.updatables:
            if getattr(self.want, key) is not None:
                attr1 = getattr(self.want, key)
                attr2 = getattr(self.have, key)
                if attr1 != attr2:
                    changed[key] = attr1
        if changed:
            self.changes = Parameters(changed)
            return True
        return False

    def exec_module(self):
        result = dict()

        try:
            changed = self.update()
        except iControlUnexpectedHTTPError as e:
            raise F5ModuleError(str(e))

        changes = self.changes.to_return()
        result.update(**changes)
        result.update(dict(changed=changed))
        return result

    def read_current_from_device(self):
        resource = self.client.api.tm.sys.sshd.load()
        result = resource.attrs
        return Parameters(result)

    def update(self):
        self.have = self.read_current_from_device()
        if not self.should_update():
            return False
        if self.client.check_mode:
            return True
        self.update_on_device()
        return True

    def should_update(self):
        result = self._update_changed_options()
        if result:
            return True
        return False

    def update_on_device(self):
        params = self.want.api_params()
        resource = self.client.api.tm.sys.sshd.load()
        resource.update(**params)


class ArgumentSpec(object):
    def __init__(self):
        self.choices = ['enabled', 'disabled']
        self.levels = [
            'debug', 'debug1', 'debug2', 'debug3', 'error', 'fatal', 'info',
            'quiet', 'verbose'
        ]
        self.supports_check_mode = True
        self.argument_spec = dict(
            allow=dict(
                required=False,
                default=None,
                type='list'
            ),
            banner=dict(
                required=False,
                default=None,
                choices=self.choices
            ),
            banner_text=dict(
                required=False,
                default=None
            ),
            inactivity_timeout=dict(
                required=False,
                default=None,
                type='int'
            ),
            log_level=dict(
                required=False,
                default=None,
                choices=self.levels
            ),
            login=dict(
                required=False,
                default=None,
                choices=self.choices
            ),
            port=dict(
                required=False,
                default=None,
                type='int'
            ),
            state=dict(
                default='present',
                choices=['present']
            )
        )
        self.f5_product_name = 'bigip'


def main():
    if not HAS_F5SDK:
        raise F5ModuleError("The python f5-sdk module is required")

    spec = ArgumentSpec()

    client = AnsibleF5Client(
        argument_spec=spec.argument_spec,
        supports_check_mode=spec.supports_check_mode,
        f5_product_name=spec.f5_product_name
    )

    try:
        mm = ModuleManager(client)
        results = mm.exec_module()
        client.module.exit_json(**results)
    except F5ModuleError as e:
        client.module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
