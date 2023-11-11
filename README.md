# CS-433_Assignment2

Ayush Chaudhari       &emsp; &emsp; &emsp; 20110042

Zeeshan Snehil Bhagat &emsp; 20110242
## Basic Setup
If you get any OpenFlow error:
* Run "sudo apt-get install openvswitch-testcontroller"
* Run "sudo cp /usr/bin/ovs-testcontroller /usr/bin/ovs-controller"

<br>
Our code already starts and ends "service openvswitch-switch", so no need to start it, instead start it again if you need it after our code has finished running.
<br><br>
Program related instructions are in the report itself.
<br>

## Debugging 

Sometimes, the program may throw some error or may take some more time (tolerable limit would 1-2 min as per our system). In that case do the following:<br>
* If you are in mininet and the code is running for very long, Ctrl+C. Then Ctrl+D. Then rerun the code.
* If the topology fails to build up (especially in question 2), run "sudo mn -c", then rerun the code.
<br>

## Part I: Implement the routing functionality in mininet.

## Part II: Throughput for different congestion control schemes.
Note: We plotted the graphs of the clients only and not stored the iperf bandwidth tables anywhere.
