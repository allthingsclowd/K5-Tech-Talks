from k5contractsettingsV8 import *
from k5APIwrappersV16 import *

def create_vpn_prereqs(k5token, name, cidr, demoProjectid, ext_net, az, region):
     # build a server from the API only
    name = name + "-" + randomword(8)
    # Create a network

    net_id = create_network(k5token, name, az, region).json()['network'].get('id')
    print "\nNetwork ID ", net_id

    # Create a subnet

    subnet_id = create_subnet(k5token, name, net_id, 4, cidr, az, region).json()['subnet'].get('id')
    print "\nSubnet ID ", subnet_id

    # Create a router

    router_id = create_router(k5token, name, True, az, region).json()['router'].get('id')
    print "\nRouter ID ", router_id

    add_ext_gateway = update_router_gateway(k5token, router_id, ext_net, region)
    print "\nExt Gateway ", add_ext_gateway.json()

    # Create security group
    security_group = create_security_group(k5token,  name, "VPNaaS Security Group created by API", region).json()['security_group']
    print "\nNew Security Group ", security_group
    sg_id = security_group.get('id')
    sg_name = security_group.get('name')
    # add rules to security group - ssh, rdp & icmp

    ssh = create_security_group_rule(k5token, sg_id, "ingress", "22", "22", "tcp", region)
    rdp = create_security_group_rule(k5token, sg_id, "ingress", "3389", "3389", "tcp", region)
    icmp = create_security_group_rule(k5token, sg_id, "ingress", "0", "0", "icmp", region)
    print "\nSecurity Group Rules \nSSH\n", ssh.json(), "\nRDP\n", rdp.json(), "\nICMP\n", icmp.json()

    # create a port for the server
    port_id = create_port(k5token, name, net_id, sg_id, az, region).json()['port'].get('id')

    subnet_gateway = add_port_to_router(k5token, router_id, port_id, region)
    print "\nInterface Added to Router  ", subnet_gateway.json()

    # get a global ip for this server port
    global_ip = create_global_ip(k5token, ext_net, port_id, az, region).json()['floatingip'].get('floating_ip_address')

    return (name, global_ip, subnet_id, cidr, router_id)


def create_vpn(k5token, name, peercidr, peeradr, subnet_id, router_id, psk, ext_net, az, region):

    vpnservice_id = create_vpn_service(k5token, name, router_id, subnet_id, az, region).json()['vpnservice'].get('id')
    print "\nVPN Service ID ", vpnservice_id

    ikepolicy_id = create_ike_policies(k5token, name, "sha1", "aes-128", "7200", "v1", "group5", "main", az, region).json()['ikepolicy'].get('id')
    print "\nIKE Policy ID ", ikepolicy_id

    ipsecpolicy_id = create_ipsec_policy(k5token, name, "esp", "sha1", "aes-256", "tunnel", "group5",  "7200", az, region).json()['ipsecpolicy'].get('id')
    print "\nIPSec Policy ID ", ipsecpolicy_id

    #while (show_vpn_service(k5token, vpnservice_id, region).json()['vpnservice'].get('status') != "ACTIVE"):
       # print "VPN Service Status ", show_vpn_service(k5token, vpnservice_id, region).json()['vpnservice'].get('status')

    vpn_site_connection_id = create_ipsec_site_connections(k5token, name, vpnservice_id, ikepolicy_id, ipsecpolicy_id, peeradr, peercidr, psk, az, region)

    print "\nVPN Connection ID ", vpn_site_connection_id

    return #vpn_site_connection_id


def main():

    k5token = get_scoped_token(adminUser, adminPassword, contract, demoProjectid, region).headers['X-Subject-Token']
    print k5token

    k5token2 = get_scoped_token(adminUser, adminPassword, contract, demoProjectid2, region).headers['X-Subject-Token']
    print k5token2

    SiteA = create_vpn_prereqs(k5token, "SiteA", "192.168.1.0/24", demoProjectid,  extaz1, az1, region)

    print SiteA

    SiteB = create_vpn_prereqs(k5token2, "SiteB", "10.10.1.0/24", demoProjectid2, extaz2, az2, region)

    print SiteB

    print create_vpn(k5token, SiteA[0], SiteB[3], SiteB[1], SiteA[2], SiteA[4], "secretpassword", extaz1, az1, region)

    print create_vpn(k5token2, SiteB[0], SiteA[3],  SiteA[1], SiteB[2], SiteB[4], "secretpassword", extaz2, az2, region)


if __name__ == "__main__":
    main()
