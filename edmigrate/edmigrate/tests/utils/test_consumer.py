'''
Created on Mar 16, 2014

@author: tosako
'''
import unittest
from kombu import Connection
from edmigrate.utils.consumer import ConsumerThread
from edmigrate.utils.slave_tracker import SlaveTracker
from edmigrate.utils import reply_to_conductor
import time
import threading
from edmigrate.queues import conductor
from edmigrate.utils.constants import Constants


class Test(unittest.TestCase):

    lock = threading.Lock()

    def setUp(self):
        self.lock.acquire()
        self.__connection = Connection("memory://")
        self.__thread = ConsumerThread(self.__connection)
        self.__thread.start()
        time.sleep(1)
        SlaveTracker().reset()

    def tearDown(self):
        self.__thread.stop()
        self.lock.release()

    def test_ACK_COMMAND_FIND_SLAVE(self):
        reply_to_conductor.register_slave(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        reply_to_conductor.register_slave(115, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        time.sleep(1)
        slave_tracker = SlaveTracker()
        ids = slave_tracker.get_slave_ids(timeout=5)
        self.assertEqual(2, len(ids))
        self.assertIn(112, ids)
        self.assertIn(115, ids)

    def test_ACK_COMMAND_DISCONNECT_MASTER(self):
        reply_to_conductor.register_slave(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        reply_to_conductor.register_slave(115, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        reply_to_conductor.acknowledgement_master_disconnected(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        time.sleep(1)
        slave_tracker = SlaveTracker()
        self.assertTrue(slave_tracker.is_replication_stopped(112))
        self.assertFalse(slave_tracker.is_replication_stopped(115))

    def test_ACK_COMMAND_CONNECT_MASTER(self):
        reply_to_conductor.register_slave(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        reply_to_conductor.register_slave(115, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        time.sleep(1)
        slave_tracker = SlaveTracker()
        self.assertTrue(slave_tracker.is_replication_started(112))
        self.assertTrue(slave_tracker.is_replication_started(115))
        reply_to_conductor.acknowledgement_master_disconnected(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        time.sleep(1)
        self.assertTrue(slave_tracker.is_replication_stopped(112))
        self.assertTrue(slave_tracker.is_replication_started(115))
        reply_to_conductor.acknowledgement_master_connected(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        time.sleep(1)
        self.assertTrue(slave_tracker.is_replication_started(112))
        self.assertTrue(slave_tracker.is_replication_started(115))

    def test_ACK_COMMAND_DISCONNECT_PGPOOL(self):
        reply_to_conductor.register_slave(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        reply_to_conductor.register_slave(115, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        reply_to_conductor.acknowledgement_pgpool_disconnected(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        time.sleep(1)
        slave_tracker = SlaveTracker()
        self.assertTrue(slave_tracker.is_pgpool_disconnected(112))
        self.assertFalse(slave_tracker.is_pgpool_disconnected(115))

    def test_ACK_COMMAND_CONNECT_PGPOOL(self):
        reply_to_conductor.register_slave(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        reply_to_conductor.register_slave(115, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        time.sleep(1)
        slave_tracker = SlaveTracker()
        self.assertTrue(slave_tracker.is_pgpool_connected(112))
        self.assertTrue(slave_tracker.is_pgpool_connected(115))
        reply_to_conductor.acknowledgement_pgpool_disconnected(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        time.sleep(1)
        self.assertTrue(slave_tracker.is_pgpool_disconnected(112))
        self.assertTrue(slave_tracker.is_pgpool_connected(115))
        reply_to_conductor.acknowledgement_pgpool_connected(112, self.__connection, conductor.exchange, Constants.CONDUCTOR_ROUTING_KEY)
        time.sleep(1)
        self.assertTrue(slave_tracker.is_pgpool_connected(112))
        self.assertTrue(slave_tracker.is_pgpool_connected(115))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_ACK_COMMAND_FIND_SLAVE']
    unittest.main()
