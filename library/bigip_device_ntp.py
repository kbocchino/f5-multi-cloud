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
module: bigip_device_ntp
short_description: Manage NTP servers on a BIG-IP.
description:
  - Manage NTP servers on a BIG-IP.
version_added: "2.2"
options:
  ntp_servers:
    description:
      - A list of NTP servers to set on the device. At least one of C(ntp_servers)
        or C(timezone) is required.
    required: false
    default: []
  state:
    description:
      - The state of the NTP servers on the system. When C(present), guarantees
        that the NTP servers are set on the system. When C(absent), removes the
        specified NTP servers from the device configuration.
    required: false
    default: present
    choices:
      - absent
      - present
  timezone:
    description:
      - The timezone to set for NTP lookups. At least one of C(ntp_servers) or
        C(timezone) is required.
    default: UTC
    required: false
notes:
  - Requires the f5-sdk Python package on the host. This is as easy as pip
    install f5-sdk.
extends_documentation_fragment: f5
requirements:
  - f5-sdk
authors:
  - Tim Rupp (@caphrim007)
  - Wojciech Wypior (@wojtek0806)
'''

EXAMPLES = '''
- name: Set NTP server
  bigip_device_ntp:
      ntp_servers:
          - "192.0.2.23"
      password: "secret"
      server: "lb.mydomain.com"
      user: "admin"
      validate_certs: "no"
  delegate_to: localhost

- name: Set timezone
  bigip_device_ntp:
      password: "secret"
      server: "lb.mydomain.com"
      timezone: "America/Los_Angeles"
      user: "admin"
      validate_certs: "no"
  delegate_to: localhost
'''

RETURN = '''
ntp_servers:
    description: The NTP servers that were set on the device
    returned: changed
    type: list
    sample: ["192.0.2.23", "192.0.2.42"]
timezone:
    description: The timezone that was set on the device
    returned: changed
    type: string
    sample: "true"
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
        'servers': 'ntp_servers'
    }

    api_attributes = [
        'servers', 'timezone',
    ]

    updatables = [
        'ntp_servers', 'timezone'
    ]

    returnables = [
        'ntp_servers', 'timezone'
    ]

    absentables = [
        'ntp_servers'
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
                result[api_attribute] = getattr(self,
                                                self.api_map[api_attribute])
            else:
                result[api_attribute] = getattr(self, api_attribute)
        result = self._filter_params(result)
        return result


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

    def _absent_changed_options(self):
        changed = {}
        for key in Parameters.absentables:
            if getattr(self.want, key) is not None:
                set_want = set(getattr(self.want, key))
                set_have = set(getattr(self.have, key))
                if set_want != set_have:
                    changed[key] = list(set_want)
        if changed:
            self.changes = Parameters(changed)
            return True
        return False

    def exec_module(self):
        changed = False
        result = dict()
        state = self.want.state

        try:
            if state == "present":
                changed = self.update()
            elif state == "absent":
                changed = self.absent()
        except iControlUnexpectedHTTPError as e:
            raise F5ModuleError(str(e))

        changes = self.changes.to_return()
        result.update(**changes)
        result.update(dict(changed=changed))
        return result

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

    def should_absent(self):
        result = self._absent_changed_options()
        if result:
            return True
        return False

    def absent(self):
        self.have = self.read_current_from_device()
        if not self.should_absent():
            return False
        if self.client.check_mode:
            return True
        self.absent_on_device()
        return True

    def update_on_device(self):
        params = self.want.api_params()
        resource = self.client.api.tm.sys.ntp.load()
        resource.update(**params)

    def read_current_from_device(self):
        resource = self.client.api.tm.sys.ntp.load()
        result = resource.attrs
        return Parameters(result)

    def absent_on_device(self):
        params = self.changes.api_params()
        resource = self.client.api.tm.sys.ntp.load()
        resource.update(**params)


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        self.argument_spec = dict(
            ntp_servers=dict(
                required=False,
                default=None,
                type='list',
            ),
            timezone=dict(
                required=False,
                default=None,
            )
        )
        self.required_one_of = [
            ['ntp_servers', 'timezone']
        ]
        self.f5_product_name = 'bigip'


def main():
    if not HAS_F5SDK:
        raise F5ModuleError("The python f5-sdk module is required")

    spec = ArgumentSpec()

    client = AnsibleF5Client(
        argument_spec=spec.argument_spec,
        supports_check_mode=spec.supports_check_mode,
        f5_product_name=spec.f5_product_name,
        required_one_of=spec.required_one_of
    )

    try:
        mm = ModuleManager(client)
        results = mm.exec_module()
        client.module.exit_json(**results)
    except F5ModuleError as e:
        client.module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
