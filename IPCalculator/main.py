from pydantic import BaseModel
from fastapi import FastAPI

description = """
The first networks assignment is an IP address calculator that can return information on an IP address, subnet an IP address, and supernet 
multiple IP addresses.

The IP addresses and subnet masks must be enclosed in double quotes, for example `"136.206.18.7"` or `"255.255.255.192"`

## IP Calculator

The IP calculator takes an **ip address** and returns the class of the address.

Once it has found the class of the IP address it will also return:
* The number of networks,
* The number of hosts,
* The first IP address,
* And the last IP address

belonging to that class.

For example, if you entered the IP address `"172.16.52.63"` in a POST request,
you would recieve the following data in JSON format:

`{
  "class": "B",
  "num_networks": 16384,
  "num_hosts": 65536,
  "first_address": "128.0.0.0",
  "last_address": "191.255.255.255"
}`

This is an example of a class B address. A class C address such as `"210.130.0.0"` will return:

`{
  "class": "C",
  "num_networks": 2097152,
  "num_hosts": 256,
  "first_address": "192.0.0.0",
  "last_address": "223.255.255.255"
}`

## Subnet Calculator

Subnetting is used to make it easier to manage and maintain a large block of IP addresses by breaking them down into smaller blocks of IP 
addresses. This will make them easier to maintain and it will be easier to control any problems that arise as it will be localised in one 
block instead of causing problems for the entire network.

The Subnet Calculator takes an **ip address** and **subnet mask** and returns:

* The ip address in CIDR notation. This is the IP address followed by the number of network bits of the subnet mask
* The number of subnets on the network. This is how many addresses the IP address can be split into.
* For each subnet how many addressable hosts there are. This is the range of the subnet minus two since the first and last address are the network and
 broadcast address and are not addressable hosts.
* The addresses of the valid subnets.
* The broadcast address of each subnet. This is the last address on the network and is used to communicate with all hosts on the network.
* The first and last valid address on each subnet.

For example if you entered the IP address `"172.16.0.0"` and the subnet mask `"255.255.192.0"` you would return:

`{
  "address_cidr": "172.16.0.0/18",
  "num_subnets": 4,
  "addressable_hosts_per_subnet": 16382,
  "valid_subnets": [
    "172.16.0.0",
    "172.16.64.0",
    "172.16.128.0",
    "172.16.192.0"
  ],
  "broadcast_addresses": [
    "172.16.63.255",
    "172.16.127.255",
    "172.16.191.255",
    "172.16.255.255"
  ],
  "first_addresses": [
    "172.16.0.1",
    "172.16.64.1",
    "172.16.128.1",
    "172.16.192.1"
  ],
  "last_addresses": [
    "172.16.63.254",
    "172.16.127.254",
    "172.16.191.254",
    "172.16.255.254"
  ]
}`

## Supernet Calculator

Supernetting is used if someone wants to request a block of IP addresses that is larger than the block size of one class but smaller 
than the block size of the next class. In this case, the person requesting the addresses is given multiple blocks of a class's addresses 
which is joined together into one block.

The Supernet Calculator takes a **list of ip addresses** and combines them into one and returns:

* The supernet network address in CIDR notation. This is the smallest IP address from the list followed by 
the number of network bits of the supernet address.
* The mask of the supernet address. This is found by comparing each address and adding a '1' bit to the mask in binary if each address matches and
 stopping when the bits of each address no longer match.

If `["192.0.0.0", "192.0.1.0", "192.0.2.0", "192.0.3.0"]` 
was the list of IP addresses given it would return:

`{
  "address": "192.0.0.0/22",
  "mask": "255.255.252.0"
}`
"""

tags_metadata = [
    {
        "name": "ipcalc",
        "description": "Enter an IP address in double quotes.",
    },
    {
        "name": "subnet",
        "description": "Enter an IP address and its subnet mask.",
    },
    {
        "name": "supernet",
        "description": "Enter a list of IP addresses.",
    },
]

app = FastAPI(
    title='IP Address Calculator',
    description=description,
    openapi_tags=tags_metadata
)

# post request body for the IP calculator
class IPcalcItem(BaseModel):
    address: str # for the IP calculator it only takes one argument: an ip address enclosed in a string

# post request body for the subnet mask calculator
class SubnetItem(BaseModel):
    address: str
    mask: str

# post request body for the supernet calculator
class SupernetItem(BaseModel):
    addresses: list

# hardcoding the host and network bits for each class with a dictionary
# given in assignment description
classes = {
    'A' : {
    'network_bits' : 7,
    'host_bits' : 24
    },

    'B' : {
    'network_bits' : 14,
    'host_bits' : 16
    },

    'C' : {
    'network_bits' : 21,
    'host_bits' : 8
    },

    'D' : {
    'network_bits' : 'N/A',
    'host_bits' : 'N/A'
    },

    'E' : {
    'network_bits' : 'N/A',
    'host_bits' : 'N/A'
    },
}

#function to return how many network bits a class has
def networks(letter): # takes in the class
    try:
        return 2 ** (classes[letter]['network_bits']) # access the dictionary entry for the class and return 2 ** class network bits
    except TypeError: #type error will occur for class D and E as its networks bits is not an integer
        return 'N/A'

#function to return how many host bits a class has
def hosts(letter):
    try:
        return 2 ** (classes[letter]['host_bits']) # access the dictionary entry for the class
    except TypeError: #type error will occur for class D and E as its networks bits is not an integer
        return 'N/A'

#function to find out which class an ip address belings to
def which_class(ip):

    first_num = int(ip.split(".")[0]) #split the ip on the '.' and take the first number

    if first_num >= 0 and first_num <= 127: # the class is found by seeing which range the first number lies between
        return 'A'
    elif first_num >= 128 and first_num <= 191:
        return 'B'
    elif first_num >= 192 and first_num <= 223:
        return 'C'
    elif first_num >= 224 and first_num <= 239:
        return 'D'
    elif first_num >= 240 and first_num <= 255:
        return 'E'

# function to return the range of the ip addresses for a class
def ip_range(letter): # takes the class
    if letter == 'A': # check if the class passed in is equal to A
        return '0.0.0.0', '127.255.255.255' # return the smallest and largest ip addresses for class A
    elif letter == 'B': # repeat the check for all other classes (B -> E)
        return '128.0.0.0', '191.255.255.255'
    elif letter == 'C':
        return '192.0.0.0', '223.255.255.255'
    elif letter == 'D':
        return '224.0.0.0', '239.255.255.255'
    elif letter == 'E':
        return '240.0.0.0', '255.255.255.255'

@app.post("/ipcalc", tags=['ipcalc'])
async def ipcalc(item : IPcalcItem):
    ipclass = which_class(item.address) # find which class the ip address is
    min, max = ip_range(ipclass) # find the range of the ip addresses for the class
    # return the ipcalc information in JSON format
    return { # return the class, number of networks, number of hosts, first address and last address of the ip address
	"class": '{}'.format(ipclass),
    "num_networks": networks(ipclass),
    "num_hosts": hosts(ipclass),
    "first_address": '{}'.format(min),
    "last_address": '{}'.format(max),
    }
    

#------------------------------------------------------------------------------

#function to find the ip address in CIDR notation
def cidr(ip, mask):
    split_mask = mask.split(".") # split the subnet mask into a list of the numbers
    
    binary_mask = '' # create a string that will hold the binary version of the subnet mask
    for elem in split_mask: # go through each number in the mask
        bin_elem = bin(int(elem))[2:].zfill(8) # convert the number into binary and zfill(8) ensures the binary number will be 8 bits
        binary_mask += str(bin_elem) # add the binary number to the binary mask

    host_bits = 0
    while binary_mask[host_bits] != '0': # loop through the binary mask to count how many ones are at the start -> host bits
        host_bits += 1
    #binary_mask.count('1')

    return ip + '/' + str(host_bits), host_bits # return the ip address with the CIDR notation and the number of host bits

# function to return the number of subnets there will be
def num_subnets(host_bits):
    bits = host_bits % 8 # find the leftover bits that arent in a byte of 8 ones
    return 2 ** bits

# function to return the number of hosts each subnet will have
def num_hosts(host_bits):
    bits = 32 - host_bits # number of zero bits in the subnet mask
    return (2 ** bits) - 2 # minus two since the first (network) and last (broadcast) address are not addressable hosts

# function that will return a list of the valid subnets
def valid_subnets(ip, mask, host_bits): # function takes the ip address, subnet mask, and number of host bits
    split_mask = mask.split('.') # split the subnet mask on the '.'
    position = 0
    subnet_mask = 0
    while position < 4: # loop through the split subnet mask
        if split_mask[position] != '255': # find the first element that isnt '255'
            subnet_mask = int(split_mask[position]) # set the subnet_mask to that element
            break # found the element so break out of the loop
        position += 1
    block = 256 - subnet_mask # find the block size of each subnet

    split_ip = ip.split('.') # split the ip address on the '.'
    subnets = [] # create a list to hold the subnets 
    
    i = 0
    while i < num_subnets(host_bits): # find how many subnets there will be and loop through the number
        subnets.append('.'.join(split_ip)) # add the ip address to the list of subnets
        split_ip[position] = str(int(split_ip[position]) + block) # increase the ip address by the block size
        i += 1

    return subnets, block, position # return the list of subnets, the block size, and the position of the subnet mask

# function that finds the first address of each subnet
def first_addresses(subnets): # function takes the list of subnets and the position of the subnet mask
    first_addresses = [] # create a new list
    for subnet in subnets:
        split_subnet = subnet.split('.') # split the subnet
        split_subnet[3] = str(int(split_subnet[3]) + 1) # increase the last number by one
        first_addresses.append('.'.join(split_subnet)) # rejoin the subnet and add it to the list of first addresses

    return first_addresses

# function that returns the broadcast addresses
def broadcast_addresses(subnets, position, block_size):
    broadcast_addresses = []
    for subnet in subnets:
        split_subnet = subnet.split('.')
        split_subnet[position] = str(int(split_subnet[position]) + block_size - 1) # increase the subnet by the block size
        if position != 3: # if the position of the subnet mask isnt the last number
            new_position = position + 1
            while new_position <= 3: # loop through the remaining numbers
                split_subnet[new_position] = '255' # change each following number to '255'
                new_position += 1
        broadcast_addresses.append('.'.join(split_subnet)) # add the updated address to the list of broadcast addresses

    return broadcast_addresses

# function to return the list of last addresses of each subnet
def last_addresses(subnets, position, block_size):
    last_addresses = []
    for subnet in subnets:
        split_subnet = subnet.split('.')
        if position == 3: # if the subnet mask is the last number
            split_subnet[position] = str(int(split_subnet[position]) + block_size - 2) # increase by the block minus 2, 
                                                                                       # since the last address is the broadcast address
        else:
            split_subnet[position] = str(int(split_subnet[position]) + block_size - 1) # increase by the block minus 1
            new_position = position + 1
            while new_position < 3: # loop through the numbers until you reach the last one
                split_subnet[new_position] = '255' # update them to be 255
                new_position += 1

            split_subnet[new_position] = '254' # finally change the last number to 254, since 255 is the broadcast address
        last_addresses.append('.'.join(split_subnet)) # rejoin the subnet and add it to the list

    return last_addresses

@app.post("/subnet", tags=['subnet'])
async def subnet(item : SubnetItem):
    ip, mask = item.address, item.mask
    cidr_notation, host_bits = cidr(ip, mask)
    subnets, block_size, position = valid_subnets(ip, mask, host_bits)
    return {
	"address_cidr" : '{}'.format(cidr_notation),
    "num_subnets": num_subnets(host_bits),
    "addressable_hosts_per_subnet": num_hosts(host_bits),
    "valid_subnets": subnets,
    "broadcast_addresses": broadcast_addresses(subnets, position, block_size),
    "first_addresses": first_addresses(subnets),
    "last_addresses": last_addresses(subnets, position, block_size)
    }

#--------------------------------------------------------------------------------------

# function that will return the smallest ip address from a list of ip addresses
def min_address(addresses):
    int_addresses = [] # create a list to store the addresses as integers
    for address in addresses: # loop through the addresses
        tmp_address = ''
        for num in address:
            if num != '.':
                tmp_address += num # add the numbers to the address without the '.'
        int_addresses.append(int(tmp_address)) # add the address as an integer to the list

    return int_addresses.index(min(int_addresses)) # return the index of the smallest address

# function to return the supernet in CIDR notation
def supernet_cidr(addresses):
    bin_addresses = [] # create a list to store the addresses in binary
    for address in addresses:
        split_address = address.split(".")
        
        bin_address = ''
        for elem in split_address: # go through each element in the split address
            bin_address += str(bin(int(elem))[2:].zfill(8)) # convert the number into binary and convert back to a string and add to address
        bin_addresses.append(bin_address) # add the address in binary to the list

    i = 0
    count = 0
    while i < 32: # loop through the length of the binary address
        same = True # set same to True
        matching_bit = bin_addresses[0][i] # take the first address and compare its bits with the the other addresses
        for elem in bin_addresses:
            if elem[i] != matching_bit: # if one of the addresses bits doesnt match the first address' bit
                same = False # set same to be False and break the loop
                break
        
        if same == True: # if same stays true, the bit in all the addresses match
            count += 1 # increase the count
        else:
            break # if same has changed, stop counting and break the loop
        i += 1

    supernet = str(addresses[min_address(addresses)]) + '/' + str(count) # combine the smallest address with the count
    
    return supernet, count # return the supernet in CIDR notation, and the count (host bits)

# function to return the network mask
def network_mask(count): # function takes the count of the host bits
    binary_mask = ('1' * count) + ('0' * (32 - count)) # create the network mask in binary using the no. of host bits
    
    network_mask = '' # create a string to hold the network mask
    i = 0
    while i < 4: # loop through the address
        network_mask += str(int(binary_mask[(8 * i) : (8 * (i + 1))], base=2)) # take the address in groups of eight, convert to int, add to string
        network_mask += '.' # add a '.' to seperate the numbers
        i += 1

    network_mask = network_mask[:-1] # remove the last '.' from the address
    return network_mask

@app.post("/supernet", tags=['supernet'])
async def supernet(item: SupernetItem):
    supernet, count = supernet_cidr(item.addresses)
    # return in JSON the supernet address and mask
    return {
        "address": '{}'.format(supernet),
	    "mask": '{}'.format(network_mask(count))
    }
