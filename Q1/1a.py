# !/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSController


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    # pylint: disable=arguments-differ
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):

        #adding 3 routers in 3 different subnets
        r1 = self.addNode( 'ra', cls = LinuxRouter, ip = '192.168.1.1/24' )
        r2 = self.addNode( 'rb', cls = LinuxRouter, ip = '192.168.2.1/24' )
        r3 = self.addNode( 'rc', cls = LinuxRouter, ip = '192.168.3.1/24' )

        #adding the switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        #adding the host-swith link
        self.addLink(s1, r1, intfName2 = 'r1-eth1', params2={ 'ip' : '192.168.1.1/24' })
        self.addLink(s2, r2, intfName2 = 'r2-eth1', params2={ 'ip' : '192.168.2.1/24' })
        self.addLink(s3, r3, intfName2 = 'r3-eth1', params2={ 'ip' : '192.168.3.1/24' })


        #adding router to router link in a new subnet for the establishing connections between routers
        self.addLink(r1, r2, intfName1='r1-eth2', intfName2='r2-eth2',
                     params1={'ip': '192.100.0.1/24'},
                     params2={'ip': '192.100.0.2/24'},
                     bw=1 , delay = "10ms")
        self.addLink(r2, r3, intfName1='r2-eth3', intfName2='r3-eth2',
                     params1={'ip': '192.100.1.2/24'},
                     params2={'ip': '192.100.1.3/24'},
                     bw=1 , delay = "10ms")
        self.addLink(r3, r1, intfName1='r3-eth3', intfName2='r1-eth3',
                     params1={'ip': '192.100.2.3/24'},
                     params2={'ip': '192.100.2.1/24'},
                     bw=1 , delay = "10ms")

        #adding host specifying the default route
        h1a = self.addHost('h1', ip = '192.168.1.101/24', defaultRoute = 'via 192.168.1.1')
        h1b = self.addHost('h2', ip = '192.168.1.102/24', defaultRoute = 'via 192.168.1.1')

        h2a = self.addHost('h3', ip = '192.168.2.101/24', defaultRoute = 'via 192.168.2.1')
        h2b = self.addHost('h4', ip = '192.168.2.102/24', defaultRoute = 'via 192.168.2.1')
        
        h3a = self.addHost('h5', ip = '192.168.3.101/24', defaultRoute = 'via 192.168.3.1')
        h3b = self.addHost('h6', ip = '192.168.3.102/24', defaultRoute = 'via 192.168.3.1')

        #adding host switch links
        self.addLink(h1a, s1, bw=2, delay = "5ms")
        self.addLink(h1b, s1, bw=2, delay = "5ms")

        self.addLink(h2a, s2, bw=2, delay = "5ms")
        self.addLink(h2b, s2, bw=2, delay = "5ms")

        self.addLink(h3a, s3, bw=2, delay = "5ms")
        self.addLink(h3b, s3, bw=2, delay = "5ms")


def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo = topo, controller=OVSController ) 

    info( '*** Routing Table on Router :\n' )

    #adding routing for reaching networks that aren't directly connected
    info(net[ 'ra' ].cmd("ip route add 192.168.2.0/24 via 192.100.0.2 dev r1-eth2"))
    info(net[ 'ra' ].cmd("ip route add 192.168.3.0/24 via 192.100.2.3 dev r1-eth3"))

    info(net[ 'rb' ].cmd("ip route add 192.168.1.0/24 via 192.100.0.1 dev r2-eth2"))
    info(net[ 'rb' ].cmd("ip route add 192.168.3.0/24 via 192.100.1.3 dev r2-eth3"))

    info(net[ 'rc' ].cmd("ip route add 192.168.1.0/24 via 192.100.2.1 dev r3-eth3"))
    info(net[ 'rc' ].cmd("ip route add 192.168.2.0/24 via 192.100.1.2 dev r3-eth2"))


    # info("\nFor router ra:", net['ra'].cmd('route'))
    # info("\nFor router rb:", net['rb'].cmd('route'))
    # info("\nFor router rc:", net['rc'].cmd('route'))


    net.start()
    CLI( net )
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
