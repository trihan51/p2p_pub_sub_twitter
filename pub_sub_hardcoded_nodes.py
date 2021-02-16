# simple_pub.py

import socket

import zmq
import time
from threading import Thread

host = "*"
port = "5001"
# for testing with 1 node, use these for rcv
localhost = "localhost"
rcv_port =  "5002"

ip_name_map = {
  "172.31.28.101": "manny",
  "172.31.24.25": "moe",
  "172.31.21.186": "jack",
  "127.0.1.1": "tony",
}


# Creates a socket instance
context = zmq.Context()

def get_my_username():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    username = ip_name_map.get(local_ip)
    #print("get_my_username: username: {} ip address: {}".format(username, local_ip))
    return username

def get_my_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    #print("get_my_username: username: {} ip address: {}".format(username, local_ip))
    return local_ip

def lookup_ip_from_name(name):
    for key, value in ip_name_map.items():
        if value == name:
            return key
    print("Error! lookup_ip_from_name for {} no ip found!".format(name))
    return ""

def on_publish_tweet():
    username = get_my_username()
    socket_pub = context.socket(zmq.PUB)
    socket_pub.bind("tcp://{}:{}".format(host, port))
    time.sleep(1)

    while True:
        tweet = input("Enter your Tweet: \n")
        socket_pub.send_string("username", flags=zmq.SNDMORE)
        socket_pub.send_json({"tweet": f"{tweet}"})

def on_receive_tweet():
    username = get_my_username()
    if username != "manny":
        pub_username = "manny"
    else:
        pub_username = "moe"
    pub_ip = lookup_ip_from_name(pub_username)

    print("Connecting to {} on {}".format(pub_username, pub_ip))
    socket_sub = context.socket(zmq.SUB)
    socket_sub.connect("tcp://{}:{}".format(pub_ip, port))
    #socket_sub.connect("tcp://{}:{}".format(localhost, rcv_port))
    socket_sub.subscribe("username")

    while True:
        username = socket_sub.recv_string()
        message = socket_sub.recv_json()
        print(f"User: {username}. Tweet: {message['tweet']}")


#username = input("Enter your username: \n")
username = get_my_username()

publisher = Thread(target=on_publish_tweet)
subscriber = Thread(target=on_receive_tweet)

publisher.start()
subscriber.start()