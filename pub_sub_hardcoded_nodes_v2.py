# simple_pub.py

import socket
import sys

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

######################### Global Variables #########################
socket_pub = None
socket_sub = None

######################### Init Functions #########################
def init_publisher():
    global socket_pub
    username = get_my_username()
    socket_pub = context.socket(zmq.PUB)
    socket_pub.bind("tcp://{}:{}".format(host, port))
    time.sleep(1)

def init_subscribers():
    global socket_sub
    my_username = get_my_username()
    socket_sub = context.socket(zmq.SUB)
    for ip, name in ip_name_map.items():
        if name != my_username:
            print("Connecting to {} on {}".format(name, ip))
            socket_sub.connect("tcp://{}:{}".format(ip, port))
            socket_sub.subscribe(name)

######################### Helper Functions #########################
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
    global socket_pub
    username = get_my_username()
    tweet = input("Enter your Tweet: \n")
    socket_pub.send_string(username, flags=zmq.SNDMORE)
    socket_pub.send_json({"tweet": f"{tweet}"})

def on_receive_tweet():
    global socket_sub
    while True:
        username = socket_sub.recv_string()
        message = socket_sub.recv_json()
        print(f"User: {username}. Tweet: {message['tweet']}")

def print_options():
    print("--------------------")
    print("Menu of Options")
    print("--------------------")
    print("1. Subscribe")
    print("2. Unsubscribe")
    print("3. List your subscriptions")
    print("4. Update username")
    print("5. Tweet")
    print("6. print menu")
    print("7. Shutdown")

######################### Main #########################
def main():
    global socket_pub
    global socket_sub

    # initialize the publisher and subscribers
    init_publisher()
    init_subscribers()
    subscriber = Thread(target=on_receive_tweet)
    subscriber.start()

    # Print Menu and Process User Input
    print_options()
    while True: 
        selected_option = input("Please select a numbered option: ")
        if selected_option == "1":
            username = Input("Enter username: ")
            socket_sub.subscribe(username)
        elif selected_option == "2":
            username = Input("Enter username: ")
            socket_sub.unsubscribe(username)
        elif selected_option == "3":
            print("3")
        elif selected_option == "4":
            username = Input("Enter new username: ")
            ip_name_map[get_my_ip()] = username
        elif selected_option == "5":
            on_publish_tweet()
        elif selected_option == "6":
            print_options()
        elif selected_option == "7":
            sys.exit()
        else:
            print("Invalid option selected")

if __name__ == '__main__':
    main()
