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
module: bigip_software
short_description: Manage BIG-IP software versions and hotfixes
description:
   - Manage BIG-IP software versions and hotfixes
version_added: "2.4"
options:
  force:
    description:
      - If C(yes) will upload the file every time and replace the file on the
        device. If C(no), the file will only be uploaded if it does not already
        exist. Generally should be C(yes) only in cases where you have reason
        to believe that the image was corrupted during upload.
      - If C(yes) with C(reuse_inactive_volume) is specified and C(volume) is
        not specified, Software will be installed / activated regardless of
        current running version to a new or an existing volume.
    default: no
    choices:
      - yes
      - no
  reuse_inactive_volume:
    description:
      - Automatically chooses the first inactive volume in alphanumeric order.
        If there is no inactive volume, new volume with incremented volume name
        will be created. For example, if HD1.1 is currently active and no other
        volume exists, then the module will create HD1.2 and install the
        software. If volume name does not end with numeric character,
        then add .1 to the current active volume name. When C(volume) is
        specified, this option will be ignored.
  state:
    description:
      - When C(installed), ensures that the software is uploaded/downloaded
        and installed on the system. The device is not, however, rebooted into
        the new software.
      - When C(activated), ensures that the software is uploaded/downloaded,
        installed, and the system is rebooted to the new software.
      - When C(present), ensures that the software is uploaded/downloaded.
      - When C(absent), only the uploaded/downloaded image
        will be removed from the system.
    default: activated
    choices:
      - absent
      - activated
      - installed
      - present
  volume:
    description:
      - The volume to install the software and, optionally, the hotfix to. This
        parameter is only required when the C(state) is either C(activated) or
        C(installed).
  software:
    description:
      - The path to the software (base image) to install. The parameter must be
        provided if the C(state) is either C(installed) or C(activated).
      - If C(remote_src) is used, this parameter will have to be a
        C(HTTP) or C(HTTPS)link to the software image.
      - When providing link to the software ISO, if the ISO name is
        different than the one listed inside the C(software_md5sum) md5sum file.
        We will change it accordingly when saving the files on the device. This
        might lead to ISO names not matching the links provided in C(software).
    aliases:
      - base_image
  hotfix:
    description:
      - The path to an optional Hotfix to install. This parameter requires that
        the C(software) parameter be specified or the corresponding software
        image exists on the unit.
      - If C(remote_src) is used, this parameter will have to be a
        C(HTTP) or C(HTTPS)link to the hotfix image.
      - When providing link to the hotfix ISO, if the ISO name
        is different than the one listed inside the C(hotfix_md5) md5sum file.
        We will change it accordingly while saving the files on the device.
        This might lead to ISO names not matching the links provided
        in C(hotfix).
    aliases:
      - hotfix_image
  software_md5sum:
    description:
      - The link to an MD5 sum file of the remote software ISO image,
        it is required when  C(software) parameter is used and C(remote_src)
        is selected.
      - Parameter only used when and C(state) is C(installed), C(activated),
        or C(present).
  hotfix_md5sum:
    description:
      - The link to an MD5 sum file of the remote hotfix ISO image,
        it is required when C(hotfix) parameter is used and C(remote_src)
        is selected.
      - Parameter only used when and C(state) is C(installed), C(activated),
        or C(present).
  build:
     description:
     - Parameter specifying build number of the remote ISO image.
       This parameter is mandatory when C(remote_src) is in use.
     - If C(hotfix) and C(software) are specified. The build number will be
       C(always) the C(build) of the C(hotfix). For example, C(hotfix) has
       build of C(1.0.271) and C(software) has a build of C(0.0.249),
       then C(build) parameter has to be set to C(1.0.271).
     - If this parameter is missing when C(state) is C(activated)
       or C(installed), there will be an attempt to supplement that information
       with searching by name for relevant ISO on the unit. When none is found
       the exception will be raised and process terminated.
     - If this parameter is missing when C(state) is C(present)
       we will confirm the existence of the ISO with searching by name.
       If the ISO exists under different name, it might lead to duplication of
       ISO images on the unit.
     - Finally if this parameter is missing when C(state) is
       C(absent) it might cause the desired ISO not to be deleted.
  version:
     description:
     - Parameter specifying version of of the remote ISO image.
       This parameter is mandatory when C(remote_src) is in use.
     - If C(hotfix) and C(software) are specified. The version number C(always)
       be the C(version) of the C(hotfix).
     - If this parameter is missing when C(state) is C(activated)
       or C(installed), there will be an attempt to supplement that information
       with searching by name for relevant ISO on the unit. When none is found
       the exception will be raised and process terminated.
     - If this parameter is missing when C(state) is C(present)
       we will confirm the existence of the ISO with searching by name. If the
       ISO exists under different name, it might lead to duplication of ISO
       images on the unit.
     - Finally if this parameter is missing when C(state) is
       C(absent) it might cause the desired ISO not to be deleted.
  remote_src:
    description:
       - Parameter to enable remote source usage. When set to C(yes) bigip will
         attempt to download and verify the images using the links provided in
         C(software), C(hotfix), C(software_md5sum) and C(hotfix_md5sum).
       - This parameter also makes the C(software_md5sum) and C(hotfix_md5sum)
         mandatory when C(state is C(present), C(activated) or C(installed).
    default: 'no'
notes:
  - Requires the f5-sdk Python package on the host.
    This is as easy as pip install f5-sdk
  - Requires the isoparser Python package on the host. This can be installed
    with pip install isoparser
  - Requires the lxml Python package on the host. This can be installed
    with pip install lxml
extends_documentation_fragment: f5
requirements:
  - f5-sdk
  - isoparser
authors:
  - Tim Rupp (@caphrim007)
  - Wojciech Wypior (@wojtek0806)
'''

EXAMPLES = '''
- name: Remove uploaded hotfix
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      hotfix: "/root/Hotfix-BIGIP-11.6.0.3.0.412-HF3.iso"
      state: "absent"
  delegate_to: localhost

- name: Upload hotfix
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      hotfix: "/root/Hotfix-BIGIP-11.6.0.3.0.412-HF3.iso"
      state: "present"
  delegate_to: localhost

- name: Remove uploaded base image
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "/root/BIGIP-11.6.0.0.0.401.iso"
      state: "absent"
  delegate_to: localhost

- name: Upload base image
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "/root/BIGIP-11.6.0.0.0.401.iso"
      state: "present"
  delegate_to: localhost

- name: Upload base image and hotfix
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "/root/BIGIP-11.6.0.0.0.401.iso"
      hotfix: "/root/Hotfix-BIGIP-11.6.0.3.0.412-HF3.iso"
      state: "present"
  delegate_to: localhost

- name: Remove uploaded base image and hotfix
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "/root/BIGIP-11.6.0.0.0.401.iso"
      hotfix: "/root/Hotfix-BIGIP-11.6.0.3.0.412-HF3.iso"
      state: "absent"
  delegate_to: localhost

- name: Install (upload, install) base image. Create volume if not exists
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "/root/BIGIP-11.6.0.0.0.401.iso"
      volume: "HD1.1"
      state: "installed"
  delegate_to: localhost

- name: Install (upload, install) base image and hotfix. Create volume if not exists
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "/root/BIGIP-11.6.0.0.0.401.iso"
      hotfix: "/root/Hotfix-BIGIP-11.6.0.3.0.412-HF3.iso"
      volume: "HD1.1"
      state: "installed"
  delegate_to: localhost

- name: Activate (upload, install, reboot) base image. Create volume if not exists
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "/root/BIGIP-11.6.0.0.0.401.iso"
      volume: "HD1.1"
      state: "activated"
  delegate_to: localhost

- name: Activate (upload, install, reboot) base image and hotfix. Create volume if not exists
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "/root/BIGIP-11.6.0.0.0.401.iso"
      hotfix: "/root/Hotfix-BIGIP-11.6.0.3.0.412-HF3.iso"
      volume: "HD1.1"
      state: "activated"
  delegate_to: localhost

- name: Activate (upload, install, reboot) base image and hotfix. Reuse inactive volume in volumes with prefix.
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "/root/BIGIP-11.6.0.0.0.401.iso"
      hotfix: "/root/Hotfix-BIGIP-11.6.0.3.0.412-HF3.iso"
      reuse_inactive_volume: yes
      state: "activated"
  delegate_to: localhost

- name: Activate (download, install, reboot, reuse_inactive_volume) base image and hotfix
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      hotfix: "http://fake.com/Hotfix-12.1.2.1.0.271-HF1.iso"
      hotfix_md5sum: "http://fake.com/Hotfix-12.1.2.1.0.271-HF1.iso.md5"
      software: "http://fake.com/BIGIP-12.1.2.0.0.249.iso"
      software_md5sum: "http://fake.com/BIGIP-12.1.2.0.0.249.iso.md5"
      build: "1.0.271"
      version: "12.1.2"
      remote_src: "yes"
      state: "activated"
      reuse_inactive_volume: True
  delegate_to: localhost

- name: Download hotfix image
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      hotfix: "http://fake.com/Hotfix-12.1.2.1.0.271-HF1.iso"
      hotfix_md5sum: "http://fake.com/Hotfix-12.1.2.1.0.271-HF1.iso.md5"
      build: "1.0.271"
      version: "12.1.2"
      remote_src: "yes"
      state: "present"
  delegate_to: localhost

- name: Remove uploaded hotfix image
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      hotfix: "http://fake.com/Hotfix-12.1.2.1.0.271-HF1.iso"
      build: "1.0.271"
      version: "12.1.2"
      remote_src: "yes"
  delegate_to: localhost

- name: Install (download, install) base image
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "http://fake.com/BIGIP-12.1.2.0.0.249.iso"
      software_md5sum: "http://fake.com/BIGIP-12.1.2.0.0.249.iso.md5"
      build: "0.0.249"
      version: "12.1.2"
      remote_src: "yes"
      volume: "HD1.1"
      state: "installed"
  delegate_to: localhost

- name: Install (download, install) base image and hotfix
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      hotfix: "http://fake.com/Hotfix-12.1.2.1.0.271-HF1.iso"
      hotfix_md5sum: "http://fake.com/Hotfix-12.1.2.1.0.271-HF1.iso.md5"
      software: "http://fake.com/BIGIP-12.1.2.0.0.249.iso"
      software_md5sum: "http://fake.com/BIGIP-12.1.2.0.0.249.iso.md5"
      build: "1.0.271"
      version: "12.1.2"
      remote_src: "yes"
      state: "installed"
      volume: "HD1.2"
   delegate_to: localhost

- name: Download hotfix image (name mismatch)
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      hotfix: "http://fake.com/12.1.2-HF1.iso"
      hotfix_md5sum: "http://fake.com/Hotfix-12.1.2HF1.md5"
      build: "1.0.271"
      version: "12.1.2"
      remote_src: "yes"
      state: "present"
  delegate_to: localhost

- name: Download software image (name mismatch)
  bigip_software:
      server: "bigip.localhost.localdomain"
      user: "admin"
      password: "admin"
      software: "http://fake.com/BIGIP-12.1.2.iso"
      software_md5sum: "http://fake.com/12.1.2.md5"
      build: "0.0.249"
      version: "12.1.2"
      remote_src: "yes"
      state: "present"
  delegate_to: localhost
'''

RETURN = '''
force:
    description: Set when forcing the ISO upload/download.
    returned: changed
    type: bool
    sample: yes
state:
    description: Action performed on the target device.
    returned: changed
    type: string
    sample: "absent"
reuse_inactive_volume:
    description: Create volume or reuse existing volume.
    returned: changed
    type: bool
    sample: no
remote_src:
    description: Download ISO on the target device.
    returned: changed
    type: bool
    sample: "yes"
software:
    description: Local path, or remote link to the software ISO image.
    returned: changed
    type: string
    sample: "http://someweb.com/fake/software.iso"
hotfix:
    description: Local path, or remote link to the hotfix ISO image.
    returned: changed
    type: string
    sample: "/root/hotfixes/hotfix.iso"
software_md5:
    description: MD5 sum file for the remote software ISO image.
    returned: changed
    type: string
    sample: "http://someweb.com/fake/software.iso.md5"
hotfix_md5:
    description: MD5 sum file for the remote hotfix ISO image.
    returned: changed
    type: string
    sample: "http://someweb.com/fake/hotfix.iso.md5"
build:
    description: Build of the remote ISO image.
    returned: changed
    type: string
    sample: "0.0.249"
version:
    description: Version of the remote ISO image.
    returned: changed
    type: string
    sample: "12.1.1"
volume:
    description: Volume to install desired image on
    returned: changed
    type: string
    sample: "HD1.2"
'''

import io
import isoparser
from ansible.module_utils.f5_utils import (
    AnsibleF5Parameters,
    AnsibleF5Client,
    defaultdict,
    F5ModuleError,
    HAS_F5SDK,
    iControlUnexpectedHTTPError,
    iteritems,
    os,
    time
)
from lxml import etree

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse


class Parameters(AnsibleF5Parameters):
    def __init__(self, params=None):
        self._values = defaultdict(lambda: None)
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

    updatables = [
        'version', 'volume', 'build'
    ]

    returnables = [
        'force', 'hotfix', 'state',
        'software', 'volume', 'reuse_inactive_volume', 'remote_src',
        'software_md5sum', 'hotfix_md5sum', 'build', 'version'
    ]

    api_attributes = [
        'volume', 'options'
    ]

    api_map = {'name': 'volume'}

    @property
    def remote_src(self):
        remote = self._values['remote_src']
        image_md5sum = self._values['software_md5sum']
        hotfix_md5sum = self._values['hotfix_md5sum']
        state = self._values['state']
        hotfix = self._values['hotfix']
        software = self._values['software']
        err = 'You must provide md5sum file links if using remote source.'

        if state != 'absent':
            if remote:
                if hotfix and software:
                    if not image_md5sum or not hotfix_md5sum:
                        raise F5ModuleError(err)
                    return remote
                elif hotfix:
                    if not hotfix_md5sum:
                        raise F5ModuleError(err)
                    return remote
                elif software:
                        if not image_md5sum:
                            raise F5ModuleError(err)
                        return remote
            else:
                return remote
        else:
            return remote

    @property
    def software(self):
        link = self._values['software']
        link_md5 = self._values['software_md5sum']
        remote = self.remote_src

        if link is None:
            return None

        if remote:
            software = self.handle_remote_source(link)
            self._values['software_name'] = software
            if link_md5:
                image_md5 = self.handle_remote_source(link_md5)
                self._values['imgmd5_name'] = image_md5

        else:
            software = os.path.split(link)[1]
            self._values['software_name'] = software

        return self._values['software']

    @property
    def hotfix(self):
        link = self._values['hotfix']
        link_md5 = self._values['hotfix_md5sum']
        remote = self.remote_src

        if link is None:
            return None

        if remote:
            hotfix = self.handle_remote_source(link)
            self._values['hotfix_name'] = hotfix
            if link_md5:
                hotfix_md5 = self.handle_remote_source(link_md5)
                self._values['hfmd5_name'] = hotfix_md5

        else:
            hotfix = os.path.split(link)[1]
            self._values['hotfix_name'] = hotfix

        return self._values['hotfix']

    @property
    def options(self):
        state = self._values['state']
        create = self._values['create_volume']
        opt = list()

        if create:
            opt.append({'create-volume': True})
        if state == 'activated':
            opt.append({'reboot': True})

        return opt

    @property
    def volume(self):
        state = self._values['state']
        volume = self._values['volume']
        reuse = self._values['reuse_inactive_volume']

        if state in ['absent', 'present', None]:
            return self._values['volume']

        if volume is not None:
            if not self._volume_exists_on_device(volume):
                self._values['create_volume'] = True
            else:
                self._check_active_volume(volume)

            return self._values['volume']

        if volume is None:
            if reuse:
                new_volume = self._get_next_available_volume()
                if self._volume_exists_on_device(volume):
                    self._values['delete_volume'] = True
                    self._values['create_volume'] = True
                else:
                    self._values['create_volume'] = True
                self._values['volume'] = new_volume

                return self._values['volume']
            else:
                raise F5ModuleError('You must specify a volume.')

    @property
    def version(self):
        psoftware = self.software
        photfix = self.hotfix
        remote = self.remote_src
        version = self._values['version']

        if version is True:
            return version

        if remote is False and version is None:
            if photfix:
                self.use_iso(photfix)
            else:
                self.use_iso(psoftware)

        return self._values['version']

    @property
    def build(self):
        psoftware = self.software
        photfix = self.hotfix
        remote = self.remote_src
        build = self._values['build']

        if remote is True:
            return build

        if remote is False and build is None:
            if photfix:
                self.use_iso(photfix)
            else:
                self.use_iso(psoftware)

        return self._values['build']

    @version.setter
    def version(self, value):
        self._values['version'] = value

    @build.setter
    def build(self, value):
        self._values['build'] = value

    def use_iso(self, iso):
        iso = isoparser.parse(iso)
        content = self._find_iso_content(iso)
        content = io.BytesIO(content)
        context = etree.iterparse(content)
        for action, elem in context:
            if elem.text:
                text = elem.text
            if elem.tag == 'version':
                self._values['version'] = text
            elif elem.tag == 'buildNumber':
                self._values['build'] = text

    def _find_iso_content(self, iso):
        paths = ['/METADATA.XML', 'metadata.xml']

        for path in paths:
            try:
                content = iso.record(path).content
                return content
            except KeyError:
                pass
        raise F5ModuleError('Unable to find metadata file in ISO. Please file a bug.')

    def handle_remote_source(self, link):
        source = urlparse.urlparse(link)
        name = source.path.split('/')[-1]
        if source.scheme:
            if source.scheme == 'http':
                return name
            elif source.scheme == 'https':
                self._values['secure'] = True
                return name
            else:
                raise F5ModuleError('Only remote HTTP or HTTPS sources are supported.')
        else:
            raise F5ModuleError('{0} is not a valid URL, please provide a valid link'.format(link))

    def _list_volumes_on_device(self):
        volumes = self.client.api.tm.sys.software.volumes.get_collection()
        return volumes

    def _load_volume_from_device(self, volume):
        vol = self.client.api.tm.sys.software.volumes.volume.load(
            name=volume)
        return vol

    def _volume_exists_on_device(self, volume):
        result = self.client.api.tm.sys.software.volumes.volume.exists(name=volume)
        return result

    def _check_active_volume(self, volume):
        v = self._load_volume_from_device(volume)
        if hasattr(v, 'active') and v.active is True:
            raise F5ModuleError('Cannot install software or hotfixes to active volumes.')

    def _get_next_available_volume(self):
        volumes = self._list_volumes_on_device()
        if len(volumes) == 1:
            for vol in volumes:
                if hasattr(vol, 'active') and vol.active is True:
                    return self._volume_name_increment(vol.name)
        else:
            for vol in volumes:
                if not hasattr(vol, 'active') or vol.active is not True:
                    return str(vol.name)

    def _volume_name_increment(self, active):
        try:
            active_volume = str(active).split('.')
            active_volume[-1] = str(int(active_volume[-1]) + 1)
            target_volume_name = '.'.join(active_volume)
        except Exception:
            target_volume_name = str(active) + '.1'

        self._values['create_volume'] = True
        return target_volume_name

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
        self.want = Parameters()
        self.want.client = self.client
        self.want.update(self.client.module.params)

    def exec_module(self):
        if self.want.remote_src:
            manager = self.get_manager('remote')
        else:
            manager = self.get_manager('local')

        return manager.exec_module()

    def get_manager(self, target):
        if target == 'remote':
            return RemoteManager(self.client)
        if target == 'local':
            return LocalManager(self.client)


class BaseManager(object):
    def __init__(self, client):
        self.client = client
        self.have = None
        self.want = Parameters()
        self.want.client = self.client
        self.want.update(self.client.module.params)
        self.changes = Parameters()

    def exec_module(self):
        changed = False
        result = dict()
        state = self.want.state

        try:
            if state == "activated":
                changed = self.activated()
            elif state == "installed":
                changed = self.installed()
            elif state == "present":
                changed = self.present()
            elif state == "absent":
                changed = self.absent()
        except iControlUnexpectedHTTPError as e:
            raise F5ModuleError(str(e))

        changes = self.changes.to_return()
        result.update(**changes)
        result.update(dict(changed=changed))
        return result

    def _set_changed_options(self):
        changed = {}
        for key in Parameters.returnables:
            if getattr(self.want, key) is not None:
                changed[key] = getattr(self.want, key)
        if changed:
            self.changes = Parameters(changed)

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

    def activated(self):
        if self.is_activated():
            return False
        elif self.is_installed():
            return self.activate()
        else:
            self.install_volume()
            self.wait_for_device_reboot()
            return True

    def is_activated(self):
        volume = self.software_on_volume()
        if not volume:
            return False
        if hasattr(volume, 'active') and volume.active is True:
            return True

    def installed(self):
        if self.is_installed():
            return False
        else:
            self.install_volume()
            return True

    def is_installed(self):
        volume = self.software_on_volume()
        if not volume:
            return False
        if not hasattr(volume, 'active') or volume.active is not True:
            return True

    def activate(self):
        self.have = self.get_current_active()
        self._update_changed_options()
        if self.client.check_mode:
            return True
        self.reboot_volume_on_device()
        self.wait_for_device_reboot()
        return True

    def present(self):
        if self.exists():
            return False
        else:
            self._set_changed_options()
            if self.client.check_mode:
                return True
            self.upload()
            return True

    def absent(self):
        if not self.exists():
            return False
        else:
            if self.client.check_mode:
                return True
            self.remove()
            return True

    def install_volume(self):
        self._set_changed_options()
        if self.client.check_mode:
            return True
        if not self.exists():
            self.upload()
        if self.want.delete_volume:
            self.delete_volume_on_device()
        if not self.want.hotfix:
            self.install_image_on_device()
        else:
            version = self.want.version
            if self.base_image_exists():
                self.install_hotfix_on_device()
            else:
                raise F5ModuleError('Base image of version: {0} must exist to install this hotfix.'.format(version))

        self.wait_for_software_install_on_device()

    def upload(self):
        software_path = self.want.software
        hotfix_path = self.want.hotfix
        image_list = self.list_images_on_device()
        hotfix_list = self.list_hotfixes_on_device()

        if self.want.forced:
            self.remove()

        if software_path and not self.image_exists_on_device():
            if self.want.remote_src:
                self.download_iso_on_device()
            else:
                self.upload_to_device(software_path)
            self.wait_for_images(image_list)

        if hotfix_path and not self.hotfix_exists_on_device():
            if self.want.remote_src:
                self.download_iso_on_device(True)
            else:
                self.upload_to_device(hotfix_path)
            self.wait_for_images(hotfix_list, True)

    def remove(self):
        software_path = self.want.software
        hotfix_path = self.want.hotfix
        image_list = self.list_images_on_device()
        hotfix_list = self.list_hotfixes_on_device()

        if hotfix_path:
            self.delete_hotfix_on_device()
            self.wait_for_images(hotfix_list, True)

        if software_path:
            self.delete_image_on_device()
            self.wait_for_images(image_list)

    def exists(self):
        forced = self.want.forced
        software_path = self.want.software
        hotfix_path = self.want.hotfix

        if forced:
            return False

        if software_path and hotfix_path:
            if self.image_exists_on_device() and self.hotfix_exists_on_device():
                return True
        elif hotfix_path:
            if self.hotfix_exists_on_device():
                return True
        elif software_path:
            if self.image_exists_on_device():
                return True
        else:
            return False

    def base_image_exists(self):
        version = self.want.version
        images = self.list_images_on_device()
        for image in images:
            if image.version == version:
                return True
        else:
            return False

    def _device_reconnect(self):
        self.client.api = self.client._get_mgmt_root('bigip', **self.client._connect_params)

    def wait_for_images(self, count, hotfix=False):
        current = len(count)
        if hotfix:
            while True:
                if len(self.list_hotfixes_on_device()) != current:
                    break
            time.sleep(1)
        else:
            while True:
                if len(self.list_images_on_device()) != current:
                    break
            time.sleep(1)

    def wait_for_device_reboot(self):
        vol = self.want.volume
        while True:
            time.sleep(5)
            try:
                self._device_reconnect()
                volume = self.client.api.tm.sys.software.volumes.volume.load(
                    name=vol
                )
                if hasattr(volume, 'active') and volume.active is True:
                    break
            except Exception:
                # Handle all exceptions because if the system is offline (for a
                # reboot) the REST client will raise exceptions about
                # connections
                pass

    def wait_for_software_install_on_device(self):
        # We need to delay this slightly in case the the volume needs to be
        # created first
        for count in range(10):
            if self.volume_exists_on_device():
                break
            time.sleep(4)
        progress = self.load_volume_on_device()
        while True:
            time.sleep(10)
            progress.refresh()
            status = progress.status
            if 'complete' in status:
                break
            elif 'failed' in status:
                raise F5ModuleError(status)

    def delete_volume_on_device(self):
        volume = self.load_volume_on_device()
        volume.delete()
        for count in range(10):
            time.sleep(5)
            if not self.volume_exists_on_device():
                break

    def get_current_active(self):
        volumes = self.list_volumes_on_device()
        for volume in volumes:
            if hasattr(volume, 'active') and volume.active is True:
                result = volume.attrs
                return Parameters(result)


class LocalManager(BaseManager):
    def software_on_volume(self):
        volumes = self.list_volumes_on_device()
        version = self.want.version
        build = self.want.build
        for volume in volumes:
            if hasattr(volume, 'version') and hasattr(volume, 'build'):
                if volume.version == version and volume.build == build:
                    return volume

    def _has_build_and_version(self, item):
        if item.version != self.want.version:
            return False
        if item.build != self.want.build:
            return False
        return True

    def install_image_on_device(self):
        params = self.want.api_params()
        self.client.api.tm.sys.software.images.exec_cmd(
            'install', name=self.want.software_name, **params
        )

    def install_hotfix_on_device(self):
        params = self.want.api_params()
        self.client.api.tm.sys.software.hotfix_s.exec_cmd(
            'install', name=self.want.hotfix_name, **params
        )

    def upload_to_device(self, filepath):
        self.client.api.cm.autodeploy.software_image_uploads.upload_image(
            filepath
        )

    def list_images_on_device(self):
        images = self.client.api.tm.sys.software.images.get_collection()
        return images

    def list_hotfixes_on_device(self):
        hotfixes = self.client.api.tm.sys.software.hotfix_s.get_collection()
        return hotfixes

    def delete_image_on_device(self):
        img = self.client.api.tm.sys.software.images.image.load(
            name=self.want.software_name)
        img.delete()

    def delete_hotfix_on_device(self):
        hf = self.client.api.tm.sys.software.hotfix_s.hotfix.load(
            name=self.want.hotfix_name)
        hf.delete()

    def list_volumes_on_device(self):
        volumes = self.client.api.tm.sys.software.volumes.get_collection()
        return volumes

    def image_exists_on_device(self):
        images = self.client.api.tm.sys.software.images.get_collection()
        if any(self._has_build_and_version(i) for i in images):
            return True
        return False

    def hotfix_exists_on_device(self):
        hotfixes = self.client.api.tm.sys.software.hotfix_s.get_collection()
        if any(self._has_build_and_version(h) for h in hotfixes):
            return True
        return False

    def load_volume_on_device(self):
        volume = self.client.api.tm.sys.software.volumes.volume.load(
            name=self.want.volume)
        return volume

    def reboot_volume_on_device(self):
        self.client.api.tm.sys.software.volumes.exec_cmd(
            'reboot', volume=self.want.volume
        )

    def volume_exists_on_device(self):
        result = self.client.api.tm.sys.software.volumes.volume.exists(name=self.want.volume)
        return result


class RemoteManager(BaseManager):
    def software_on_volume(self):
        self.check_product_info()
        volumes = self.list_volumes_on_device()
        version = self.want.version
        build = self.want.build
        for volume in volumes:
            if hasattr(volume, 'version') and hasattr(volume, 'build'):
                if volume.version == version and volume.build == build:
                    return volume

    def check_product_info(self):
        hotfix = self.want.hotfix
        version = self.want.version
        build = self.want.build
        state = self.want.state

        if state in ['installed', 'activated']:
            if version is None or build is None:
                if hotfix:
                    self.set_product_info(True)
                else:
                    self.set_product_info()
            return False

        elif state in ['present', 'absent']:
            if version is None or build is None:
                return True
            else:
                return False

    def set_product_info(self, hotfix=False):
        # We attempt to use filename when version or build is missing
        if hotfix:
            info = self.load_hotfix_by_name_from_device()
        else:
            info = self.load_image_by_name_from_device()

        if info is None:
            raise F5ModuleError('Unable to set ISO information based on ISO name, please specify version and build.')

        self.want.version = info.version
        self.want.build = info.build

    def prepare_command(self, url, name):
        # We will add file download resume, multiple file download,
        # ftp/ftps in next iterations. We need to test this simple solution first
        secure = self.want.secure
        if secure:
            cmd = '-c "curl {0} -k -o /shared/images/{1}"'.format(url, name)
        else:
            cmd = '-c "curl {0} -o /shared/images/{1}"'.format(url, name)
        return cmd

    def name_match(self, url, name, hotfix=False):
        # To ensure that the ISO name matches the one in MD5 sum file,
        # If not we will change it so the ISO is saved with proper name for
        # MD5 sum checks to pass
        cmd = self.prepare_command(url, name)
        self.run_command_on_device(cmd)
        cat = '-c "cat /shared/images/{0}"'.format(name)
        output = self.run_command_on_device(cat)
        result = output.commandResult
        tmp_name = str(result.rsplit()[1])
        if hotfix:
            if tmp_name != self.want.hotfix_name:
                self.want.hotfix_name = tmp_name
            return self.want.hotfix_name
        else:
            if tmp_name != self.want.software_name:
                self.want.software_name = tmp_name
            return self.want.software_name

    def does_checksum_match(self, md5name, filename):
        cmd = '-c "cd /shared/images; md5sum -c /shared/images/{0}"'.format(
            md5name
        )
        output = self.run_command_on_device(cmd)
        result = str(output.commandResult).rstrip()
        expected = "{0}: OK".format(filename)
        if result == expected:
            return True
        else:
            return False

    def download_iso_on_device(self, hotfix=False):
        if hotfix:
            md5name = self.want.hfmd5_name
            md5_url = self.want.hotfix_md5sum
            name = self.name_match(md5_url, md5name, True)
            url = self.want.hotfix
            cmd = self.prepare_command(url, name)
            self.run_command_on_device(cmd)
            if not self.does_checksum_match(md5name, name):
                raise F5ModuleError('ISO download failed from remote host.')
        else:
            md5name = self.want.imgmd5_name
            md5_url = self.want.software_md5sum
            name = self.name_match(md5_url, md5name)
            url = self.want.software
            cmd = self.prepare_command(url, name)
            self.run_command_on_device(cmd)
            if not self.does_checksum_match(md5name, name):
                raise F5ModuleError('ISO download failed from remote host.')

    def name_check(self, name, hotfix=False):
        if hotfix:
            if name != self.want.hotfix_name:
                self.want.hotfix_name = name
        else:
            if name != self.want.software_name:
                self.want.software_name = name

    def load_image_by_name_from_device(self):
        result = None
        exists = self.image_exists_by_name_on_device()

        if exists:
            result = self.client.api.tm.sys.software.images.image.load(
                name=self.want.software_name
            )
        return result

    def load_hotfix_by_name_from_device(self):
        result = None
        exists = self.hotfix_exists_by_name_on_device()

        if exists:
            result = self.client.api.tm.sys.software.hotfix_s.hotfix.load(
                name=self.want.hotfix_name
            )
        return result

    def install_image_on_device(self):
        params = self.want.api_params()
        self.client.api.tm.sys.software.images.exec_cmd(
            'install', name=self.want.software_name, **params
        )

    def install_hotfix_on_device(self):
        params = self.want.api_params()
        self.client.api.tm.sys.software.hotfix_s.exec_cmd(
            'install', name=self.want.hotfix_name, **params
        )

    def list_images_on_device(self):
        images = self.client.api.tm.sys.software.images.get_collection()
        return images

    def list_hotfixes_on_device(self):
        hotfixes = self.client.api.tm.sys.software.hotfix_s.get_collection()
        return hotfixes

    def delete_image_on_device(self):
        img = self.client.api.tm.sys.software.images.image.load(
            name=self.want.software_name)
        img.delete()

    def delete_hotfix_on_device(self):
        hf = self.client.api.tm.sys.software.hotfix_s.hotfix.load(
            name=self.want.hotfix_name)
        hf.delete()

    def list_volumes_on_device(self):
        volumes = self.client.api.tm.sys.software.volumes.get_collection()
        return volumes

    def run_command_on_device(self, cmd):
        result = self.client.api.tm.util.bash.exec_cmd('run', utilCmdArgs=cmd)
        if result:
            return result
        else:
            raise F5ModuleError('Could not execute command. Most likely device is unresponsive.')

    def image_exists_on_device(self):
        if self.check_product_info():
            return self.image_exists_by_name_on_device()
        images = self.list_images_on_device()
        for image in images:
            if image.version == self.want.version:
                self.name_check(image.name)
                return True
        return False

    def hotfix_exists_on_device(self):
        if self.check_product_info():
            return self.hotfix_exists_by_name_on_device()
        hotfixes = self.list_hotfixes_on_device()
        for hotfix in hotfixes:
            if hotfix.version == self.want.version:
                if hotfix.build == self.want.build:
                    self.name_check(hotfix.name, True)
                    return True
        return False

    def hotfix_exists_by_name_on_device(self):
        result = self.client.api.tm.sys.software.hotfix_s.hotfix.exists(name=self.want.hotfix_name)
        return result

    def image_exists_by_name_on_device(self):
        result = self.client.api.tm.sys.software.images.image.exists(name=self.want.software_name)
        return result

    def load_volume_on_device(self):
        volume = self.client.api.tm.sys.software.volumes.volume.load(
            name=self.want.volume)
        return volume

    def reboot_volume_on_device(self):
        self.client.api.tm.sys.software.volumes.exec_cmd(
            'reboot', volume=self.want.volume
        )

    def volume_exists_on_device(self):
        result = self.client.api.tm.sys.software.volumes.volume.exists(name=self.want.volume)
        return result


class ArgumentSpec(object):
    def __init__(self):
        self.states = ['absent', 'activated', 'installed', 'present']
        self.supports_check_mode = True
        self.argument_spec = dict(
            state=dict(
                default='activated',
                choices=self.states
            ),
            force=dict(
                type='bool',
                default='no'
            ),
            hotfix=dict(
                aliases=['hotfix_image'],
            ),
            software=dict(
                aliases=['base_image']
            ),
            reuse_inactive_volume=dict(
                type='bool',
                default='no'
            ),
            remote_src=dict(
                type='bool',
                default='no'
            ),
            volume=dict(),
            software_md5sum=dict(),
            hotfix_md5sum=dict(),
            version=dict(),
            build=dict()
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
