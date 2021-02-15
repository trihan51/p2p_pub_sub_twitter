# simple_pub.py
import zmq
import time
from threading import Thread

host = "*"
local_host = "localhost"
port_1 = "5001"
port_2 = "5002"

context = zmq.Context()

# Getting user specified information
username = input("Enter your username: \n")

# Starting Publisher
def on_publish_tweet():
	socket_pub = context.socket(zmq.PUB)
	socket_pub.bind("tcp://{}:{}".format(host, port_2))
	time.sleep(1)

	while True:
		tweet = input("Enter your Tweet: \n")
		socket_pub.send_string("username", flags=zmq.SNDMORE)
		socket_pub.send_json({"tweet": f"{tweet}"})

publisher = Thread(target=on_publish_tweet)
publisher.start()

# Starting Subscribers
def on_receive_tweet():
	socket_sub = context.socket(zmq.SUB)
	socket_sub.connect("tcp://{}:{}".format(local_host, port_1))
	socket_sub.subscribe("username")

	while True:
		username = socket_sub.recv_string()
		message = socket_sub.recv_json()
		print(f"User: {username}. Tweet: {message['tweet']}")

subscriber = Thread(target=on_receive_tweet)
subscriber.start()
