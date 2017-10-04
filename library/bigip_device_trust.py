#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2017 F5 Networks Inc.
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
module: bigip_device_trust
short_description: Manage the trust relationships between BIG-IPs.
description:
  - Manage the trust relationships between BIG-IPs. Devices, once peered, cannot
    be updated. If updating is needed, the peer must first be removed before it
    can be re-added to the trust.
version_added: "2.5"
options:
  peer_server:
    description:
      - The peer address to connect to and trust for synchronizing configuration.
        This is typically the management address of the remote device, but may
        also be a Self IP.
    required: True
  peer_hostname:
    description:
      - The hostname that you want to associate with the device. This value will
        be used to easily distinguish this device in BIG-IP configuration. If not
        specified, the value of C(peer_server) will be used as a default.
  peer_user:
    description:
      - The API username of the remote peer device that you are trusting. Note
        that the CLI user cannot be used unless it too has an API account. If this
        value is not specified, then the value of C(user), or the environment
        variable C(F5_USER) will be used.
  peer_password:
    description:
      - The password of the API username of the remote peer device that you are
        trusting. If this value is not specified, then the value of C(password),
        or the environment variable C(F5_PASSWORD) will be used.
  type:
    description:
      - Specifies whether the device you are adding is a Peer or a Subordinate.
        The default is C(peer).
      - The difference between the two is a matter of mitigating risk of
        compromise.
      - A subordinate device cannot sign a certificate for another device.
      - In the case where the security of an authority device in a trust domain
        is compromised, the risk of compromise is minimized for any subordinate
        device.
      - Designating devices as subordinate devices is recommended for device
        groups with a large number of member devices, where the risk of compromise
        is high.
    choices:
      - peer
      - subordinate
    default: peer
notes:
    - Requires the f5-sdk Python package on the host. This is as easy as
      pip install f5-sdk.
requirements:
  - f5-sdk
extends_documentation_fragment: f5
author:
  - Tim Rupp (@caphrim007)
'''

EXAMPLES = '''
- name: Add trusts for all peer devices to Active device
  bigip_device_trust:
      server: "lb.mydomain.com"
      user: "admin"
      password: "secret"
      peer_server: "{{ item.ansible_host }}"
      peer_hostname: "{{ item.inventory_hostname }}"
      peer_user: "{{ item.bigip_username }}"
      peer_password: "{{ item.bigip_password }}"
  with_items: hostvars
  when: inventory_hostname in groups['master']
  delegate_to: localhost
'''

RETURN = '''
peer_server:
    description: The remote IP address of the trusted peer.
    returned: changed
    type: string
    sample: "10.0.2.15"
peer_hostname:
    description: The remote hostname used to identify the trusted peer.
    returned: changed
    type: string
    sample: "test-bigip-02.localhost.localdomain"
'''

import re

try:
    import netaddr
    HAS_NETADDR = True
except ImportError:
    HAS_NETADDR = False

from ansible.module_utils.f5_utils import AnsibleF5Client
from ansible.module_utils.f5_utils import AnsibleF5Parameters
from ansible.module_utils.f5_utils import HAS_F5SDK
from ansible.module_utils.f5_utils import F5ModuleError

try:
    from ansible.module_utils.f5_utils import iControlUnexpectedHTTPError
except ImportError:
    HAS_F5SDK = False


class Parameters(AnsibleF5Parameters):
    api_map = {
        'deviceName': 'peer_hostname',
        'caDevice': 'type',
        'device': 'peer_server',
        'username': 'peer_user',
        'password': 'peer_password'
    }

    api_attributes = [
        'name', 'caDevice', 'device', 'deviceName', 'username', 'password'
    ]

    returnables = [
        'peer_server', 'peer_hostname'
    ]

    updatables = []

    def to_return(self):
        result = {}
        try:
            for returnable in self.returnables:
                result[returnable] = getattr(self, returnable)
            result = self._filter_params(result)
            return result
        except Exception:
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
    def peer_server(self):
        if self._values['peer_server'] is None:
            return None
        try:
            result = str(netaddr.IPAddress(self._values['peer_server']))
            return result
        except netaddr.core.AddrFormatError:
            raise F5ModuleError(
                "The provided 'peer_server' parameter is not an IP address."
            )

    @property
    def peer_hostname(self):
        if self._values['peer_hostname'] is None:
            return self.peer_server
        regex = re.compile('[^a-zA-Z.-_]')
        result = regex.sub('_', self._values['peer_hostname'])
        return result

    @property
    def partition(self):
        # Partitions are not supported when making peers.
        # Everybody goes in Common.
        return None

    @property
    def type(self):
        if self._values['type'] == 'peer':
            return True
        return False


class ModuleManager(object):
    def __init__(self, client):
        self.client = client
        self.have = None
        self.want = Parameters(self.client.module.params)
        self.changes = Parameters()

    def _set_changed_options(self):
        changed = {}
        for key in Parameters.returnables:
            if getattr(self.want, key) is not None:
                changed[key] = getattr(self.want, key)
        if changed:
            self.changes = Parameters(changed)

    def exec_module(self):
        changed = False
        result = dict()
        state = self.want.state

        try:
            if state == "present":
                changed = self.present()
            elif state == "absent":
                changed = self.absent()
        except iControlUnexpectedHTTPError as e:
            raise F5ModuleError(str(e))

        changes = self.changes.to_return()
        result.update(**changes)
        result.update(dict(changed=changed))
        return result

    def present(self):
        if self.exists():
            return False
        else:
            return self.create()

    def create(self):
        self._set_changed_options()
        if self.want.peer_user is None:
            self.want.update({'peer_user': self.want.user})
        if self.want.peer_password is None:
            self.want.update({'peer_password': self.want.password})
        if self.want.peer_hostname is None:
            self.want.update({'peer_hostname': self.want.server})
        if self.client.check_mode:
            return True
        self.create_on_device()
        return True

    def absent(self):
        if self.exists():
            return self.remove()
        return False

    def remove(self):
        if self.client.check_mode:
            return True
        self.remove_from_device()
        if self.exists():
            raise F5ModuleError("Failed to remove the trusted peer.")
        return True

    def exists(self):
        result = self.client.api.tm.cm.devices.get_collection()
        for device in result:
            try:
                if device.managementIp == self.want.peer_server:
                    return True
            except AttributeError:
                pass
        return False

    def create_on_device(self):
        params = self.want.api_params()
        import q
        q.q(params)
        self.client.api.tm.cm.add_to_trust.exec_cmd(
            'run',
            name='Root',
            **params
        )

    def remove_from_device(self):
        result = self.client.api.tm.cm.remove_from_trust.exec_cmd(
            'run', deviceName=self.want.peer_hostname
        )
        if result:
            result.delete()


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        self.argument_spec = dict(
            peer_server=dict(required=True),
            peer_hostname=dict(),
            peer_user=dict(),
            peer_password=dict(no_log=True),
            type=dict(
                choices=['peer', 'subordinate'],
                default='peer'
            )
        )
        self.f5_product_name = 'bigip'


def main():
    try:
        spec = ArgumentSpec()

        client = AnsibleF5Client(
            argument_spec=spec.argument_spec,
            supports_check_mode=spec.supports_check_mode,
            f5_product_name=spec.f5_product_name
        )

        if not HAS_F5SDK:
            raise F5ModuleError("The python f5-sdk module is required")

        if not HAS_NETADDR:
            raise F5ModuleError("The python netaddr module is required")

        mm = ModuleManager(client)
        results = mm.exec_module()
        client.module.exit_json(**results)
    except F5ModuleError as e:
        client.module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
