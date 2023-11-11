from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSController
import subprocess

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class NetworkTopo(Topo):
    def build(self, **_opts):
        r1 = self.addHost('ra', cls=LinuxRouter, ip='172.16.0.1/24')
        s1 = self.addSwitch('s1')
        self.addLink(s1, r1, intfName2='ra-eth1', params2={'ip': '172.16.0.1/24'})
        h1 = self.addHost('h1', ip='172.16.0.2/24', defaultRoute='via 172.16.0.1')
        h2 = self.addHost('h2', ip='172.16.0.3/24', defaultRoute='via 172.16.0.1')
        self.addLink(h1, s1)
        self.addLink(h2, s1)

        r2 = self.addHost('rb', cls=LinuxRouter, ip='172.16.1.1/24')
        s2 = self.addSwitch('s2')
        self.addLink(s2, r2, intfName2='rb-eth1', params2={'ip': '172.16.1.1/24'})
        h3 = self.addHost('h3', ip='172.16.1.2/24', defaultRoute='via 172.16.1.1')
        h4 = self.addHost('h4', ip='172.16.1.3/24', defaultRoute='via 172.16.1.1')
        self.addLink(h3, s2)
        self.addLink(h4, s2)

        r3 = self.addHost('rc', cls=LinuxRouter, ip='172.16.2.1/24')
        s3 = self.addSwitch('s3')
        self.addLink(s3, r3, intfName2='rc-eth1', params2={'ip': '172.16.2.1/24'})
        h5 = self.addHost('h5', ip='172.16.2.2/24', defaultRoute='via 172.16.2.1')
        h6 = self.addHost('h6', ip='172.16.2.3/24', defaultRoute='via 172.16.2.1')
        self.addLink(h5, s3)
        self.addLink(h6, s3)

        self.addLink(r1, r2, intfName1='ra-eth2', intfName2='rb-eth2',
                    params1={'ip': '172.16.3.1/24'}, params2={'ip': '172.16.3.2/24'})
        self.addLink(r2, r3, intfName1='rb-eth3', intfName2='rc-eth2',
                    params1={'ip': '172.16.4.1/24'}, params2={'ip': '172.16.4.2/24'})
        self.addLink(r3, r1, intfName1='rc-eth3', intfName2='ra-eth3',
                    params1={'ip': '172.16.5.1/24'}, params2={'ip': '172.16.5.2/24'})

if __name__ == '__main__':
    setLogLevel('info')
    subprocess.run("service openvswitch-switch start".split(" "))
    # subprocess.run("sudo apt-get install openvswitch-testcontroller".split(" "))
    # subprocess.run("sudo cp /usr/bin/ovs-testcontroller /usr/bin/ovs-controller".split(" "))
    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True, controller=OVSController)
    
    net.start()
    # Routing table setup
        
    net["ra"].cmd("ip route add 172.16.1.0/24 via 172.16.3.2 dev ra-eth2")
    net["ra"].cmd("ip route add 172.16.2.0/24 via 172.16.3.2 dev ra-eth2")
    net["rb"].cmd("ip route add 172.16.0.0/24 via 172.16.3.1 dev rb-eth2")
    net["rb"].cmd("ip route add 172.16.2.0/24 via 172.16.4.2 dev rb-eth3")
    net["rc"].cmd("ip route add 172.16.0.0/24 via 172.16.4.1 dev rc-eth2")
    net["rc"].cmd("ip route add 172.16.1.0/24 via 172.16.4.1 dev rc-eth2")
    
    info('*** Routing Tables on Routers:\n')
    for router in ['ra', 'rb', 'rc']:
        info(net[router].cmd('route'))
    CLI(net)
    net.stop()
    # subprocess.run(["kill $(lsof -t -i:6653)"])
    subprocess.run("service openvswitch-switch stop".split(" "))
