from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSController
from time import sleep
from mininet.link import TCLink
import argparse

parser = argparse.ArgumentParser(description='Mininet Topology with TCP client-server using iperf')
parser.add_argument('--config', default='b', help='Configuration (b or c)')
parser.add_argument('--congestion', default='cubic', help='Congestion control scheme (e.g., cubic, reno)')
parser.add_argument('--loss', default='0', help='Link loss rate (e.g., 0, 10)')
args = parser.parse_args()


class NetworkTopo(Topo):
    "A LinuxRouter connecting three IP subnets"
    # def __init__(self, loss):
    #     self.link_loss = loss

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
        self.addLink(s1, s2,cls=TCLink, bw=20, loss=int(args.loss))



def run(config, congestion_control, link_loss):

    "Test Linux Router with iperf TCP client-server"
    topo = NetworkTopo()
    net = Mininet(topo=topo, controller=OVSController, link=TCLink)

    # Configure congestion control and link loss
    # for switch in net.switches:
    #     switch.cmd(f'tc qdisc del dev {switch.name}-eth1 root')
    #     switch.cmd(f'tc qdisc add dev {switch.name}-eth1 root netem loss {link_loss} delay 10ms')
    #     switch.cmd(f'ethtool -K {switch.name}-eth1 gro off')

    net.start()

    net.waitConnected()

    # Start server on h4
    server_host = net.get('h4')
    server_host.cmd('iperf -s &')
    sleep(2)

    # Start clients based on configuration
    if config == 'b':
        client_hosts = ['h1']
    elif config == 'c':
        client_hosts = ['h1', 'h2', 'h3']
    else:
        info('Invalid configuration. Use --config=b or --config=c\n')
        net.stop()
        return

    num = 1
    # Run iperf commands and capture the output
    iperf_output = ""
    for host in client_hosts:
        client = net.get(host)
        iperf_cmd = f'iperf -c {server_host.IP()} -t 10 -i 1 -C {congestion_control}'
        iperf_output = client.cmd(iperf_cmd)

        file_path = f"./file{num}.txt"
        with open(file_path, 'w') as file:
            file.write(iperf_output)

        info(f'Iperf results:\n{iperf_output}\n') 
        num += 1

    # Wait for iperf tests to complete
    # print(iperf_output)
    # Print the complete iperf output

    # CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run(args.config, args.congestion, args.loss)