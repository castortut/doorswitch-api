Fridge API
==========

A service that listens to updates on an MQTT message broker from the fridge-mounted switch panel.
Serves both raw switch state information and a dictionary with product labels attached. 

The purpose is to let people who consume products from the fridge to flip a switch when something
runs out. The information can then be used as a simple shopping list. It can be consumed by web applications,
Telegram bots, etc.

Requires Python 3.6+, flask and flask_mqtt
