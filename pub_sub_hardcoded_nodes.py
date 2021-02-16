# simple_pub.py

import socket

import zmq
import time
from threading import Thread

host = "*"
port = "5001"
# for testing with 1 node, use these for rcv
localhost = "localhost"
rcv_port =  "5001"

ip_name_map = {
  "172.31.28.101": "manny",
  "172.31.24.25": "moe",
  "172.31.21.186": "jack",
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
        socket_pub.send_string(username, flags=zmq.SNDMORE)
        socket_pub.send_json({"tweet": f"{tweet}"})

def on_receive_tweet():
    my_username = get_my_username()

    socket_sub = context.socket(zmq.SUB)
    for ip, name in ip_name_map.items():
        if name != my_username:
            print("Connecting to {} on {}".format(name, ip))
            socket_sub.connect("tcp://{}:{}".format(ip, port))
            socket_sub.subscribe(name)

    while True:
        username = socket_sub.recv_string()
        message = socket_sub.recv_json()
        print(f"User: {username}. Tweet: {message['tweet']}")


username = get_my_username()

publisher = Thread(target=on_publish_tweet)
subscriber = Thread(target=on_receive_tweet)

publisher.start()
subscriber.start()
