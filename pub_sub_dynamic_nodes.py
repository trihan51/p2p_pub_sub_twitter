# simple_pub.py

import socket
import sys

import zmq
import time
from threading import Thread
import ipaddress

######################### Global Variables #########################
host = "*"
port = "5001"
# for testing with 1 node, use these for rcv
localhost = "localhost"
rcv_port =  "5001"

# we will create a connection to all of these addresses
base_ip_address = "172.31.21.1" # FIXME, needs to match actual AWS range!
ip_mask = "20" # FIXME, needs to match actual AWS range!

# This is primarily only used to hold our own ip and user name
ip_name_map = {

}

# mutable set to ensure no duplicates
subscriptions_set = set()


# Creates a socket instance
context = zmq.Context()

socket_pub = None
socket_sub = None

######################### Init Functions #########################
def init_publisher():
    global socket_pub
    username = get_my_username()
    socket_pub = context.socket(zmq.PUB)
    socket_pub.bind("tcp://{}:{}".format(host, port))
    time.sleep(1)


"""
   Lacking a discovery service, open a connection to all
   ip addresses in the space. 
   
   Subscription add/remove are independent of publisher names.
"""
def connect_hosts():
    global socket_sub
    socket_sub = context.socket(zmq.SUB)

    # iterate the entire range of ip addresses
    ip_list = [str(ip) for ip in ipaddress.IPv4Network('{}/{}'.format(base_ip_address, ip_mask), False).hosts()]
    print("Connecting IP's in range: {} to {}".format(ip_list[0], ip_list[-1]))

    my_ip = get_my_ip()
    #for ip in host_ip_list:
    for ip in ip_list:
        if ip != my_ip:
            #print("Connecting to host {}".format(ip))
            socket_sub.connect("tcp://{}:{}".format(ip, port))

######################### Helper Functions #########################
def get_my_username():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    username = ip_name_map.get(local_ip)
    return username

def get_my_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
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
        print(f"\n  User: {username}. Tweet: {message['tweet']}")

def set_username():
    my_ip = get_my_ip()
    old_username = ip_name_map.get(my_ip)
    prompt = "  Please enter an initial username for tweets: "

    if old_username:
        print("Current username: {}".format(old_username))
        prompt = "  Enter a new username: "

    username = input(prompt)
    if username:
        ip_name_map[get_my_ip()] = username
    else:
        print(" username not changed!")

def subscribe():
    global socket_sub
    username = input("Enter username to subscribe: ")
    if username:
        subscriptions_set.add(username)
        socket_sub.subscribe(username)
        print(" Subscribed to user {}".format(username))
    else:
        print(" Invalid  input, no subscription change made")

def unsubscribe():
    global socket_sub
    username = input("Enter username to unsubscribe: ")
    if username:
        if username in subscriptions_set:
            subscriptions_set.remove(username)
            socket_sub.unsubscribe(username)
            print(" Unscribed to user {}".format(username))
        else:
            print(" You were not subscribed, to {}, no subscription change made".format(username))
    else:
        print(" Invalid  input, no subscription change made")
        

def list_subscriptions():
    print("Your subscriptions: ")
    for sub in subscriptions_set:
        print("     {}".format(sub))

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
    connect_hosts()
    subscriber = Thread(target=on_receive_tweet)
    subscriber.start()

    set_username()

    # Print Menu and Process User Input
    print_options()
    while True: 
        selected_option = input("Please select a numbered option: ")
        if selected_option == "1":                  # 1. Subscribe
            subscribe()
        elif selected_option == "2":                # 2. Unsubscribe
            unsubscribe()
        elif selected_option == "3":                # 3. List your subscriptions
            list_subscriptions()
        elif selected_option == "4":                # 4. Update username
            set_username()
        elif selected_option == "5":                # 5. Tweet
            on_publish_tweet()
        elif selected_option == "6":
            print_options()
        elif selected_option == "7":
            sys.exit()
        else:
            print("Invalid option selected")

if __name__ == '__main__':
    main()
