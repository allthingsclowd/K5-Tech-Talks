from k5contractsettingsV8 import *
from k5APIwrappersV15 import *


def create_k5_server(k5token, name, cidr, project, az, ext_net, imageid, flavorid, volsize, count ):
    # build a server from the API only
    name = name + "-" + randomword(8)
    # Create a network

    net_id = create_network(k5token, name, az , region).json()['network'].get('id')
    print "\nNetwork ID ", net_id

    # Create a subnet

    subnet_id = create_subnet(k5token, name, net_id, 4, cidr, az, region).json()['subnet'].get('id')
    print "\nSubnet ID ", subnet_id

    # Create a router

    router_id = create_router(k5token, name, True, az, region).json()['router'].get('id')
    print "\nRouter ID ", router_id
    # Attach subnet to router

    add_interface = add_interface_to_router(k5token, router_id, subnet_id, region)
    print "\nInterface Added to Router  ", add_interface.json()

    add_ext_gateway = update_router_gateway(k5token, router_id, ext_net, region)
    print "\nExt Gateway ", add_ext_gateway.json()

    # Create ssh-key pair

    newkp = create_keypair(k5token, name, project, az, region).json()['keypair']
    print "\nNew Keypair ", newkp
    newkp_id = newkp.get('id')
    newkp_pvk = newkp.get('private_key')
    newkp_pbk = newkp.get('public_key')
    newkp_name = newkp.get('name')
    print "\nPrivate Key:\n",  newkp_pvk

    # Create security group
    security_group = create_security_group(k5token,  name, "Demo Security Group created by API", region).json()['security_group']
    print "\nNew Security Group ", security_group
    sg_id = security_group.get('id')
    sg_name = security_group.get('name')
    # add rules to security group - ssh, rdp & icmp

    ssh = create_security_group_rule(k5token, sg_id, "ingress", "22", "22", "tcp", region)
    rdp = create_security_group_rule(k5token, sg_id, "ingress", "3389", "3389", "tcp", region)
    icmp = create_security_group_rule(k5token, sg_id, "ingress", "0", "0", "icmp", region)
    print "\nSecurity Group Rules \nSSH\n", ssh.json(), "\nRDP\n", rdp.json(), "\nICMP\n", icmp.json()
    ServerDetails = "Private Key:\n=========\n" +str(newkp_pvk)  + "\n\nServer Details\n=========\n"
    # simple little routine to ensure only 1 global ip is assigned per group of servers
    while count > 0:
        if count == 1:
            public = True
        else:
            public = False
        NewServer = create_server(k5token, name, net_id, sg_id, ext_net, imageid, flavorid, newkp_name, sg_name, volsize, public, az, region)
        ServerDetails = ServerDetails + str(count) + ". " + NewServer + "\n"
        count = count - 1
    ServerDetails = ServerDetails + "\n=========\n"
    return ServerDetails

def create_server(k5token, name, net_id, sg_id, ext_net, imageid, flavorid, newkp_name, sg_name, volsize, public, az, region):

    name = name + "-" + randomword(8)
    # create a port for the server
    port = create_port(k5token, name, net_id, sg_id, az, region).json()['port']
    port_id = port.get('id')
    port_ip = port['fixed_ips'][0].get('ip_address')
    global_ip = "None"

    print k5token, name, imageid, flavorid, newkp_name, sg_name, az, volsize,  port_id, project, region

    # get a global ip for this server port
    if public:
        global_ip = create_global_ip(k5token, ext_net, port_id, az, region).json()['floatingip'].get('floating_ip_address')

    # create server
    server_id = create_server_with_port(k5token, name, imageid, flavorid, newkp_name, sg_name, az, volsize,  port_id, demoProjectid, region).json()['server'].get(id)
    #print create_server_with_port(k5token, name, imageid, flavorid, newkp_name, sg_name, az, volsize,  port_id, demoProjectid, region).json()

    #serverdetails = show_server(k5token, server_id, demoProjectid, region)

    print "\nPrivate IP:\n",  port_ip, "\nGlobal IP \n", global_ip
    return "[ "+ str(name) + " | " + str(port_ip) + " | " + str(global_ip) + "]"

def main():
    k5token = get_scoped_token(adminUser, adminPassword, contract, demoProjectid, region).headers['X-Subject-Token']
    print k5token

    print create_k5_server(k5token, "demo", "192.168.1.0/24", demoProjectid, az1, extaz1, "ffa17298-537d-40b2-a848-0a4d22b49df5", "1101", "3" , 3)


if __name__ == "__main__":
    main()





