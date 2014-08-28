from _cffi import *

def zyre_version():
    major, minor, patch  = new_int(), new_int(), new_int()
    zyre_lib.zyre_version(major, minor, patch)
    return (major[0], minor[0], patch[0])

class ZyreException(Exception):
    def __init__(self, error):
        self._error = error

    def __repr__(self):
        return 'ZyreException("{}")'.format(self._error)

    def __str__(self):
        return 'ZyreError: {}'.format(self._error)

class ZyreEvent(object):
    def __init__(self, zyre_event_t):
        self._z_event = zyre_event_t

    def __del__(self):
        zyre_lib.zyre_event_destroy(ffi.new('zyre_event_t**', self._z_event))

    @property
    def sender(self):
        return ffi.string(zyre_lib.zyre_event_sender(self._z_event))

    @property
    def name(self):
        return ffi.string(zyre_lib.zyre_event_name(self._z_event))

    @property
    def address(self):
        return ffi.string(zyre_lib.zyre_event_address(self._z_event))

    @property
    def group(self):
        return ffi.string(zyre_lib.zyre_event_group(self._z_event))

class ZyreNode(object):
    def __init__(self, name = '', verbose=False):
        self._z_node = zyre_lib.zyre_new(name)
        if (verbose):
            zyre_lib.zyre_set_verbose(self._z_node)
        self.groups = set()

        self._port = 5670 # default port
        self._interface = ''

    def __del__(self):
        self.stop()
        zyre_lib.zyre_destroy(ffi.new('zyre_t**',self._z_node))

    @property
    def name(self):
        return ffi.string(zyre_lib.zyre_name(self._z_node))

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        zyre_lib.zyre_set_port(self._z_node, value)

    @property
    def uuid(self):
        return ffi.string(zyre_lib.zyre_uuid(self._z_node))

    @property
    def interface(self):
        return ffi.string(czmq_lib.zsys_interface())

    @interface.setter
    def interface(self, value):
        zyre_lib.zyre_set_interface(self._z_node, value)

    def set_header(self, name, value):
        zyre_lib.zyre_set_header(self._z_node, name, value)

    def set_interval(self, value):
        zyre_lib.zyre_set_interval(self._z_node, value)

    def start(self):
        if zyre_lib.zyre_start(self._z_node) == 1:
            raise ZyreNode('Failed to start beacon')

    def stop(self):
        zyre_lib.zyre_stop(self._z_node)

    def join(self, group):
        zyre_lib.zyre_join(self._z_node, group)
        self.groups.add(group)

    def leave(self, group):
        zyre_lib.zyre_leave(self._z_node, group)
        self.groups.remove(group)

    def whispers(self, peer, msg_string):
        zyre_lib.zyre_whispers(self._z_node, peer, msg_string)

    def shouts(self, group, msg_string):
        zyre_lib.zyre_shouts(self._z_node, group, msg_string)

    def dump(self):
        zyre_lib.zyre_dump(self._z_node)

