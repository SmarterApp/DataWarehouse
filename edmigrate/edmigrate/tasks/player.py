'''
Created on Mar 21, 2014

@author: ejen
'''
from edmigrate.queues import conductor
import logging
from edmigrate.utils.utils import get_broker_url
from edmigrate.utils.constants import Constants
from edmigrate.database.repmgr_connector import RepMgrDBConnection
import subprocess
from edmigrate.settings.config import Config, get_setting
import edmigrate.utils.reply_to_conductor as reply_to_conductor
from time import sleep
from kombu import Connection
import socket
from edmigrate.edmigrate_celery import celery
from edmigrate.utils.utils import Singleton


class Player(metaclass=Singleton):

    def __init__(self, logger=logging.getLogger(Constants.WORKER_NAME),
                 admin_logger=logging.getLogger(Constants.EDMIGRATE_ADMIN_LOGGER),
                 connection=Connection(get_broker_url()),
                 exchange=conductor.exchange,
                 routing_key=Constants.CONDUCTOR_ROUTING_KEY):
        self.logger = logger
        self.admin_logger = admin_logger
        self.connection = connection
        self.exchange = exchange
        self.routing_key = routing_key
        self.node_id = None
        self.hostname = None
        self.COMMAND_HANDLERS = {
            Constants.COMMAND_REGISTER_PLAYER: self.register_player,
            Constants.COMMAND_START_REPLICATION: self.connect_master,
            Constants.COMMAND_STOP_REPLICATION: self.disconnect_master,
            Constants.COMMAND_CONNECT_PGPOOL: self.connect_pgpool,
            Constants.COMMAND_DISCONNECT_PGPOOL: self.disconnect_pgpool,
            Constants.COMMAND_RESET_PLAYERS: self.reset_players
        }
        self.set_hostname(socket.gethostname())
        self.set_node_id_from_hostname()

    @classmethod
    def cleanup(cls):
        cls._instances = {}

    def _hostname(self):
        if self.hostname is None:
            return ""
        else:
            return str(self.hostname)

    def _node_id(self):
        if self.node_id is None:
            return ""
        else:
            return str(self.node_id)

    def __enter__(self):
        return self

    def __exit__(self, _type, value, tb):
        pass

    def run_command(self, command, nodes):
        if command in self.COMMAND_HANDLERS:
            if nodes is None:
                if command in [Constants.COMMAND_REGISTER_PLAYER, Constants.COMMAND_RESET_PLAYERS]:
                    self.COMMAND_HANDLERS[command]()
                    self.logger.info("{name}: executed {command}".format(command=command, name=self.__class__.__name__))
                    self.admin_logger.info("{name} at {hostname} with node id {node_id} executed {command} successfully".
                                           format(name=self.__class__.__name__, hostname=self._hostname(),
                                                  node_id=self._node_id(), command=command))
                else:
                    self.logger.warning("{name}: {command} require nodes".format(command=command, name=self.__class__.__name__))
                    self.admin_logger.warning("{name} at {hostname} with node id {node_id} failed to execute {command} due to no nodes specified".
                                              format(name=self.__class__.__name__, hostname=self._hostname(),
                                                     node_id=self._node_id(), command=command))
            else:
                if self.node_id in nodes:
                    self.COMMAND_HANDLERS[command]()
                    self.logger.info("{name}: {node_id} executed {command}".
                                     format(command=command, name=self.__class__.__name__, node_id=self._node_id()))
                    self.admin_logger.info("{name} at {hostname} with node id {node_id} executed {command} {nodes} successfully".
                                           format(name=self.__class__.__name__, hostname=self._hostname(),
                                                  node_id=self._node_id(), command=command, nodes=str(nodes)))
                else:
                    # ignore the command
                    self.logger.warning("{name}: {command} is ignored because {node_id} is not in {nodes}"
                                        .format(command=command, name=self.__class__.__name__,
                                                node_id=self._node_id(), nodes=str(nodes)))
                    self.admin_logger.warning("{name} at {hostname} with node id {node_id} ignored {command} {nodes}".
                                              format(name=self.__class__.__name__, hostname=self._hostname(),
                                                     node_id=self._node_id(), command=command, nodes=str(nodes)))
        else:
            self.logger.warning("{command} is not implemented by {name}".format(command=command, name=self.__class__.__name__))
            self.admin_logger.warning("{name} at {hostname} with node id {node_id} did not process {command} {nodes} due to command is not implemented".
                                      format(name=self.__class__.__name__, hostname=self._hostname(),
                                             node_id=self._node_id(), command=command, nodes=str(nodes)))

    def set_hostname(self, hostname):
        '''
        get hostname for the current node
        '''
        self.hostname = hostname

    def set_node_id_from_hostname(self):
        '''
        look up repl_nodes for node_id of the host.
        '''
        self.node_id = None
        with RepMgrDBConnection() as conn:
            repl_nodes = conn.get_table(Constants.REPL_NODES)
            results = conn.execute(repl_nodes.select())
            nodes = results.fetchall()
            for node in nodes:
                if node[Constants.REPL_NODE_CONN_INFO].find("host={hostname}".format(hostname=self.hostname)) >= 0:
                    self.node_id = node[Constants.ID]
                    break
        return self.node_id

    def search_blocked_hostname(self, output, hostname):
        '''
        @param output: iptable -L output
        @param hostname: hostname for the machine that are looked up in iptables chain output
        '''
        lines = output.split('\n')
        found = False
        for line in lines:
            if line.find(hostname) >= 0 \
                    and line.find('reject-with icmp-port-unreachable') >= 0 \
                    and line.find('REJECT') >= 0:
                found = True
                break
        return found

    def check_iptable_has_blocked_machine(self, hostname):
        '''
        Run iptables -L, get the output, and search hostname that is in blocked chain
        @param hostname: hostname for the blocked machine
        '''
        chain = get_setting(Config.IPTABLES_CHAIN, Constants.IPTABLES_CHAIN)
        sudo = get_setting(Constants.IPTABLES_SUDO, Constants.IPTABLES_SUDO)
        iptables = get_setting(Constants.IPTABLES_COMMAND, Constants.IPTABLES_COMMAND)
        try:
            output = subprocess.check_output([sudo, iptables, Constants.IPTABLES_LIST, chain], universal_newlines=True)
        except subprocess.CalledProcessError:
            self.logger.error("{name}: Problem to use iptables. Please check with administrator".
                              format(name=self.__class__.__name__,))
            self.admin_logger.critical("{name} at {hostname} with node id {node_id} couldn't use iptables command. Please check edmigrate's privilege.".
                                       format(name=self.__class__.__name__, hostname=self._hostname(),
                                              node_id=self._node_id()))
            output = ''
        return self.search_blocked_hostname(output, hostname)

    def remove_iptable_rules(self, hostname, max_retries):
        '''
        remove machine from iptables block list
        @param hostname: hostname to be blocked
        @param max_retries: maximum time to retry to remove host from iptable block rules
        '''
        # the code will try to clean up as many as possible iptables rules that block the host in case multiple
        # rules are inserted. But in order not fall into infinite loops. we use max_retries in
        # edmigrate.utils.constants to control maximum number of retries
        # also, if celery has no privileges to operate iptables, it will trigger exception and return result as false
        chain = get_setting(Config.IPTABLES_CHAIN, Constants.IPTABLES_CHAIN)
        sudo = get_setting(Constants.IPTABLES_SUDO, Constants.IPTABLES_SUDO)
        iptables = get_setting(Constants.IPTABLES_COMMAND, Constants.IPTABLES_COMMAND)
        try:
            output = subprocess.check_output([sudo, iptables, Constants.IPTABLES_DELETE, chain,
                                              Constants.IPTABLES_SOURCE, hostname,
                                              Constants.IPTABLES_JUMP, Constants.IPTABLES_TARGET],
                                             universal_newlines=True)
            while output != 'iptables: No chain/target/match by that name.' and max_retries >= 0:
                sleep(Constants.REPLICATION_CHECK_INTERVAL)
                output = subprocess.check_output([sudo, iptables, Constants.IPTABLES_DELETE, chain,
                                                  Constants.IPTABLES_SOURCE, hostname,
                                                  Constants.IPTABLES_JUMP, Constants.IPTABLES_TARGET],
                                                 universal_newlines=True)
                max_retries -= 1
        except subprocess.CalledProcessError:
            self.logger.warning("{name}: Failed to remove rules to reject {hostname}".
                                format(name=self.__class__.__name__, hostname=hostname))
        return not self.check_iptable_has_blocked_machine(hostname)

    def add_iptable_rules(self, hostname):
        '''
        add machine into iptable block chain
        @param hostname: hostname for the machine
        '''
        chain = get_setting(Config.IPTABLES_CHAIN, Constants.IPTABLES_CHAIN)
        sudo = get_setting(Constants.IPTABLES_SUDO, Constants.IPTABLES_SUDO)
        iptables = get_setting(Constants.IPTABLES_COMMAND, Constants.IPTABLES_COMMAND)
        try:
            subprocess.check_output([sudo, iptables, Constants.IPTABLES_INSERT, chain,
                                     Constants.IPTABLES_SOURCE, hostname,
                                     Constants.IPTABLES_JUMP, Constants.IPTABLES_TARGET],
                                    universal_newlines=True)
            sleep(Constants.REPLICATION_CHECK_INTERVAL)
        except subprocess.CalledProcessError:
            self.logger.error("{name}: Failed to add rules to reject {hostname}".
                              format(name=self.__class__.__name__, hostname=hostname))
        return self.check_iptable_has_blocked_machine(hostname)

    def connect_pgpool(self):
        '''
        remove iptables rules to enable pgpool access slave database
        '''
        pgpool = get_setting(Config.PGPOOL_HOSTNAME)
        self.logger.info("{name}: Resuming pgpool ( {pgpool} )".
                         format(name=self.__class__.__name__, pgpool=pgpool))
        # perform multiple times disable in case it was blocked multiple times in iptables
        max_retries = Constants.REPLICATION_MAX_RETRIES
        status = self.remove_iptable_rules(pgpool, max_retries)
        if status:
            reply_to_conductor.acknowledgement_pgpool_connected(self.node_id, self.connection,
                                                                self.exchange, self.routing_key)
            self.logger.info("{name}: Unblock pgpool ( {pgpool} )".
                             format(name=self.__class__.__name__, pgpool=pgpool))
            self.admin_logger.info("{name} at {hostname} with node id {node_id} unblocked pgpool machine ( {pgpool}).".
                                   format(name=self.__class__.__name__, hostname=self._hostname(),
                                          node_id=self._node_id(), pgpool=pgpool))
        else:
            self.logger.warning("{name}: Failed to unblock pgpool ( {pgpool} )".
                                format(name=self.__class__.__name__, pgpool=pgpool))
            self.admin_logger.critical("{name} at {hostname} with node id {node_id} failed to unblock pgpool machine ( {pgpool} ). Please check the {hostname}.".
                                       format(name=self.__class__.__name__, hostname=self._hostname(),
                                              node_id=self._node_id(), pgpool=pgpool))

    def disconnect_pgpool(self):
        '''
        insert iptables rules to block pgpool to access postgres db
        '''
        pgpool = get_setting(Config.PGPOOL_HOSTNAME)
        self.logger.info("{name}: Blocking pgpool ( {pgpool} )".
                         format(name=self.__class__.__name__, pgpool=pgpool))
        # only add rules when there is no rule in iptables
        status = self.add_iptable_rules(pgpool)
        if status:
            reply_to_conductor.acknowledgement_pgpool_disconnected(self.node_id, self.connection,
                                                                   self.exchange, self.routing_key)
            self.logger.info("{name}: Block pgpool ( {pgpool} )".
                             format(name=self.__class__.__name__, pgpool=pgpool))
            self.admin_logger.info("{name} at {hostname} with node id {node_id} blocked pgpool machine ( {pgpool}).".
                                   format(name=self.__class__.__name__, hostname=self._hostname(),
                                          node_id=self._node_id(), pgpool=pgpool))
        else:
            self.logger.warning("{name}: Failed to block pgpool ( {pgpool} )".
                                format(name=self.__class__.__name__, pgpool=pgpool))
            self.admin_logger.critical("{name} at {hostname} with node id {node_id} failed to block pgpool machine ( {pgpool} ). Please check the {hostname}.".
                                       format(name=self.__class__.__name__, hostname=self._hostname(),
                                              node_id=self._node_id(), pgpool=pgpool))

    def connect_master(self):
        '''
        remove iptable rules to unblock master from access slave database
        '''
        master = get_setting(Config.MASTER_HOSTNAME)
        self.logger.info("{name}: Resuming master( {master} )".
                         format(name=self.__class__.__name__, master=master))
        # perform multiple times disable in case it was blocked multiple times in iptables
        max_retries = Constants.REPLICATION_MAX_RETRIES
        status = self.remove_iptable_rules(master, max_retries)
        if status:
            reply_to_conductor.acknowledgement_master_connected(self.node_id, self.connection,
                                                                self.exchange, self.routing_key)
            self.logger.info("{name}: Unblock master database ( {master} )".
                             format(name=self.__class__.__name__, master=master))
            self.admin_logger.info("{name} at {hostname} with node id {node_id} unblocked master database ( {master}).".
                                   format(name=self.__class__.__name__, hostname=self._hostname(),
                                          node_id=self._node_id(), master=master))
        else:
            self.logger.warning("{name}: Failed to unblock master ( {master} )".
                                format(name=self.__class__.__name__, master=master))
            self.admin_logger.critical("{name} at {hostname} with node id {node_id} failed to unblock master database ( {master} ). Please check the {hostname}.".
                                       format(name=self.__class__.__name__, hostname=self._hostname(),
                                              node_id=self._node_id(), master=master))

    def disconnect_master(self):
        '''
        insert iptable rules to block master to access slave database
        '''
        master = get_setting(Config.MASTER_HOSTNAME)
        self.logger.info("{name}: Blocking master( {master} )".
                         format(name=self.__class__.__name__, master=master))
        # only add rules when there is no rule in iptables
        status = self.add_iptable_rules(master)
        if status:
            reply_to_conductor.acknowledgement_master_disconnected(self.node_id, self.connection,
                                                                   self.exchange, self.routing_key)
            self.logger.info("{name}: Block master database ( {master} )".
                             format(name=self.__class__.__name__, master=master))
            self.admin_logger.info("{name} at {hostname} with node id {node_id} blocked master database ( {master}).".
                                   format(name=self.__class__.__name__, hostname=self._hostname(),
                                          node_id=self._node_id(), master=master))
        else:
            self.logger.warning("{name}: Failed to block master( {master} )".
                                format(name=self.__class__.__name__, master=master))
            self.admin_logger.critical("{name} at {hostname} with node id {node_id} failed to block master database ( {master} ). Please check the {hostname}.".
                                       format(name=self.__class__.__name__, hostname=self._hostname(),
                                              node_id=self._node_id(), master=master))

    def reset_players(self):
        '''
        reset players. so it will not block pgpool and master database
        '''
        master = get_setting(Config.MASTER_HOSTNAME)
        pgpool = get_setting(Config.PGPOOL_HOSTNAME)
        self.logger.info("{name}: Reset iptables rules for master ( {master} ) and pgpool ( {pgpool} )".
                         format(name=self.__class__.__name__, master=master, pgpool=pgpool))
        max_retries = Constants.REPLICATION_MAX_RETRIES
        status_1 = self.remove_iptable_rules(pgpool, max_retries)
        status_2 = self.remove_iptable_rules(master, max_retries)
        if status_1 and status_2:
            reply_to_conductor.acknowledgement_reset_players(self.node_id, self.connection,
                                                             self.exchange, self.routing_key)
            self.logger.info("{name}: Reset iptables configurations for pgpool ( {pgpool} ) and master ( {master})".
                             format(name=self.__class__.__name__, pgpool=pgpool, master=master))
            self.admin_logger.info("{name} at {hostname} with node id {node_id} unblocked master database ( {master}) and pgpool machine {pgpool}.".
                                   format(name=self.__class__.__name__, hostname=self._hostname(),
                                          node_id=self._node_id(), master=master, pgpool=pgpool))
        elif status_1 and not status_2:
            self.logger.error("{name}: Failed to reset iptables for pgpool ( {pgpool} )".
                              format(name=self.__class__.__name__, pgpool=pgpool))
            self.admin_logger.critical("{name} at {hostname} with node id {node_id} failed to unblock pgpool machine {pgpool}. Please check {hostname}.".
                                       format(name=self.__class__.__name__, hostname=self._hostname(),
                                              node_id=self._node_id(), pgpool=pgpool))
        elif not status_1 and status_2:
            self.logger.error("{name}: Failed to reset iptables for master( {master} )".
                              format(name=self.__class__.__name__, master=master))
            self.admin_logger.critical("{name} at {hostname} with node id {node_id} failed to unblock master database ( {master}). Please check {hostname}.".
                                       format(name=self.__class__.__name__, hostname=self._hostname(),
                                              node_id=self._node_id(), master=master))
        else:
            self.logger.error("{name}: Failed to reset iptable for master( {master} ) and pgpool ( {pgpool} )".
                              format(name=self.__class__.__name__, master=master, pgpool=pgpool))
            self.admin_logger.critical("{name} at {hostname} with node id {node_id} failed to unblock master database ( {master}) and pgpool machine {pgpool}. Please check {hostname}".
                                       format(name=self.__class__.__name__, hostname=self._hostname(),
                                              node_id=self._node_id(), master=master, pgpool=pgpool))

    def register_player(self):
        '''
        register player to conductor
        '''
        self.logger.info("{name}: Register {name} to conductor".format(name=self.__class__.__name__))
        if self.node_id is not None:
            reply_to_conductor.register_player(self.node_id, self.connection, self.exchange, self.routing_key)
            self.logger.info("{name}: Register {hostname} as node_id ({node_id})".
                             format(name=self.__class__.__name__, hostname=self.hostname, node_id=self.node_id))
            self.admin_logger.info("{name} at {hostname} with node id {node_id} registered to conductor.".
                                   format(name=self.__class__.__name__, hostname=self._hostname(),
                                          node_id=self._node_id()))
        else:
            # log errors
            self.logger.error("{name}: {hostname} has no node_id".
                              format(name=self.__class__.__name__, hostname=self.hostname))
            self.admin_logger.critical("{name} at {hostname} with node id {node_id} failed to register to conductor. Please check {hostname}".
                                       format(name=self.__class__.__name__, hostname=self._hostname(),
                                              node_id=self._node_id()))


@celery.task(name=Constants.PLAYER_TASK, ignore_result=True)
def player_task(command, nodes):
    """
    This is a player task that runs on slave database. It assumes only one celery worker per node. So task
    will be a singleton
    Please see https://docs.google.com/a/amplify.com/drawings/d/14K89SK6FLTPCFi0clvmnrTFMaIkc0eDDwQ0kt8CsTCE/
    for architecture
    Two tasks, COMMAND_FIND_PLAYER and COMMAND_REST_PLAYER are executed regardless player nodes are included or not
    For other tasks. Player task checks membership of current player node in nodes argument represented as a list
    of node_id. Those tasks are executed if and only if membership is true.
    """
    with Player() as player:
        player.run_command(command, nodes)
