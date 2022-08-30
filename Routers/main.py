from pydantic import BaseModel, Field
from fastapi import FastAPI

description = """
The second networks assignment recreates a network of routers, and allows the user to add and remove routers and create and remove connections between
 the routers.

When entering the name of a router, the name must be enclosed in double quotes, like `"A"`.

## 1. Add a Router
The addrouter endpoint takes a router and adds it to the already existing network of routers. The user will enter the name of the 
router and the endpoint will return the status of the action.
If the router is already in the network, the user will receive an error message, or else they will receive a success message.

For example if the user entered the POST request:
`{
    "name": "A"
}`
and the router A wasn't already in the network, they would receive the response:
`{
	"status": "success"
}`.
 If A was already in the network, they would receive the response:
 `{
	"status": "Error, node already exists"
}`

## 2. Add a Connection between two Routers
The addconnection endpoint takes two routers that must already be part of the network, and creates a connection between them.
If there is already an existing connection, the endpoint will update the connection with a new weight for the connection. The user will 
enter the name of the first router, the name of the second router, and the weight of the connection between them, and the endpoint will return 
the status of the action.

For example if the user entered the POST request:
`{
    "from": "A",
    "to": "C",
    "weight": 10
}`,
if there is no connection between the routers, the endpoint will create a connection and return the status:
`{
    "status": "success"
}`.
If there is already a connection, the endpoint will update the connection with the new weight of the connection and return the status:
`{
    "status": "updated"
}`.
The final return option is if either or both of the routers are not in the network. In that case the endpoint will return:
`{
    "status": "Error, router does not exist"
}`.

## 3. Remove a Router
The removerouter endpoint takes a router and removes it from the network of routers. The user enters the name of the router they wish to remove 
as input and the endpoint will return the status of the removal in JSON format.

If the user wants to remove the router "D" from the network, the input would be:
`{
    "name": "D"
}`.
The endpoint will remove the router from the network and return the status
`{
    "status": "success"
}`. 
Even if the router is not in the network, the status of the action will still be "success", since the user has still achieved what
they want, wish is to not have that router in the network.

## 4. Remove a Connection between two Routers
The removeconnection endpoint takes two routers and removes the connection that exists between them in the network. The user enters 
the two routers that they want to disconnect, and the endpoint returns the status of the action.

If the user wanted to remove the connection between routers A and D, they would enter the following in the POST request:
`{
    "from": "A",
    "to": "D"
}`.
The endpoint will remove the connection between the two routers and return:
`{
    "status": "success"
}`. If there is no connection between the routers already, or if the routers aren't in the network, the returned status will still be 
"success", as the user has still gotten what they wanted, ehich is no connection between the routers entered. 

## 5. Find the Shortest Path between two Routers
The route endpoint takes two routers and finds the shortest path to travel between the two routers using the different routers in the network. The 
user enters the name of the first router and the name of the second router and the endpoint will find the shortest path between them and 
return the weight of the journey and the path taken by travelling through the different routers.

For example if the user wanted to find the path taken between router "A" and router "C", they would enter the following in a POST request:
`{
  "from": "A",
  "to": "C"
}`.

The endpoint would return:
`{
  "from": "A",
  "to": "C",
  "weight": 7,
  "route": [
    {
      "from": "A",
      "to": "D",
      "weight": 1
    },
    {
      "from": "D",
      "to": "E",
      "weight": 1
    },
    {
      "from": "E",
      "to": "C",
      "weight": 5
    }
  ]
}`.
If there is no path between the routers, or if one or both of the routers aren't in the network, the endpoint will return the weight of 
the path as -1, and the path taken is an empty list. If the start and end router are both the same, the endpoint will return the weight of 0 
for the path, and a list containing only the router, to show that no path has been taken.
"""
# tags for the endpoints
tags_metadata = [
    {
        "name": "Add Router",
        "description": "Add a router into the network."
    },
    {
        "name": "Connect Routers",
        "description": "Connect two routers in your network."
    },
    {
        "name": "Remove Router",
        "description": "Remove a router from your network."
    },
    {
        "name": "Remove Connection",
        "description": "Remove a connection between two routers."
    },
    {
        "name": "Find Shortest Path",
        "description": "Find the shortest path between two routers in your network."
    },
]

app = FastAPI(
    title='Routing',
    description=description,
    openapi_tags=tags_metadata
)
# base model for end points that only take the name of a router
class RouterItem(BaseModel):
    name: str = Field(title="Name of Router", example="A")

# base model for the addedge function with the two nodes and the weight of the edge
class EdgeWeightItem(BaseModel):
    from_: str = Field(None, alias='from', title="First Router", example="A")
    to: str = Field(title="Second Router", example="B")
    weight: int = Field(title="Weight of Connection", example=8)

# base model for endpoints that take an edge between two nodes
class EdgeItem(BaseModel):
    from_: str = Field(None, alias='from', title="First Router", example="A")
    to: str = Field(title="Second Router", example="E")

class Graph: # a graph represents the network

    def __init__(self):
        self.graph = {} # create a dictionary for the graph

    def addNode(self, node): # function to add a node to the graph
        self.graph[node] = {} # set the value of the node to a blank dictionary

    def addEdge(self, node1, node2, weight): # function to create a weighted edge between to nodes
        if node1 in self.graph and node2 in self.graph: # only works if both nodes are in the graph
            self.graph[node1][node2] = weight # add each node to the other node's dictionary
            self.graph[node2][node1] = weight # set the node' value to the edge weight

    def removeNode(self, node): # function to remove a node from the graph
        if node in self.graph: # check if the node is in the dictionary
            del self.graph[node] # if it is, delete it
        for othernode in self.graph: # go through the other nodes in the graph
            if node in self.graph[othernode]: # delete the node from the other node's dictionary as well
                del self.graph[othernode][node]

    def removeEdge(self, node1, node2): # function to remove an edge between two nodes
        if node1 in self.graph[node2]: # if the node is in the other node's dictionary, delete it
            del self.graph[node2][node1]
        if node2 in self.graph[node1]: # repeat the other way around
            del self.graph[node1][node2]

    def shortest_path(self, node1, node2): # function to return the shortest path between two nodes using Dijkstra's Algorithm
        visited = [] # create a list that will hold the nodes that have been visited
        path, previous = {}, {} # create two dictionaries to hold the distance to each node and the node visited before it

        for node in self.nodes(): # go through each node in the graph
            path[node] = float('inf') # set the distance to each node to infinity
            previous[node] = '' # set the previously visited node for each node to an empty string

        previous[node1] = node1 # since were starting at the first node, set the previous node to itself
        path[node1] = 0 # distance to the first node from itself is zero
        i = 0
        while i < len(path): # loop through the nodes
            temp = {} # create a temp dictionary to find the node with the shortest path that hasn't been visited yet
            for node in path: # go through each node
                if node not in visited: # add the node to the temp dictionary if it hasn't been visited
                    temp[node] = path[node]
            curr = min(temp, key=temp.get) # find the node with the smallest distance value -> node to visit next

            visited.append(curr) # add the node to the visited nodes
            for node in path: # go through each node
                if node in self.graph[curr]: # if the node is connected to the current node
                    if path[curr] + self.graph[curr][node] < path[node]: # check if the new route to the node is shorter than the current distance
                        path[node] = path[curr] + self.graph[curr][node] # update the distance if it is
                        previous[node] = curr # since you have come to the node through the current node, that is the node you visited directly previously
            i += 1
        
        if path[node2] == float('inf'): # if the distance is still infinity, there is no path to the fist node
            return -1, [] # return a distance of -1 and an empty list that represents the path taken
        else:   
            nodes_list = [] # create a list to hold the path you travelled to get to the final node
            tmp = node2 # create a tmp variable to hold the final node to go through the previous dict without changing the value of the node
            while tmp != node1:
                nodes_list.append(tmp) # go through the previous dictionary and add every node previously visited from the final node to the start
                tmp = previous[tmp]
            nodes_list.append(node1) # add the first node to the list
            nodes_list.reverse() # reverse the list so its going from the first node to the final node
            full_path = [] # create a list that will hold the final full path showing the weights and each step taken
            i = 0
            while i < len(nodes_list) - 1: # go through the list of nodes visited
                full_path.append(
                    {
                        'from': nodes_list[i], # go from one node
                        'to': nodes_list[i+1], # to the next
                        'weight': self.graph[nodes_list[i]][nodes_list[i+1]] # add the weight of the edge between the two nodes
                    }
                )
                i += 1
            return path[node2], full_path # return the distance between the two nodes and the path taken between them

    def nodes(self): # function to return a list of the nodes in the graph
        return list(self.graph.keys()) # the nodes are the keys in the graph dictionary

    def check(self, node1, node2): # function to check the status for connect function
        if node1 not in self.graph or node2 not in self.graph: # make sure both nodes are in the graph
            return "Error, router does not exist"
        elif node2 not in self.graph[node1] or node1 not in self.graph[node2]: # check if there isnt already a connection between the nodes
            return "success"
        else: # there already is a connection between the nodes so the function will just update it
            return "updated" 

# starter code that creates the graph, nodes, and edges
g = Graph()

# nodes = ['A', 'B', 'C', 'D', 'E']
# for node in nodes:
#     g.addNode(node)

# g.addEdge('A', 'D', 1)
# g.addEdge('A', 'B', 6)
# g.addEdge('B', 'C', 5)
# g.addEdge('B', 'D', 2)
# g.addEdge('B', 'E', 2)
# g.addEdge('E', 'C', 5)
# g.addEdge('D', 'E', 1)
#--------------------------------------------------------
@app.post("/addrouter", tags=["Add Router"], summary="Enter the name of the router you want to add.", response_description="The status of adding the router")
async def addrouter(item : RouterItem): # addrouter endpoint takes the name of a router to add to the network
    status = ""

    if item.name in g.nodes(): # if the node (router) is already in the graph (network)
        status = "Error, node already exists"
    else: # if it isn't in the graph, add it
        status = "success"
        g.addNode(item.name)
    
    return { # return the status of adding the router to the network
        "status": status
    }

# to create a connection between two routers
@app.post("/connect", tags=["Connect Routers"], summary="Enter the name of the two routers you want to connect.", response_description="The status of connecting the routers") 
async def connect(item : EdgeWeightItem): # end point takes two routers and the weight of the connection between them
    status = g.check(item.from_, item.to) # find out what the return status of the endpoint will be

    g.addEdge(item.from_, item.to, item.weight) # add the connection to the network
    
    return { # return whether the connection was successful or not
        "status": status
    }

# remove a router from the network
@app.post("/removerouter", tags=["Remove Router"], summary="Enter the name of the router you want to remove.", response_description="The status of removing the router")
async def removerouter(item : RouterItem): # endpoint takes the name of the router to be removed

    if item.name in g.nodes(): # check if the router is actually in the network 
        g.removeNode(item.name) # remove the router from the network

    return { # return if the router has been removed successfully
        "status": "success" # even if the router isn't in the network the status is still success because the user got what they want
    }
        
# remove a connection between two routers
@app.post("/removeconnection", tags=["Remove Connection"], summary="Enter the name of the two routers you want to remove the connection between.", response_description="The status of removing the connection")
async def removeconnection(item : EdgeItem): # takes the two routers

    if item.from_ in g.nodes() and item.to in g.nodes(): # check that both routers are in the network
        g.removeEdge(item.from_, item.to) # remove the connection between them

    return { # return if the connection has been removed successfully
        "status": "success" # even if the connection isn't in the network the status is still success because the user got what they want
    }

# find the shortest path between two routers
@app.post("/route", tags=["Find Shortest Path"], summary="Enter the name of the two routers you want to find the path between.", response_description="The path taken between the routers")
async def route(item : EdgeItem): # endpoint takes the two routers in question
    if item.from_ == item.to: # if start and end router are the same
        full_path = []
        full_path.append(item.from_) # the path taken only contains the node
        return {
            "from": item.from_,
            "to": item.to,
            "weight": 0, # the weight of the route is 0 as you haven't moved
            'route': full_path
        }
    elif item.from_ in g.nodes() and item.to in g.nodes(): # check that both routers are in the network
        weight, full_path = g.shortest_path(item.from_, item.to) # return the distance between the two routers and the path taken between them

        return { # return the start router, final router, the distance between them, and the path taken
            "from": item.from_,
            "to": item.to,
            "weight": weight,
            'route': full_path
        }
    else: # if one or both of the routers aren't in the network, return a weight of -1 and an empty list for the path taken
        return {
            "from": item.from_,
            "to": item.to,
            "weight": -1,
            'route': []
        }