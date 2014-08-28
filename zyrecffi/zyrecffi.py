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
        return 'ZyreException: {}'.format(self._error)

class ZyreEvent(object):

    ZYRE_EVENT_ENTER    = zyre_lib.ZYRE_EVENT_ENTER
    ZYRE_EVENT_JOIN     = zyre_lib.ZYRE_EVENT_JOIN
    ZYRE_EVENT_LEAVE    = zyre_lib.ZYRE_EVENT_LEAVE
    ZYRE_EVENT_EXIT     = zyre_lib.ZYRE_EVENT_EXIT
    ZYRE_EVENT_WHISPER  = zyre_lib.ZYRE_EVENT_WHISPER
    ZYRE_EVENT_SHOUT    = zyre_lib.ZYRE_EVENT_SHOUT

    def __init__(self, zyre_event_t):
        self._z_event = zyre_event_t

    def __del__(self):
        zyre_lib.zyre_event_destroy(ffi.new('zyre_event_t**', self._z_event))

    def __repr__(self):
        return 'ZyreEvent({})'.format(self._z_event)

    def __str__(self):
        return 'ZyreEvent: {} {} {} {} {}'.format(self.type_string,
                                                  self.name,
                                                  self.group,
                                                  self.sender,
                                                  self.address)

    @property
    def sender(self):
        z_sender = zyre_lib.zyre_event_sender(self._z_event)
        return c_string_to_py(z_sender)

    @property
    def name(self):
        z_name = zyre_lib.zyre_event_name(self._z_event)
        return c_string_to_py(z_name)

    @property
    def address(self):
        z_address = zyre_lib.zyre_event_address(self._z_event)
        return c_string_to_py(z_address)

    @property
    def group(self):
        z_group = zyre_lib.zyre_event_group(self._z_event)
        return c_string_to_py(z_group)

    @property
    def type(self):
        return zyre_lib.zyre_event_type(self._z_event)

    @property
    def type_string(self):
        return self._event_type_string(self.type)

    def _event_type_string(self, event_type):
        for key, value in self.__class__.__dict__.items():
            if key.find('ZYRE_EVENT_') > -1 and value == int(event_type):
                return key

    def header(self, name):
        z_header = zyre_lib.zyre_event_header(self._z_event, name)
        return c_string_to_py(z_header)

    def _zmsg(self):
        return check_null(zyre_lib.zyre_event_msg(self._z_event))

    @property
    def msg_string(self):
        zmsg = self._zmsg()
        if (zmsg):
            return c_string_to_py(czmq_lib.zmsg_popstr(zmsg))
        return None


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

    def set_endpoint(self, endpoint):
        ret = zyre_lib.zyre_set_endpoint(self._z_node, endpoint)

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
        if not isinstance(msg_string, str):
            raise ZyreException('{} is not a string'.format(msg_string))
        zyre_lib.zyre_shouts(self._z_node, group, msg_string)

    def dump(self):
        zyre_lib.zyre_dump(self._z_node)

    def recv_event(self):
        zyre_event = zyre_lib.zyre_event_new(self._z_node)
        return ZyreEvent(zyre_event)

    def _zsock(self):
        return zyre_lib.zyre_socket(self._z_node)

    def socket_fd(self):
        return czmq_lib.zsock_fd(self._zsock())
