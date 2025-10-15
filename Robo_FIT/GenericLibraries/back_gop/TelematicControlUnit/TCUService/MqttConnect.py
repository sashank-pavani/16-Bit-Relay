import time
import os
import queue
import paho.mqtt.client as mqtt
import logging

message_count = 0
message_count2 = 0
verbose = True
log_data_flag = False
display = True
last_message = dict()


class MqttConnect:
    _broker = ""
    _port = ""
    _user_id = ""
    _user_password = ""
    _topic_ack = []
    _MSG_TYPE_CONNACK = "CONNACK"
    _MSG_TYPE_DISCONNECT = "DISCONNECT"
    _MSG_TYPE_SUBACK = "SUBACK"
    _MSG_TYPE_PUBACK = "PUBACK"
    _MSG_TYPE_CHKSUBS = "CHECKSUBS"
    _MSG_TYPE_UNSUBACK = "UNSUBACK"
    _message_q = queue.Queue()

    def __init__(self, broker, port=1883, user_id="", user_pass=""):
        """
        MqqtConnect class Constructor
        :param broker: IP address of your Broker.
        :param port: port number in which broker listening, (Default=1883)
        :param user_id: (Optional), User ID for login
        :param user_pass: (Optional), User password for login
        """
        MqttConnect._broker = broker
        MqttConnect._port = port
        MqttConnect._user_id = user_id
        MqttConnect._user_password = user_pass

        # Config Python logging module to get the logs and save to the File
        log_file_name = os.path.join(os.getcwd(), "log.txt")
        logging.basicConfig(filename=log_file_name,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

    def get_message_queue(self):
        """
        This method provide the server message in the form of queue
        :return: Message Queue
        """
        return MqttConnect._message_q

    def get_message_count(self):
        """
        Total number of message comes form server
        :return: Message count
        """
        return message_count

    def get_displayed_message_count(self):
        """
        Total number of displayed Message
        :return: Displayed Message
        """
        return message_count2

    def has_changed(self, topic, m_rxd):
        """
        This method check if the message is change for given topic, and create the dictionary of that messages.
        :param topic: Name of the topic which user subscribe
        :param m_rxd: Message return form the broker
        :return: 0 if new message arrived
                1 if no message is change for given topic
        """
        global last_message
        if topic not in last_message:
            last_message[topic] = m_rxd
            return 0
        else:
            if last_message[topic] == m_rxd:  # no change
                return 1
            else:
                last_message[topic] = m_rxd  # set last message
                return 0  # return 0 to output

    def _on_connect(self, client, user_data, flag, rc):
        """
        This is a callback function which check the user connected to the server or not.
        :param client: the client instance for this callback
        :param user_data: the private user data as set in Client() or userdata_set()
        :param flag: response flags sent by the broker
        :param rc: return code,  the connection result

        Connection Return Codes
        0: Connection successful
        1: Connection refused – incorrect protocol version
        2: Connection refused – invalid client identifier
        3: Connection refused – server unavailable
        4: Connection refused – bad username or password
        5: Connection refused – not authorised
        6-255: Currently unused.
        """
        if rc == 0:
            client.connected_flag = True
            logging.info("Successfully Connected...!!!")
        elif rc == 1:
            logging.info("Connection refused - incorrect protocol version")
            client.bad_connection_flag = True
        elif rc == 2:
            logging.info("Connection refused - invalid client identifier")
            client.bad_connection_flag = True
        elif rc == 3:
            logging.info("Connection refused - server unavailable")
            client.bad_connection_flag = True
        elif rc == 4:
            logging.info("Connection refused - bad username or password")
            client.bad_connection_flag = True
        elif rc == 5:
            logging.info("Connection refused - not authorised")
            client.bad_connection_flag = True
        else:
            logging.info("There is an error to connect to the server...!!!")
            client.bad_connection_flag = True

    def _on_disconnect(self, client, user_data, rc=0):
        """
        This is a callback function, which called when user disconnect from the server
        :param client: the client instance for this callback
        :param user_data: the private user data as set in Client() or userdata_set()
        :param rc: return code, the connection result, (Default value 0)
        """
        logging.info("Disconnected flags" + "result code" + str(rc) + "client_id ")
        client.connected_flag = False
        client.disconnect_flag = True

    def _on_log(self, client, user_data, level, buf):
        """
        This is a callback function for getting the server logs.
        All the server INFO logs given by this method
        :param client: the client instance for this callback
        :param user_data: the private user data as set in Client() or userdata_set()
        :param level: gives the severity of the message and will be one of
                    MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING,
                    MQTT_LOG_ERR, and MQTT_LOG_DEBUG.
        :param buf: the message itself
        """
        logging.info("log: " + buf)
        log_file_name = os.path.join(os.getcwd(), "log.txt")

        # on_log() is a call back function so its important to open your file into 'Append Mode'
        log_file = open(log_file_name, "a")
        log_file.write(str(buf) + "\n")

    def _on_publish(self, client, userdata, mid):
        """
        The mid variable matches the mid variable returned from the
        corresponding publish() call, to allow outgoing messages to be tracked.
        This callback is important because even if the publish() call returns
        success, it does not always mean that the message has been sent.
        :param client: the client instance for this callback
        :param userdata: the private user data as set in Client() or userdata_set()
        :param mid: matches the mid variable returned from the corresponding
                    publish() call, to allow outgoing messages to be tracked.
        """
        logging.info("In on_pub callback mid= " + str(mid))
        client.puback_flag = True

    def mqtt_subscribe_topics(self, client, topics):
        """
        This method is used for tracking that given topics are subscribed or not
        :param client: the client instance for this callback
        :param topics: list of topics, user want to subscribe.
        :return: -1 if any error/exception occurs for subscribing the topic
                otherwise append the MqttConnect._topic_ack list.
        """

        for t in topics:
            try:
                logging.info("subscribing " + str(topics))
                logging.info("Topics is : %s" % str(t))
                r = client.subscribe(t)
                # r is mid value
                if r[0] != 0:
                    logging.info("error on subscribing " + str(r))
                    return -1
                logging.info("subscribed to topics return code" + str(r))
            except Exception as e:
                logging.info("error on subscribe" + str(e))
                return -1
            # t -> Topic
            # r -> Mid value
            # 0 is Flag, topic ack
            logging.info("Unsubscribe value ", [t[0], r[1], 0])
            MqttConnect._topic_ack.append([t[0], r[1], 0])

    def mqqt_unsubscribe_topic(self, client, topics):
        for t in topics:
            try:
                logging.info("Unsubscribing " + str(topics))
                logging.info("Topics is : %s" % str(t))
                r = client.unsubscribe(t)
                # r is mid value
                if r[0] != 0:
                    logging.info("error on unsubscribing " + str(r))
                    return -1
                logging.info("unsubscribed to topics return code" + str(r))
            except Exception as e:
                logging.info("error on unsubscribe" + str(e))
                return -1
            # t -> Topic
            # r -> Mid value
            # 0 is Flag, topic ack
            MqttConnect._topic_ack.append([t[0], r[1], 0])

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """
        This is a callback function used to subscribe the topic.
        :param client: the client instance for this callback
        :param userdata: the private user data as set in Client() or userdata_set()
        :param mid: matches the mid variable returned from the corresponding
                        subscribe() call.
        :param granted_qos: list of integers that give the QoS level the broker has
                        granted for each of the different subscription requests.
        """
        logging.info("in on subscribe callback result " + str(mid))
        for t in MqttConnect._topic_ack:
            if t[1] == mid:
                t[2] = 1  # acknowledged
                logging.info("subscription acknowledged  " + t[0])
                client.suback_flag = True

    def _on_unsubscribe(self, client, userdata, mid):
        logging.info("in on unsubscribe callback result " + str(mid))
        for t in MqttConnect._topic_ack:
            if t[1] == mid:
                t[2] = 1  # acknowledged
                logging.info("unsubscription acknowledged  " + t[0])
                client.unsuback_flag = True

    def _on_message(self, client, user_data, message):
        """
        Define the message received callback implementation
        :param client: the client instance for this callback
        :param user_data: the private user data as set in Client() or userdata_set()
        :param message:  an instance of MQTTMessage.
                    This is a class with members topic, payload, qos, retain.
        """
        topic = message.topic
        m_decode = str(message.payload.decode("utf-8", "ignore"))
        self.process_message(decoded_message=m_decode, topic=topic)

    def _chk_sub(self):
        """
        This method check the subscription status
        :return: False if I have unacknowledged subscription, otherwise True
        """
        for t in MqttConnect._topic_ack:
            if t[2] == 0:
                logging.info("Subscription to " + t[0] + " not acknowledged")
                return False
            return True

    def wait_for(self, client, message_type, period=0.25):
        if message_type == MqttConnect._MSG_TYPE_CONNACK:
            if client.on_connect:
                while not client.connected_flag:
                    logging.info("waiting connack")
                    print("waiting connack")
                    client.loop()  # check for messages
                    time.sleep(period)
        elif message_type == MqttConnect._MSG_TYPE_DISCONNECT:
            if client.on_disconnect:
                while client.diconnect_flag:
                    logging.info("waiting disconnect")
                    print("waiting disconnect")
                    client.loop()  # check for messages
                    time.sleep(period)
        elif message_type == MqttConnect._MSG_TYPE_SUBACK:
            if client.on_subscribe:
                while not client.suback_flag:
                    logging.info("waiting suback")
                    print("waiting suback")
                    client.loop()  # check for messages
                    time.sleep(period)
        elif message_type == MqttConnect._MSG_TYPE_PUBACK:
            if client.on_publish:
                logging.info("Wait for publish")
                while not client.puback_flag:
                    client.loop()  # check for messages
                    logging.info("waiting puback")
                    print("waiting puback")
                    time.sleep(period)
        elif message_type == MqttConnect._MSG_TYPE_CHKSUBS:
            if self._chk_sub:
                logging.info("Will wait fot all logging...!!!")
                print("Will wait fot all logging...!!!")
                count = 0
                while not self._chk_sub():
                    # check for the message
                    client.loop()
                    logging.info("Wait for all subscription...!!!")
                    print("Wait for all subscription...!!!")
                    time.sleep(period)
                    if count >= 20:
                        return False
                    count += 1
                return True
        elif message_type == MqttConnect._MSG_TYPE_UNSUBACK:
            if client.on_unsubscribe:
                logging.info("Unsubscribe the topic...!!!")
                print("Unsubscribe the topic...!!!")
                while not client.sunsuback_flag:
                    client.loop()  # check for messages
                    logging.info("waiting unsuback")
                    print("waiting unsuback")
                    time.sleep(period)

    def set_user_login(self, user_id, pwd):
        MqttConnect._user_id = user_id
        MqttConnect._user_password = pwd

    def connect_to_server(self, client_id="default_client") -> mqtt.Client:
        try:
            # create the instance of the client by using unique client ID
            client = mqtt.Client(client_id)
            print(client)
            # set the all callback functions
            client.on_connect = self._on_connect
            client.on_log = self._on_log
            client.on_subscribe = self._on_subscribe
            client.on_publish = self._on_publish
            client.on_message = self._on_message
            client.on_disconnect = self._on_disconnect
            client.on_unsubscribe = self._on_unsubscribe
            # connect by using UserID and Password provided by the user.
            print("User name: ", MqttConnect._user_id, MqttConnect._user_password)
            if MqttConnect._user_id != "" and MqttConnect._user_password != "":
                client.username_pw_set(MqttConnect._user_id, MqttConnect._user_password)
                logging.info("User Login Success using ID and Password...!!!")
                print("User Login Success using ID and Password...!!!")

            # flag
            client.bad_connection_flag = False
            client.connected_flag = False
            client.disconnect_flag = False
            client.puback_flag = False
            client.suback_flag = False

            connflag = False
            badcount = 0
            while not connflag:
                logging.info("connecting to broker " + str(MqttConnect._broker) + " retry= " + str(badcount))
                logging.info("connecting to broker " + str(MqttConnect._broker))
                print("connecting to broker " + str(MqttConnect._broker) + " retry= " + str(badcount))
                print("connecting to broker " + str(MqttConnect._broker))

                try:
                    client.connect(MqttConnect._broker, MqttConnect._port)  # connect to broker
                    print("Connect Call")
                    connflag = True
                except:
                    client.badconnection_flag = True
                    logging.info("connection failed")
                    print("connection failed")
                    badcount += 1
                    if badcount == 3:
                        raise SystemError("No Connected")  # give up
            print("Connecting.....Please wait")

            self.wait_for(client, MqttConnect._MSG_TYPE_CONNACK)
            return client
        except ConnectionError as conn_err:
            logging.info("There is an exception " + str(conn_err))

    def process_message(self, decoded_message, topic):
        global message_count, message_count2, verbose, log_data_flag, display, last_message
        data = dict()
        time_now = time.localtime(time.time())
        message_count += 1
        # TODO: Change the decode message if mesg not comes form server
        # print("Decoded message type is ", type(decoded_message), decoded_message)
        if decoded_message is not None:
            m = "MESSAGE TIME: " + time.asctime(time_now) + ", TOPIC: " + topic + ", MESSAGE: " + str(decoded_message)
        else:
            m = "MESSAGE TIME: " + time.asctime(time_now) + ", TOPIC: " + topic + ", MESSAGE: " + "None"
        if display:
            if verbose:  # display all message
                MqttConnect._message_q.put(m)
                message_count2 += 1
            else:  # only display change message
                if self.has_changed(topic, decoded_message) == 0:  # changed so logging.info
                    MqttConnect._message_q.put(m)
                    message_count2 += 1
        logging.info("List of message: " + str(last_message))
