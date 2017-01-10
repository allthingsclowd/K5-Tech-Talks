from k5contractsettingsV8 import *
from k5APIwrappersV14 import *

k5token = get_scoped_token(adminUser, adminPassword, contract, demoProjectid, region).headers['X-Subject-Token']


# build a server from the API only

# Create a network

net_id = create_network(k5token, "HelloK5APIWorld-net2", az1 , region).json()['network'].get('id')
print "\nNetwork ID ", net_id

# Create a subnet

subnet_id =  create_subnet(k5token, "HelloK5APIWorld-subnet2", net_id, 4, "192.168.100.0/24", az1, region).json()['subnet'].get('id')
print "\nSubnet ID ", subnet_id

# Create a router

router_id = create_router(k5token,"HelloK5APIWorld-subnet2", True, az1, region).json()['router'].get('id')
print "\nRouter ID ", router_id
# Attach subnet to router

add_interface = add_interface_to_router(k5token, router_id, subnet_id, region)
print "\nInterface Added to Router  ", add_interface.json()

# Attach router to  external network (set gateway)

add_ext_gateway = update_router_gateway(k5token, router_id, "df8d3f21-75f2-412a-8fd9-29de9b4a4fa8", region)
print "\nExt Gateway ", add_ext_gateway.json()

# Create ssh-key pair

newkp = create_keypair(k5token, "HelloK5APIWorld-Keypair2", demoProjectid, az1, region).json()['keypair']
print "\nNew Keypair ", newkp
newkp_id = newkp.get('id')
newkp_pvk = newkp.get('private_key')
newkp_pbk = newkp.get('public_key')
newkp_name = newkp.get('name')

# Create security group
security_group = create_security_group(k5token, "HelloK5APIWorld-SecurityGroup2", "An API Demo Security Group", region).json()['security_group']
print "\nNew Security Group ", security_group
sg_id = security_group.get('id')
sg_name = security_group.get('name')
# add rules to security group - ssh, rdp & icmp

ssh = create_security_group_rule(k5token, sg_id, "ingress", "22", "22", "tcp", region)
rdp = create_security_group_rule(k5token, sg_id, "ingress", "3389", "3389", "tcp", region)
icmp = create_security_group_rule(k5token, sg_id, "ingress", "0", "0", "icmp", region)
print "\nSecurity Group Rules \nSSH\n", ssh.json(), "\nRDP\n", rdp.json(), "\nICMP\n", icmp.json()


imageid = 'ffa17298-537d-40b2-a848-0a4d22b49df5'
flavorid = '1101'

# create server
serverdetails = create_server(k5token, "HelloK5APIWorld-server2", imageid, flavorid, newkp_name, sg_name, az1, "3",  net_id, demoProjectid, region)

print "\nServer Details\n", serverdetails, "\nJSON : \n", serverdetails.json(), "\nPrivate Key:\n",  newkp_pvk





# create a floating ip

# assign floating ip to  server port
