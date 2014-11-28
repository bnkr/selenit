Selenibench
===========

An attempt at automating browsers for performance testing.

Essentially this is to make the process faster, not necessarily better.
Benchmarking websites is something which selenium is not really that great for
because you don't really get enough data but you can get some decent profiling
done.

Note that networking makes a big difference here.  Consider changing the packet
scheduler on your selenium machine to match the kind of users you are optimising
for::

  # Add 150ms delay to every packet on eth0.
  tc qdisc add dev eth0 root netem delay 150ms
