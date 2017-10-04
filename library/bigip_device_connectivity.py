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
module: bigip_device_connectivity
short_description: Manages device IP configuration settings for HA on a BIG-IP.
description:
  - Manages device IP configuration settings for HA on a BIG-IP. Each BIG-IP device
    has synchronization and failover connectivity information (IP addresses) that
    you define as part of HA pairing or clustering. This module allows you to configure
    that information.
version_added: "2.4"
options:
  config_sync_ip:
    description:
      - Local IP address that the system uses for ConfigSync operations.
  mirror_primary_address:
    description:
      - Specifies the primary IP address for the system to use to mirror
        connections.
  mirror_secondary_address:
    description:
      - Specifies the secondary IP address for the system to use to mirror
        connections.
  unicast_failover:
    description:
      - Desired addresses to use for failover operations. Options C(address)
        and C(port) are supported with dictionary structure where C(address) is the
        local IP address that the system uses for failover operations. Port
        specifies the port that the system uses for failover operations. If C(port)
        is not specified, the default value C(1026) will be used.
  failover_multicast:
    description:
      - When C(yes), ensures that the Failover Multicast configuration is enabled
        and if no further multicast configuration is provided, ensures that
        C(multicast_interface), C(multicast_address) and C(multicast_port) are
        the defaults specified in each option's description. When C(no), ensures
        that Failover Multicast configuration is disabled.
    choices:
      - yes
      - no
  multicast_interface:
    description:
      - Interface over which the system sends multicast messages associated
        with failover. When C(failover_multicast) is C(yes) and this option is
        not provided, a default of C(eth0) will be used.
  multicast_address:
    description:
      - IP address for the system to send multicast messages associated with
        failover. When C(failover_multicast) is C(yes) and this option is not
        provided, a default of C(224.0.0.245) will be used.
  multicast_port:
    description:
      - Port for the system to send multicast messages associated with
        failover. When C(failover_multicast) is C(yes) and this option is not
        provided, a default of C(62960) will be used. This value must be between
        0 and 65535.
notes:
  - Requires the f5-sdk Python package on the host. This is as easy as pip
    install f5-sdk.
  - This module is primarily used as a component of configuring HA pairs of
    BIG-IP devices.
  - Requires BIG-IP >= 12.1.x.
requirements:
  - f5-sdk >= 2.2.3
extends_documentation_fragment: f5
author:
  - Tim Rupp (@caphrim007)
'''

EXAMPLES = '''
- name: Configure device connectivity for standard HA pair
  bigip_device_connectivity:
      config_sync_ip: "10.1.30.1"
      mirror_primary_address: "10.1.30.1"
      unicast_failover:
          - address: "10.1.30.1"
      server: "lb.mydomain.com"
      user: "admin"
      password: "secret"
  delegate_to: localhost
'''

RETURN = '''
changed:
    description: Denotes if the F5 configuration was updated.
    returned: always
    type: bool
config_sync_ip:
    description: The new value of the C(config_sync_ip) setting.
    returned: changed
    type: string
    sample: "10.1.1.1"
mirror_primary_address:
    description: The new value of the C(mirror_primary_address) setting.
    returned: changed
    type: string
    sample: "10.1.1.2"
mirror_secondary_address:
    description: The new value of the C(mirror_secondary_address) setting.
    return: changed
    type: string
    sample: "10.1.1.3"
unicast_failover:
    description: The new value of the C(unicast_failover) setting.
    return: changed
    type: list
    sample: [{'address': '10.1.1.2', 'port': 1026}]
failover_multicast:
    description: Whether a failover multicast attribute has been changed or not.
    return: changed
    type: bool
multicast_interface:
    description: The new value of the C(multicast_interface) setting.
    return: changed
    type: string
    sample: "eth0"
multicast_address:
    description: The new value of the C(multicast_address) setting.
    return: changed
    type: string
    sample: "224.0.0.245"
multicast_port:
    description: The new value of the C(multicast_port) setting.
    return: changed
    type: string
    sample: 1026
'''

from netaddr import IPAddress, AddrFormatError
from ansible.module_utils.f5_utils import (
    AnsibleF5Client,
    AnsibleF5Parameters,
    HAS_F5SDK,
    F5ModuleError,
    iControlUnexpectedHTTPError
)


class Parameters(AnsibleF5Parameters):
    api_map = {
        'configsyncIp': 'config_sync_ip',
        'multicastInterface': 'multicast_interface',
        'multicastIp': 'multicast_address',
        'multicastPort': 'multicast_port',
        'mirrorIp': 'mirror_primary_address',
        'mirrorSecondaryIp': 'mirror_secondary_address'
    }
    api_attributes = [
        'configsyncIp', 'multicastInterface', 'multicastIp', 'multicastPort',
        'mirrorIp', 'mirrorSecondaryIp', 'unicastAddress'
    ]
    returnables = [
        'config_sync_ip', 'multicast_interface', 'multicast_address',
        'multicast_port', 'mirror_primary_address', 'mirror_secondary_address',
        'failover_multicast', 'unicast_failover'
    ]
    updatables = [
        'config_sync_ip', 'multicast_interface', 'multicast_address',
        'multicast_port', 'mirror_primary_address', 'mirror_secondary_address',
        'failover_multicast', 'unicast_failover'
    ]

    @property
    def multicast_port(self):
        if self._values['multicast_port'] is None:
            return None
        result = int(self._values['multicast_port'])
        if result < 0 or result > 65535:
            raise F5ModuleError(
                "The specified 'multicast_port' must be between 0 and 65535."
            )
        return result

    @property
    def multicast_address(self):
        if self._values['multicast_address'] is None:
            return None
        elif self._values['multicast_address'] in ["none", "any6", '']:
            return "any6"
        result = self._get_validated_ip_address('multicast_address')
        return result

    @property
    def mirror_primary_address(self):
        if self._values['mirror_primary_address'] is None:
            return None
        elif self._values['mirror_primary_address'] in ["none", "any6", '']:
            return "any6"
        result = self._get_validated_ip_address('mirror_primary_address')
        return result

    @property
    def mirror_secondary_address(self):
        if self._values['mirror_secondary_address'] is None:
            return None
        elif self._values['mirror_secondary_address'] in ["none", "any6", '']:
            return "any6"
        result = self._get_validated_ip_address('mirror_secondary_address')
        return result

    @property
    def managementIp(self):
        result = self._values['management_ip']
        return result

    @managementIp.setter
    def managementIp(self, value):
        self._values['management_ip'] = value

    @property
    def config_sync_ip(self):
        if self._values['config_sync_ip'] is None:
            return None
        elif self._values['config_sync_ip'] in ["none", '']:
            return "none"
        result = self._get_validated_ip_address('config_sync_ip')
        return result

    @property
    def unicastAddress(self):
        return self.unicast_failover

    @unicastAddress.setter
    def unicastAddress(self, value):
        result = []
        for item in value:
            if item['ip'] == 'management-ip':
                del item['ip']
                item['address'] = self._values['management_ip']
            else:
                item['address'] = item.pop('ip')
            result.append(item)
        if result:
            self._values['unicast_failover'] = result

    @property
    def unicast_failover(self):
        if self._values['unicast_failover'] is None:
            return None
        if self._values['unicast_failover'] == ['none']:
            return []
        result = []
        for item in self._values['unicast_failover']:
            address = item.get('address', None)
            port = item.get('port', None)
            address = self._validate_unicast_failover_address(address)
            port = self._validate_unicast_failover_port(port)
            result.append(
                dict(
                    effectiveIp=address,
                    effectivePort=port,
                    ip=address,
                    port=port
                )
            )
        if result:
            return result
        else:
            return None

    def _validate_unicast_failover_port(self, port):
        try:
            result = int(port)
        except ValueError:
            raise F5ModuleError(
                "The provided 'port' for unicast failover is not a valid number"
            )
        except TypeError:
            result = 1026
        return result

    def _validate_unicast_failover_address(self, address):
        try:
            result = IPAddress(address)
            return str(result)
        except KeyError:
            raise F5ModuleError(
                "An 'address' must be supplied when configuring unicast failover"
            )
        except AddrFormatError:
            raise F5ModuleError(
                "'address' field in unicast failover is not a valid IP address"
            )

    def _get_validated_ip_address(self, address):
        try:
            IPAddress(self._values[address])
            return self._values[address]
        except AddrFormatError:
            raise F5ModuleError(
                "The specified '{0}' is not a valid IP address".format(
                    address
                )
            )

    def api_params(self):
        result = {}
        for api_attribute in self.api_attributes:
            if self.api_map is not None and api_attribute in self.api_map:
                result[api_attribute] = getattr(self, self.api_map[api_attribute])
            else:
                result[api_attribute] = getattr(self, api_attribute)
        result = self._filter_params(result)
        return result

    def to_return(self):
        result = {}
        try:
            for returnable in self.returnables:
                result[returnable] = getattr(self, returnable)
        except Exception:
            pass
        result = self._filter_params(result)
        return result


class Changes(Parameters):
    @property
    def mirror_primary_address(self):
        if self._values['mirror_primary_address'] == 'any6':
            return "none"
        else:
            return self._values['mirror_primary_address']

    @property
    def mirror_secondary_address(self):
        if self._values['mirror_secondary_address'] == 'any6':
            return "none"
        else:
            return self._values['mirror_secondary_address']

    @property
    def multicast_address(self):
        if self._values['multicast_address'] == 'any6':
            return "none"
        else:
            return self._values['multicast_address']

    @property
    def unicast_failover(self):
        if self._values['unicast_failover'] is None:
            return None
        elif self._values['unicast_failover']:
            return self._values['unicast_failover']
        return "none"

    @property
    def failover_multicast(self):
        values = ['multicast_address', 'multicast_interface', 'multicast_port']
        if all(self._values[x] in [None, 'any6'] for x in values):
            return None
        return True


class ModuleManager(object):
    def __init__(self, client):
        self.client = client
        self.want = Parameters(self.client.module.params)
        self.changes = Changes()

    def _update_changed_options(self):
        changed = {}
        for key in Parameters.updatables:
            if getattr(self.want, key) is not None:
                attr1 = getattr(self.want, key)
                attr2 = getattr(self.have, key)
                if attr1 != attr2:
                    changed[key] = attr1
        if changed:
            self.changes = Changes(changed)
            return True
        return False

    def should_update(self):
        result = self._update_changed_options()
        if result:
            return True
        return False

    def exec_module(self):
        changed = False
        result = dict()
        state = self.want.state

        try:
            if state == "present":
                changed = self.update()
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

    def remove(self):
        if self.client.check_mode:
            return True
        self.remove_from_device()
        return True

    def update_on_device(self):
        params = self.want.api_params()
        collection = self.client.api.tm.cm.devices.get_collection()
        for resource in collection:
            if resource.selfDevice == 'true':
                resource.modify(**params)
                return
        raise F5ModuleError(
            "The host device was not found."
        )

    def read_current_from_device(self):
        collection = self.client.api.tm.cm.devices.get_collection()
        for resource in collection:
            if resource.selfDevice == 'true':
                result = resource.attrs
                return Parameters(result)
        raise F5ModuleError(
            "The host device was not found."
        )


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        self.argument_spec = dict(
            multicast_port=dict(
                type='int'
            ),
            multicast_address=dict(),
            multicast_interface=dict(),
            failover_multicast=dict(
                type='bool'
            ),
            unicast_failover=dict(
                type='list'
            ),
            mirror_primary_address=dict(),
            mirror_secondary_address=dict(),
            config_sync_ip=dict(),
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
