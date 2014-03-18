import unittest
from unittest.mock import MagicMock, create_autospec
from unittest import skip
from mocket.mocket import Mocket
from edmigrate.tests.utils.unittest_with_repmgr_sqlite import Unittest_with_repmgr_sqlite
from edmigrate.database.repmgr_connector import RepMgrDBConnection
from edmigrate.tasks.slave import get_hostname, get_slave_node_id_from_hostname, check_replication_status,\
    is_replication_paused, is_replication_active, check_iptable_has_blocked_pgpool, connect_pgpool,\
    disconnect_pgpool, connect_master, disconnect_master, find_slave, slave_task, parse_iptable_output
from edmigrate.utils.constants import Constants
import subprocess


class SlaveTaskTest(Unittest_with_repmgr_sqlite):

    @classmethod
    def setUpClass(cls):
        super(SlaveTaskTest, cls).setUpClass()

    def setUp(self):
        self.hostname = 'localhost'
        self.node_id = 1
        self.cluster = 'test_cluster'
        self.pgpool = 'edwdbsrv4.poc.dum.edwdc.net'
        with RepMgrDBConnection() as conn:
            repl_nodes = conn.get_table(Constants.REPL_NODES)
            conn.execute(repl_nodes.insert().values({Constants.ID: self.node_id,
                                                     Constants.REPL_NODE_CLUSTER: self.cluster,
                                                     Constants.REPL_NODE_CONN_INFO: 'host=localhost user=repmgr dbname=test'}))
        self.noblock_firewall_output = 'Chain INPUT (policy ACCEPT)\ntarget     prot opt source               destination         \nACCEPT     all  --  anywhere             anywhere            state RELATED,ESTABLISHED \nACCEPT     icmp --  anywhere             anywhere            \nACCEPT     all  --  anywhere             anywhere            \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:http \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:webcache \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:ssh \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:distinct \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:solve \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:pcsync-https \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:amqp \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:personal-agent \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:15672 \nPGSQL      tcp  --  anywhere             anywhere            state NEW tcp dpt:postgres flags:FIN,SYN,RST,ACK/SYN \nREJECT     all  --  anywhere             anywhere            reject-with icmp-host-prohibited \n\nChain FORWARD (policy ACCEPT)\ntarget     prot opt source               destination         \nREJECT     all  --  anywhere             anywhere            reject-with icmp-host-prohibited \n\nChain OUTPUT (policy ACCEPT)\ntarget     prot opt source               destination         \n\nChain PGSQL (1 references)\ntarget     prot opt source               destination         \nACCEPT     all  --  anywhere             anywhere            \n'

        self.block_once_output = 'Chain INPUT (policy ACCEPT)\ntarget     prot opt source               destination         \nACCEPT     all  --  anywhere             anywhere            state RELATED,ESTABLISHED \nACCEPT     icmp --  anywhere             anywhere            \nACCEPT     all  --  anywhere             anywhere            \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:http \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:webcache \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:ssh \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:distinct \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:solve \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:pcsync-https \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:amqp \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:personal-agent \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:15672 \nPGSQL      tcp  --  anywhere             anywhere            state NEW tcp dpt:postgres flags:FIN,SYN,RST,ACK/SYN \nREJECT     all  --  anywhere             anywhere            reject-with icmp-host-prohibited \n\nChain FORWARD (policy ACCEPT)\ntarget     prot opt source               destination         \nREJECT     all  --  anywhere             anywhere            reject-with icmp-host-prohibited \n\nChain OUTPUT (policy ACCEPT)\ntarget     prot opt source               destination         \n\nChain PGSQL (1 references)\ntarget     prot opt source               destination         \nREJECT     all  --  edwdbsrv4.poc.dum.edwdc.net  anywhere            reject-with icmp-port-unreachable \nACCEPT     all  --  anywhere             anywhere            \n'
        self.block_twice_output = 'Chain INPUT (policy ACCEPT)\ntarget     prot opt source               destination         \nACCEPT     all  --  anywhere             anywhere            state RELATED,ESTABLISHED \nACCEPT     icmp --  anywhere             anywhere            \nACCEPT     all  --  anywhere             anywhere            \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:http \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:webcache \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:ssh \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:distinct \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:solve \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:pcsync-https \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:amqp \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:personal-agent \nACCEPT     tcp  --  anywhere             anywhere            state NEW tcp dpt:15672 \nPGSQL      tcp  --  anywhere             anywhere            state NEW tcp dpt:postgres flags:FIN,SYN,RST,ACK/SYN \nREJECT     all  --  anywhere             anywhere            reject-with icmp-host-prohibited \n\nChain FORWARD (policy ACCEPT)\ntarget     prot opt source               destination         \nREJECT     all  --  anywhere             anywhere            reject-with icmp-host-prohibited \n\nChain OUTPUT (policy ACCEPT)\ntarget     prot opt source               destination         \n\nChain PGSQL (1 references)\ntarget     prot opt source               destination         \nREJECT     all  --  edwdbsrv4.poc.dum.edwdc.net  anywhere            reject-with icmp-port-unreachable \nREJECT     all  --  edwdbsrv4.poc.dum.edwdc.net  anywhere            reject-with icmp-port-unreachable \nACCEPT     all  --  anywhere             anywhere            \n'

    def tearDown(self):
        with RepMgrDBConnection() as conn:
            repl_nodes = conn.get_table(Constants.REPL_NODES)
            conn.execute(repl_nodes.delete())

    def test_get_hostname(self):
        Mocket.enable()
        hostname = get_hostname()
        self.assertEqual(hostname, self.hostname)

    def test_get_slave_node_id_from_hostname(self):
        hostname = self.hostname
        node_id = get_slave_node_id_from_hostname(hostname)
        self.assertEqual(node_id, self.node_id)

    @skip("under development")
    def test_check_replication_status(self):
        check_replication_status()
        self.assertEqual(True, False)

    @skip("under development")
    def test_is_replication_paused(self):
        is_replication_paused()
        self.assertEqual(True, False)

    @skip("under development")
    def test_is_replication_active(self):
        is_replication_active()
        self.assertEqual(True, False)

    def test_parse_iptable_output_0(self):
        not_found = parse_iptable_output(self.noblock_firewall_output, self.pgpool)
        self.assertFalse(not_found)

    def test_parse_iptable_output_1(self):
        found = parse_iptable_output(self.block_once_output, self.pgpool)
        self.assertTrue(found)

    def test_parse_iptable_output_2(self):
        found = parse_iptable_output(self.block_twice_output, self.pgpool)
        self.assertTrue(found)

    @skip("under development")
    def test_check_iptable_has_blocked_pgpool(self):
        pgpool = 'edwdbsrv4.poc.dum.edwdc.net'
        subprocess.check_output = create_autospec(subprocess.check_output, return_value=self.noblock_firewall_output)
        result = check_iptable_has_blocked_pgpool(pgpool)
        self.assertFalse(result)

    @skip("under development")
    def test_find_slave(self):
        find_slave()
        self.assertEqual(True, False)

    @skip("under development")
    def test_connect_pgpool(self):
        connect_pgpool()
        self.assertEqual(True, False)

    @skip("under development")
    def test_disconnect_pgpool(self):
        disconnect_pgpool()
        self.assertEqual()

    @skip("under development")
    def test_connect_master(self):
        connect_master()
        self.assertEqual(True, False)

    @skip("under development")
    def test_disconnect_master(self):
        disconnect_master()
        self.assertEqual(True, False)

    @skip("under development")
    def test_slave_task(self):
        slave_task()
        self.assertEqual(True, False)
