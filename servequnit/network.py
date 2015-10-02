import random, socket, os

def get_external_address(routable=True):
    """
    Really messy way of determining which IP is network accessible.  This is
    slow and not particularly reliable, but using the machine's hostname results
    in the local address being returned.
    """
    maybe_external = ['8.8.8.8', ]
    for host in maybe_external:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((host, 80))
            name_or_ip = sock.getsockname()[0]

            if name_or_ip.startswith('127.'):
                continue
            elif name_or_ip == 'localhost':
                continue
            else:
                return name_or_ip
        except socket.error:
            pass
        finally:
            sock.close()

    raise Exception("could not find an external address")

def get_random_port():
    """Can collide anyway."""
    return random.randint(1025, pow(2, 16))
