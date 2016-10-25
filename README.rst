RIPE Atlas dyndns server
========================

|Build Status|

.. |Build Status| image:: https://travis-ci.org/RIPE-NCC/atlas-dyndns.png?branch=master
   :target: https://travis-ci.org/RIPE-NCC/atlas-dyndns

This piece of code runs a variation of “dynamic dns” functionality:
given a set of host names in a zone, it answers with “the next answer”
from a predefined list, in round-robin fashion.

The intended use is in conjunction with `RIPE Atlas`: if one needs
measurements that have multiple targets, then one measure against a
target *name*, which resolves to a different IP every time.

We measured that it’s capable of answering hundreds of queries per
second on single server - single thread mode which is enough for our
purposes. More servers and more threads further increase capacity and
resiliency, though as a consequence the clients would get the same
answer multiple times (which may be ok, depending on the specific
needs).

Usage
=====

The module runs as a `PowerDNS “backend”`: it runs as a standalone
process (potentially multi-threaded), receives translated DNS queries
from PowerDNS, provides appropriate answers via the backend API, which
in turn are translated back into DNS packets by PowerDNS.


Install
=====

``pip install ripe.atlas.dyndns``

It will be installed either in your virtualenv or system-wide.

Sample configuration can be generated:

* The backend config:
  ``atlas-pdns-pipe --sample-config > /path/to/atlas-dyndns.conf``

* PowerDNS config:
  ``atlas-pdns-pipe --sample-config-pdns > pdns.conf``

You should tweak the settings (like log and data directories, server
names, …)

You will also find the ``create-routed-list`` command useful. It can help you creating the lists of IP addresses that will used in round-robin


Stats
==========

The sample munin scripts are located in the ``munin`` directory.

Acknowledgements
================

Precursors, and early implementations for this code include `Emile
Aben’s “Scapy DNS Ninja”`_ and `Zeerover DNS`_.

.. _RIPE Atlas: https://atlas.ripe.net/
.. _PowerDNS “backend”: https://docs.powerdns.com/md/authoritative/backend-pipe/
.. _Emile Aben’s “Scapy DNS Ninja”: https://github.com/emileaben/scapy-dns-ninja
.. _Zeerover DNS: https://github.com/USC-NSL/RIPE2015HackAThon
