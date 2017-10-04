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
module: bigip_partition
short_description: Manage BIG-IP partitions.
description:
  - Manage BIG-IP partitions.
version_added: "2.5"
options:
  description:
    description:
      - The description to attach to the Partition.
  route_domain:
    description:
      - The default Route Domain to assign to the Partition. If no route domain
        is specified, then the default route domain for the system (typically
        zero) will be used only when creating a new partition.
  state:
    description:
      - Whether the partition should exist or not.
    default: present
    choices:
      - present
      - absent
notes:
  - Requires the f5-sdk Python package on the host. This is as easy as pip
    install f5-sdk.
  - Requires BIG-IP software version >= 12
requirements:
  - f5-sdk >= 2.2.3
extends_documentation_fragment: f5
author:
  - Tim Rupp (@caphrim007)
'''

EXAMPLES = '''
- name: Create partition "foo" using the default route domain
  bigip_partition:
      name: "foo"
      password: "secret"
      server: "lb.mydomain.com"
      user: "admin"
  delegate_to: localhost

- name: Create partition "bar" using a custom route domain
  bigip_partition:
      name: "bar"
      route_domain: 3
      password: "secret"
      server: "lb.mydomain.com"
      user: "admin"
  delegate_to: localhost

- name: Change route domain of partition "foo"
  bigip_partition:
      name: "foo"
      route_domain: 8
      password: "secret"
      server: "lb.mydomain.com"
      user: "admin"
  delegate_to: localhost

- name: Set a description for partition "foo"
  bigip_partition:
      name: "foo"
      description: "Tenant CompanyA"
      password: "secret"
      server: "lb.mydomain.com"
      user: "admin"
  delegate_to: localhost

- name: Delete the "foo" partition
  bigip_partition:
      name: "foo"
      password: "secret"
      server: "lb.mydomain.com"
      user: "admin"
      state: "absent"
  delegate_to: localhost
'''

RETURN = '''
route_domain:
    description: Name of the route domain associated with the partition.
    returned: changed and success
    type: int
    sample: 0
description:
    description: The description of the partition.
    returned: changed and success
    type: string
    sample: "Example partition"
'''

from ansible.module_utils.f5_utils import AnsibleF5Client
from ansible.module_utils.f5_utils import AnsibleF5Parameters
from ansible.module_utils.f5_utils import F5ModuleError
from ansible.module_utils.f5_utils import iteritems
from ansible.module_utils.f5_utils import defaultdict

try:
    from ansible.module_utils.f5_utils import HAS_F5SDK
    from ansible.module_utils.f5_utils import iControlUnexpectedHTTPError
except ImportError:
    HAS_F5SDK = False


class Parameters(AnsibleF5Parameters):
    api_map = {
        'defaultRouteDomain': 'route_domain',
    }

    api_attributes = [
        'description', 'defaultRouteDomain'
    ]

    returnables = [
        'description', 'route_domain'
    ]

    updatables = [
        'description', 'route_domain'
    ]

    def __init__(self, params=None):
        self._values = defaultdict(lambda: None)
        self._values['__warnings'] = []
        if params:
            self.update(params=params)

    def update(self, params=None):
        if params:
            for k, v in iteritems(params):
                if self.api_map is not None and k in self.api_map:
                    map_key = self.api_map[k]
                else:
                    map_key = k

                # Handle weird API parameters like `dns.proxy.__iter__` by
                # using a map provided by the module developer
                class_attr = getattr(type(self), map_key, None)
                if isinstance(class_attr, property):
                    # There is a mapped value for the api_map key
                    if class_attr.fset is None:
                        # If the mapped value does not have
                        # an associated setter
                        self._values[map_key] = v
                    else:
                        # The mapped value has a setter
                        setattr(self, map_key, v)
                else:
                    # If the mapped value is not a @property
                    self._values[map_key] = v

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
    def partition(self):
        # Cannot create a partition in a partition, so nullify this
        return None

    @property
    def route_domain(self):
        if self._values['route_domain'] is None:
            return None
        return int(self._values['route_domain'])


class Difference(object):
    def __init__(self, want, have=None):
        self.want = want
        self.have = have

    def compare(self, param):
        try:
            result = getattr(self, param)
            return result
        except AttributeError:
            result = self.__default(param)
            return result

    def __default(self, param):
        attr1 = getattr(self.want, param)
        try:
            attr2 = getattr(self.have, param)
            if attr1 != attr2:
                return attr1
        except AttributeError:
            return attr1


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

    def _update_changed_options(self):
        diff = Difference(self.want, self.have)
        updatables = Parameters.updatables
        changed = dict()
        for k in updatables:
            change = diff.compare(k)
            if change is None:
                continue
            else:
                changed[k] = change
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
            return self.update()
        else:
            return self.create()

    def create(self):
        if self.client.check_mode:
            return True
        self.create_on_device()
        if not self.exists():
            raise F5ModuleError("Failed to create the partition.")
        return True

    def should_update(self):
        result = self._update_changed_options()
        if result:
            return True
        return False

    def update(self):
        self.have = self.read_current_from_device()
        if not self.should_update():
            return False
        if self.client.check_mode:
            return True
        self.update_on_device()
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
            raise F5ModuleError("Failed to delete the partition.")
        return True

    def read_current_from_device(self):
        resource = self.client.api.tm.auth.partitions.partition.load(
            name=self.want.name
        )
        result = resource.attrs
        return Parameters(result)

    def exists(self):
        result = self.client.api.tm.auth.partitions.partition.exists(
            name=self.want.name
        )
        return result

    def update_on_device(self):
        params = self.want.api_params()
        result = self.client.api.tm.auth.partitions.partition.load(
            name=self.want.name
        )
        result.modify(**params)

    def create_on_device(self):
        params = self.want.api_params()
        self.client.api.tm.auth.partitions.partition.create(
            name=self.want.name,
            **params
        )

    def remove_from_device(self):
        result = self.client.api.tm.auth.partitions.partition.load(
            name=self.want.name
        )
        if result:
            result.delete()


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        self.argument_spec = dict(
            name=dict(required=True),
            description=dict(),
            route_domain=dict(type='int'),
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

        mm = ModuleManager(client)
        results = mm.exec_module()
        client.module.exit_json(**results)
    except F5ModuleError as e:
        client.module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
