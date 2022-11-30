from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from argparse import ArgumentParser
import re

parser = ArgumentParser(description="TFO tests")

parser.add_argument('--tfo', '-t',
                    help="set TCP Fast Open enabled",
                    action="store_true") 

parser.add_argument('--delay',
                    type=float,
                    help="Link propagation delay (ms)",
                    required=True)

args = parser.parse_args()

NUM_TRIALS = 5

class MyTopo( Topo ):
    "Simple topology example."

    def build(self, n=2):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        delay = "{0}ms".format(args.delay)
        self.addLink(h1, h2, delay=delay)
        

#topos = { 'mytopo': ( lambda: MyTopo() ) }

def tcp_fastopen():
    net = Mininet(topo = MyTopo(), link = TCLink)
    net.start()
    h1, h2 = net.get('h1', 'h2')
    #client = h1.popen("ping -c 5 {0}".format(h2.IP(), stdout=PIPE, stderr=PIPE))
    #stdout, stderr = client.communicate()
    #print(stdout)
    #print(stderr)
    if args.tfo:
        print("TFO enabled")
        proc = h2.popen("sudo python3 webserver.py --tfo")
    else:
        proc = h2.popen("sudo python3 webserver.py")
    s=0
    for i in range(NUM_TRIALS):
        getstuff = h1.popen("time wget -q -O - http://{0}:8000/bfg2k/arun-y99.github.io".format(h2.IP(),stdout=PIPE, stderr=PIPE))
        stdout, stderr = getstuff.communicate()
        #print(stdout)
        print('Time data')
        print(stderr)
        #m = re.search(b'real\t[0-9]m(.*)s', stderr)
        m = re.search(b'[0-9]:(.*)elapsed', stderr)
        print(m)
        time = float(m.group(1))
        print(time)
        s+=time
    print("Average RTT: {0}".format(s/NUM_TRIALS))
    proc.kill()

if __name__ == "__main__":
    tcp_fastopen()