# simple_pub.py
import zmq
import time
from threading import Thread

host = "*"
port = "5001"

# Creates a socket instance
context = zmq.Context()

username = input("Enter your username: \n")

def on_publish_tweet():
	socket_pub = context.socket(zmq.PUB)
	socket_pub.bind("tcp://{}:{}".format(host, port))
	time.sleep(1)

	while True:
		tweet = input("Enter your Tweet: \n")
		socket_pub.send_string("username", flags=zmq.SNDMORE)
		socket_pub.send_json({"tweet": f"{tweet}"})

def on_receive_tweet():
	socket_sub = context.socket(zmq.SUB)
	socket_sub.connect("tcp://{}:{}".format(host, port))
	socket_sub.subscribe("username")

	while True:
		username = socket_sub.recv_string()
		message = socket_sub.recv_json()
		print(f"User: {username}. Tweet: {message['tweet']}")

publisher = Thread(target=on_publish_tweet)
subscriber = Thread(target=on_receive_tweet)

publisher.start()
subscriber.start()
