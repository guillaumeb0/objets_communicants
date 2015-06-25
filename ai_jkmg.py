#-*- encoding: UTF-8 -*-
import time
import threading
import itertools

from pdu import Pdu, PduType, DeviceType, PduException

class Node:
    def __init__(self, obj_id, value, obj_time):
        self.node_id = obj_id
        self.value = value
        self.time = obj_time


class Link:
    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.weight = 0.0


class AiJkmg(threading.Thread):
    def __init__(self, epsilon, alpha, threshold_time, threshold_weight, server):
        threading.Thread.__init__(self)
        self.epsilon = epsilon
        self.alpha = alpha
        self.threshold_time = threshold_time
        self.threshold_weight= threshold_weight
        self.links = list()
        self.server = server
        self.terminated = False

    def run(self):
        t = time.time()
        #while not self.terminated and time.time() - t < 60:
        while not self.terminated:
            print('start')
            arduino_dict = self.server.get_arduino_dict()
            self.learn(arduino_dict)
            self.cheat()
            nodes = self.predict()
            if len(nodes) > 0:
                self.server.new_predict(nodes)
            time.sleep(3)
            
        #while not self.terminated:
        #    print(self.server.get_arduino_dict())
            

    def terminate(self):
        self.terminated = True

    def links_update(self, arduino_dict):
        """
        Add one or several link to links if the association of object are not already present.
        :param arduino_dict: A dictionary containing the current objects connected to the network.
        :return: None.
        """
        self.links_remove(arduino_dict)
        network_couples = self.get_network_links(arduino_dict)
        if not (len(network_couples) > 0):
            return

        # If links is empty, then we directly add network couples in links
        if not (len(self.links) > 0):
            self.links = network_couples
            return

        graph_couples = self.links
        res = list()
        for nc in network_couples:
            found = False
            for gc in graph_couples:
                c1 =  nc.i.node_id == gc.i.node_id or nc.i.node_id == gc.j.node_id
                c2 = nc.j.node_id == gc.i.node_id or nc.j.node_id == gc.j.node_id
                if c1 and c2:
                    found = True

                    if nc.i.node_id == gc.i.node_id:
                        gc.i.value = nc.i.value
                        gc.j.value = nc.j.value
                    else:
                        gc.i.value = nc.j.value
                        gc.j.value = nc.i.value

            if not found:
                res.append(nc)

        self.links.extend(res)

    def get_network_links(self, arduino_dict):
        """
        Take an arduino dict for input and give a list of link for output
        en Link
        """
        datas = arduino_dict
        couples = itertools.combinations(datas.keys(), 2)
        res = list()
        for c in couples:
            i_id = c[0]
            j_id = c[1]
            i = Node(i_id, int(datas[i_id]['pdu'].state), datas[i_id]['last_recv_msg'])
            j = Node(j_id, int(datas[j_id]['pdu'].state), datas[j_id]['last_recv_msg'])
            res.append(Link(i, j))
        return res



    def links_remove(self, arduino_dict):
        """
        Remove one or several link from links if they are not present in the arduino_dict
        and when they have not been connected for too long.
        :param arduino_dict: A dictionary containing the current objects connected to the network.
        :return: None.
        """
        res = list()
        for link in self.links:
            # Remove link not present in the arduino_dict with a delta time superior to the threshold time defined
            if link.i.node_id in arduino_dict.keys() \
                and link.j.node_id in arduino_dict.keys():
                res.append(link)
        self.links = res

    def predict(self):
        """
        Update links and Set a list of nodes to be activated.
        :return: A list of nodes.
        """

        nodes = []

        # Add nodes to the list when the link weight is superior to the threshold
        for link in self.links:
            if link.weight > self.threshold_weight:
                print('i.id: {0}, i.value: {1}; j.id{2}, j.value{3}').format(link.i.node_id, link.i.value, link.j.node_id, link.j.value)                
                if link.i.value == 1 and link.j.value == 0:
                    nodes.append(link.j.node_id)
                elif link.i.value == 0 and link.j.value == 1:
                    nodes.append(link.i.node_id)

        return nodes

    def learn(self, arduino_dict):
        """
        Update the Graph and Set the weight value of each link.
        :param arduino_dict: A dictionary containing the current objects connected to the network.
        :return: None.
        """
        self.links_update(arduino_dict)  # Update links

        for link in self.links:
            link.weight = link.weight + (self.epsilon * (link.i.value * link.j.value)) - self.alpha
            print('W{0},{1} :{2}'.format(link.i.node_id, link.j.node_id, link.weight))

    def cheat(self):
        """
        Set a high value for link
            between Pressure captor (id = "01") and ServoMotor (id = "02").
            between Pressure captor (id = "01") and Light (id = "04").
        :return: None.
        """
        for link in self.links:
            if (link.i.node_id == '11' and link.j.node_id in ('02', '12')) or (link.j.node_id == '11' and link.i.node_id in ('02', '12')):
                link.weight = 100

