
from pyre import Pyre 
from pyre import zhelper

import zmq 
import uuid
import logging
import sys
import json

import socket

""" An object of this class will run a discovery service for publisher nodes.

    Each node will just broadcast it's current name and ip at regular intervals,
    The service monitor and keep updated the node doctionary of active nodes.

    The node list is of the format ip: name.
    
    ip addresses are removed from the active list after a given time.
    
    subscribers will active ip's open for those which they have subscribed to the
    publisher. This may be multiple ips because a publisher may be using multiple
    devices.

    For now we ignore name autentication completely, but in a real implementation,
    a publisher name must be authenticated before it can join.
"""
class Discovery:

    def __init__(self, my_name, my_ip, group_name):

        self.name = my_name
        self.ip = my_ip
        self.group = group_name

        # node dict is of the format ip: name
        # This is because a user (name) may move to a new ip.
        # Duplicate ip's are not allowed, but more than 1 ip may share the 
        # same name. This is because a user may log in to multiple devices.
        # 
 
        self.node_dict = {}

        self.node = Pyre(self.group)
        self.node.set_header(self.name, self.ip)
        self.node.join(self.group)
        self.node.start()

        # this runs forever for testing, but should be run as a thread
        self._node_update_task()

    """ This task will keep the node dictionary updated.

        The node will periodically send an update (heartbeat) control message
        which has the name and ip as in the header.

        Periodically recieve the incomming messages and update the ip name dictionary
    """
    def _node_update_task(self):
        while True:
            cmds = self.node.recv()
            msg_type = cmds.pop(0)

            # debug prints
            print("NODE_MSG TYPE: %s" % msg_type)
            print("NODE_MSG PEER: %s" % uuid.UUID(bytes=cmds.pop(0)))
            print("NODE_MSG NAME: %s" % cmds.pop(0))

            # headers are packed json
            if msg_type.decode('utf-8') == "SHOUT":
                print("NODE_MSG GROUP: %s" % cmds.pop(0))
            elif msg_type.decode('utf-8') == "ENTER":
                headers = json.loads(cmds.pop(0).decode('utf-8'))
                print("NODE_MSG HEADERS: %s" % headers)
                for key in headers:
                    print("key = {0}, value = {1}".format(key, headers[key]))
            print("NODE_MSG CONT: %s" % cmds)


    """
     Get the currwnt nodes dict
     ip, name, group
    """
    def get_active_nodes(self):

        # return the active nodes dictionary
        return self.node_dict

    def get_idle_nodes(self):
        return self.node_dict

# for testing onlym as a stand-alone program
if __name__ == '__main__':
    # Create a StreamHandler for debugging
    logger = logging.getLogger("pyre")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.propagate = False

    def get_my_ip():
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        #print("get_my_username: username: {} ip address: {}".format(username, local_ip))
        return local_ip

    # get ip address, and name

    my_ip = get_my_ip()
    discovery = Discovery(my_ip, "tony", "pub_group")
