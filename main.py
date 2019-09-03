import datetime
import json
import os

from flask import Flask, request
from flask_mqtt import Mqtt

########
# Conf #
########

HISTORY_LENGTH = 10

MQTT_URL = os.environ.get("MQTT_URL", "mqtt.svc.cave.avaruuskerho.fi")

############
# Conf end #
############

LOG_LEVELS = {
    1: "INFO",
    2: "NOTICE",
    4: "WARNING",
    8: "ERROR",
    16: "DEBUG"
}

# Dictionary that the activity gets stored in
activity = {}

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = MQTT_URL
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
app.config['MQTT_USERNAME'] = None  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = None  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes

mqtt = Mqtt(app)

global state
state = {
    "updated": "",
    "switches": [],
}


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc) -> None:
    """
    Handle an event when the MQTT connection is made. Subscribe to topic in this event so that
    if the connection is lost and reconnects, the subscriptions get made again
    """
    print("Connected to MQTT")

    # Subscribe to all topics that begin with '/iot/cave/fridgeSwitch0/'
    mqtt.subscribe('/iot/cave/fridgeSwitch0/*')


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message) -> None:
    """
    Handle an event where a message is published to one of the topics we are subscribed to.
    Since we're (only) subscribed to the motion events, this means that motion has been registered somewhere.

    :param message: An object containing information (including the topic and the payload) of the message
    """

    # The last part of the topic is the sensor ID, like /iot/cave/motion0/123456
    id = message.topic.split('/')[-1]
    print("Received an update from switch {}".format(id))

    switches = []

    for bit in message.payload.decode():
        if bit == '1':
            switches.append(False)
        else:
            switches.append(True)

    global state
    state['switches'] = switches
    state['updated'] = datetime.datetime.now().timestamp()


@mqtt.on_log()
def handle_logging(client, userdata, level, buf) -> None:
    """
    Handle an event where the MQTT library wants to log a message. Ignore any DEBUG-level messages

    :param level: The level/severity of the message
    :param buf: Message contents
    """
    if LOG_LEVELS[level] != 'DEBUG':
        print(f"{LOG_LEVELS[level]}: {buf}")


@app.route("/")
def get_activity():
    """
    A Flask route that responds to requests on the URL '/'. Builds an JSON object from the stored data.
    """

    global state
    return json.dumps(state)


if __name__ == '__main__':
    # Finally start the app
    app.run(host='0.0.0.0')
