# RIPE Atlas dyndns server

This piece of code runs a variation of "dynamic dns" functionality: given a set
of host names in a zone, it answers with "the next answer" from a predefined
list, in round-robin fashion.

The intended use is in conjunction with [RIPE Atlas](https://atlas.ripe.net/):
if one needs measurements that have multiple targets, then one measure against
a target _name_, which resolves to a different IP every time.

We measured that it's capable of answering hundreds of queries per second on
single server - single thread mode which is enough for our purposes. More
servers and more threads further increase capacity and resiliency, though as a
consequence the clients would get the same answer multiple times (which may be
ok, depending on the specific needs).

# Usage

The module runs as a [PowerDNS "backend"](https://docs.powerdns.com/md/authoritative/backend-pipe/):
it runs as a standalone process (potentially multi-threaded), receives
translated DNS queries from PowerDNS, provides appropriate answers via the
backend API, which in turn are translated back into DNS packets by PowerDNS.

Sample configuration is included in `config/pdns.conf`. You can and should
tweak the settings used (like log and data directories, server names, ...)
in `settings.py`

# Acknowledgements

Precursors, and early implementations for this code include [Emile Aben's 
"Scapy DNS Ninja"](https://github.com/emileaben/scapy-dns-ninja) and
[Zeerover DNS](https://github.com/USC-NSL/RIPE2015HackAThon). 
