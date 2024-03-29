Configuration
==============

Mini-NDN uses a configuration file describing the topology and its parameters to setup a network.
It can be generated by the GUI or written by hand or scripts.

## Configuration file format:

### The [nodes] section:

At the bare minimum, the node section describes the nodes present in the topology.

    [nodes]
    a: _
    b: _

Additionally each node can take the following parameters:

* app   : Default application(s) to be started on a node (specify '_' if no app needs to be started - required).
The app is the only parameter which needs double quotes (see example below).

* cpu   : Amount of cpu available to a node (0.00 - 1.00), optional

* mem   : Amount of memory available to a node in KB

* cache : Amount of cache memory available to a node in KB


    e.g.)

    [nodes]
    a: _ cpu=0.3
    b: app="sample app 1; sampleapp2.sh" cpu=0.3

### The [links] section:

The links section describes the links in the topology.

    e.g.)

    [links]
    a:b delay=10ms

This would create a link between a and b. 'b:a' would also result in the same.
The following parameters can be configured for a node:

* delay : Delay parameter is a required parameter which defines the delay of the link (1-1000ms)

* bw    : Bandwidth of a link (<1-1000> Mbps)

* loss  : Percentage of packet loss (<1-100>)

### Example configuration file

    [nodes]
    a: _ cpu=0.3
    b: app="sampleApp1; ./sampleApp2.sh" cpu=0.3
    [links]
    a:b delay=10ms bw=100

Note that `sampleApp1` and `sampleApp2` must be either installed in the system (ex: /usr/bin)
or an absolute path needs to be given.

See `ndn_utils/topologies` for more sample files
