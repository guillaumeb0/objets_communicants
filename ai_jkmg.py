#-*- encoding: UTF-8 -*-
from pdu import Pdu, PduType, DeviceType, PduException
import time

class Node:
    def __init__(self, obj_id, value, obj_time):
        self.node_id = obj_id
        self.value = value
        self.time = obj_time


class Link:
    def __init__(self, node1, objects2):
        self.node1 = node1
        self.node2 = objects2
        self.weight = 0


class Graph:
    def __init__(self):
        self.links = []

    def add_link(self, link):
        self.links.append(link)

    def remove_link(self, link):
        self.links.remove(link)


class AiJkmg:
    def __init__(self, epsilon, alpha, threshold_time, threshold_weight):
        self.epsilon = epsilon
        self.alpha = alpha
        self.threshold_time = threshold_time
        self.threshold_weight= threshold_weight
        self.graph = Graph()

    def graph_add(self, object_dict):
        """
        Add one or several link to the graph if the association of object are not already present.
        :param object_dict: A dictionary containing the current objects connected to the network.
        :return: None.
        """
        # Add link to the Graph only when we have at least two element in the dict
        if len(object_dict) > 1:
            keys = object_dict.keys()
            n = len(keys)
            for i in range(n):
                # Check there is an element after
                if i+1 < n:
                    # Check object existence
                    # TODO : Does this work ???
                    #if [link for link in self.graph.links if link.node1.node_id == keys[i] and link.node2.node_id == keys[(i + 1)]:
                        # TODO : Get value and time of each object before creating the link
                    for link in self.graph.links:
                        if not (link.node1.node_id == key[i] and link.node2.node_id == keys[i+1]):
                            node1 = Node(keys[i], obj_value, object_dict[keys[i]]["last_recv_msg"])
                            node2 = Node(keys[(i + 1)], obj_value, object_dict[keys[(i + 1)]]["last_recv_msg"])
                            self.graph.add_link(Link(node1, node2))


    def graph_remove(self, object_dict):
        """
        Remove one or several link from the graph if they are not present in the object_dict
        and when they have not been connected for too long.
        :param object_dict: A dictionary containing the current objects connected to the network.
        :return: None.
        """
        for link in self.graph.links:
            # Remove link not present in the object_dict with a delta time superior to the threshold time defined
            if (link.node1.node_id not in object_dict and (link.node1.time - time.time()) > self.threshold_time) or \
                    (link.node2.node_id not in object_dict and (link.node2.time - time.time()) > self.threshold_time):
                self.graph.remove_link(link)

    def graph_update(self, object_dict):
        """
        Update the Graph by adding element not present in the Graph and removing element not present in the object_dict.
        :param object_dict: A dictionary containing the current objects connected to the network.
        :return: None.
        """
        self.graph_remove(object_dict)  # Remove old element from the graph

        self.graph_add(object_dict) # Add new element to the graph

    def predict(self, object_dict, object0):
        """
        Update the Graph and Set a list of object, linked to the given object (object0), to be activated.
        :param object_dict: A dictionary containing the current objects connected to the network.
        :param object0: The current object activated.
        :return: A list of objects to be activated.
        """
        self.graph_update(object_dict)  # Update the graph

        objects = []

        # Add object to the list when the link weight is superior to the threshold
        for link in self.graph.links:
            if link.node1 == object0 and link.weight > self.threshold_weight:
                objects.append(link.node1.node_id)
            elif link.node2 == object0 and link.weight > self.threshold_weight:
                objects.append(link.node2.node_id)

        return objects

    def learn(self, object_dict):
        """
        Update the Graph and Set the weight value of each link.
        :param object_dict: A dictionary containing the current objects connected to the network.
        :return: None.
        """
        self.graph_update(object_dict)  # Update the graph

        for link in self.graph.links:
            link.weight += self.epsilon * link.node1.value * link.node2.value - self.alpha

    def cheat(self):
        """
        Set a high value for link
            between Pressure captor (id = "01") and ServoMotor (id = "02").
            between Pressure captor (id = "01") and Light (id = "04").
        :return: None.
        """
        for link in self.graph.links:
            if (link.node1.node_id == "11" and link.node2 in ("02", "04")) or (link.node2.node_id == "11" and link.node1 in ("02", "04")):
                link.weight += self.epsilon * 100 * self.threshold_weight
