from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch, CPULimitedHost
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
import argparse
import os
import subprocess
import re
import matplotlib.pyplot as plt
import time

percent_loss = 0.0
class MyTopology(Topo):
    
    def build(self):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')

        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch2)
        self.addLink(host4, switch2)
        self.addLink(switch1, switch2, cls=TCLink, loss=percent_loss)
        

def run_iperf(net, config,congestion,loss):
    print(f"Running iPerf test for config={config} for {congestion} congestion control and {loss}% loss")   
    
    output_list = []
    if config == 'b':
        # Run iPerf tests between H1 and H4
        
        if net.get('h1') and net.get('h4'):
            h1 = net.get('h1')
            h4 = net.get('h4')
            h4.cmd('iperf -s &')
            # # h1.cmd(f"iperf -c {h4.IP()} -t 30 -C {congestion} -b 10M -i 1 -y C > result_{congestion}_{loss}.txt")
            # output = h1.cmd(f"iperf -c {h4.IP()} -t 4 -f G -Z {congestion.lower()} -i 0.05")
            # print(output)
            # # print(type(output))
            # output_list.append(output)

            # output_server = h4.popen(f"iperf -s -f G -i 0.05", shell=True)
            # time.sleep(1)  # Ensure the server is up and running

            output_client = h1.cmd(f"iperf -c {h4.IP()} -t 4 -f G -Z {congestion.lower()} -i 0.05")
            
            output_list.append(output_client.communicate()[0].decode())

            # output_server.kill()
            # output_list.append(output_server.communicate()[0].decode())
    elif config == 'c':

        # Run multiple clients simultaneously
        if all(net.get(host) for host in ['h1', 'h2', 'h3', 'h4']):
            h4 = net.get('h4')
            h4.cmd('iperf -s &')
            # for i in range(1, 4):
            #     client = net.get(f'h{i}')
            #     # client.cmd(f"iperf -c {h4.IP()} -t 30 -C {congestion} -b 10M -i 1 -y C > result_{congestion}_{loss}_h{i}.txt")
            #     output = client.cmd(f"iperf -c {h4.IP()} -t 4 -Z {congestion.lower()} -b 10M -i 0.2")
            #     print(output)
            #     output_list.append(output)

            clients = [net.get(f'h{i}') for i in range(1, 4)]

            outputs = []
            # output_server = h4.popen(f"iperf -s -f G -i 0.05", shell=True)
            # time.sleep(1)  # Ensure the server is up and running

            for client in clients:
                # Run each iperf client as a background process
                iperf_cmd = f"iperf -c {h4.IP()} -t 4 -f G -Z {congestion.lower()} -i 0.05"
                client_output = client.popen(iperf_cmd, shell=True)
                outputs.append(client_output)

            # output_server.kill()
            # outputs.append(output_server)
            # Gather output of all clients
            output_list = [process.communicate()[0].decode() for process in outputs]
            
    return output_list

def extract_data(output):
    time_list = re.findall(r'-(\d+\.\d+) sec', output)
    bw_list = re.findall(r'(\d*\.?\d*) GBytes/sec', output)
    # print(time_list, bw_list)
    return time_list, bw_list

def plot_graph(time_list, bw_list, save_path=None):
    time_list = [float(i) for i in time_list[:-1]]
    bw_list = [float(i) for i in bw_list[:-1]]
    plt.figure()
    plt.plot(time_list, bw_list, marker='*')
    plt.title('Time vs Throughput')
    plt.xlabel('Time (sec)')
    plt.ylabel('Throughput/Bandwidth (GBytes/sec)')
    plt.grid(True)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='TCP Client-Server Program')
    parser.add_argument('--config', type=str, choices=['b', 'c'], default='b', help='Configuration')
    parser.add_argument('--congestion', type=str, choices=['Vegas', 'Reno', 'Cubic', 'BBR'], default='Cubic', help='Congestion control scheme')
    parser.add_argument('--loss', type=float, default=0.0, help='Link loss in percentage')
    args = parser.parse_args()
    subprocess.run("service openvswitch-switch start".split(" "))
    setLogLevel('info')
    percent_loss = float(args.loss)
    topo = MyTopology()
    net = Mininet(topo=topo, waitConnected=True, link=TCLink)
    net.start()
    config_dict = {
        'b':[1,4],
        'c':[1,2,3,4]
    }
    output_list = run_iperf(net, args.config, args.congestion, args.loss)
    if len(output_list) > 0:
        for i in output_list:
            time_list, bw_list = extract_data(i)
            index = output_list.index(i)
            plot_graph(time_list, bw_list, f'./q2_plots/plot_config_{args.config}_host_{config_dict[args.config][index]}_congestion_{args.congestion}_loss_{args.loss}.png')

    CLI(net)
    net.stop()
    # subprocess.run("killall -9 iperf")  # This kills all running iperf processes
    subprocess.run("service openvswitch-switch stop".split(" "))
    # subprocess.run("sudo mn -c")
if __name__ == '__main__':
    main()
