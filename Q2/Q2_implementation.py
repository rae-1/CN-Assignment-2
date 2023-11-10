from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSController
from time import sleep
from mininet.link import TCLink
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='b')
parser.add_argument('--congestion', default='cubic')
parser.add_argument('--loss', default='0')
args = parser.parse_args()


class NetworkTopo(Topo):

    def build(self, **_opts):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        h1 = self.addHost('h1', ip='10.0.1.1/24')
        h2 = self.addHost('h2', ip='10.0.1.2/24')
        h3 = self.addHost('h3', ip='10.0.1.3/24')
        h4 = self.addHost('h4', ip='10.0.1.4/24')

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(s1, s2,cls=TCLink, bw=10, loss=int(args.loss))



def run(config, congestion_control, link_loss):
    topo = NetworkTopo()
    net = Mininet(topo=topo, controller=OVSController, link=TCLink)

    net.start()

    net.waitConnected()

    # Starting server on h4
    server_host = net.get('h4')
    server_host.cmd('iperf -s &')
    #giving some time for the server to setup
    sleep(2)

    '''
        Selecting the clients based
        on configuration
    '''
    if config == 'b':
        client_hosts = ['h1']
    elif config == 'c':
        client_hosts = ['h1', 'h2', 'h3']
    else:
        info('Invalid\n')
        net.stop()
        return

    num = 1
    # Run iperf commands and capture the output in a pcap or text file
    iperf_output = ""
    for host in client_hosts:
        #Get the client
        client = net.get(host)

        '''
            For getting the output in a pcap file.
            In case you want to see the output then
            uncomment the next 3 lines and the 85th line.
        '''
        # pcap_file = f"{args.congestion}_capture_loss_{args.loss}.pcap"
        # tcpdump_cmd = f'tcpdump -i {client.defaultIntf().name} -w {pcap_file} &'
        # client.cmd(tcpdump_cmd)

        #making the corresponding host a client
        iperf_cmd = f'iperf -c {server_host.IP()} -t 5 -i 1 -Z {congestion_control}'
        iperf_output = client.cmd(iperf_cmd)

        sleep(1)
        # client.cmd('kill %tcpdump')

        '''
            For getting the output in a text file. In case
            you want to see the output in a text file then
            uncomment the next 3 lines only.
        '''
        # file_path = f"./file{num}.txt"
        # with open(file_path, 'w') as file:
        #     file.write(iperf_output)


        '''
            The infomation about the throughput that is stored
            in the text or pcap file is also displayed in the terminal.
        '''
        info(f'Iperf results:\n{iperf_output}\n') 
        num += 1

    # CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run(args.config, args.congestion, args.loss)