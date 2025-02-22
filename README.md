# Peer to Peer Chat Program

## Overview

The project implements a peer to peer chat program in Python (version 3.12.2, any version above 3 would work).
With this program, a user can connect to peers over the TCP, send and receive messages simultaneously in real time, retrieve its own list of peers, query whether a peer is connected over their network, retrieve the list of peers of any peer that they're connected to, remove a peer from their network, etc.
## (we have implemented the bonus question)

## Features
1) The program enables users to connect to other users using TCP (peer to peer).
2) It uses Multithreading to handle multiple connections.
3) The peers can send and receive messages in real time.
4) The node can request its peers for their peer list.
5) The node can retrieve its own peer list and check whether a particular peer is still connected.
6) The node can add or remove any peer over TCP using their IP address and the port number.
7) the node can exit the network anytime.

## Requirements 
Python (version 3.x or above), and the following libraries installed :  
1) Socket     
2) Sys  
3) Threading   
4) Time

Basic understanding of python and network/socket programming using python.

## Commands
Once the node is running, use the following commands:

| Command  | Description |

| `send <message>` | Send a message to all connected peers. |

| `add <peer_ip> <peer_port>` | Add a new peer connection. |

| `delete <peer_ip> <peer_port>` | Remove a peer from the network. |

| `list` | Display a list of all connected peers. |

| `query <peer_ip> <peer_port>` | Check if a specific peer is connected. |

| `select <peer_ip> <peer_port>` | Retrieve peer list from a specific peer. |

| `exit` | Disconnect and stop the node. |


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install socket (or other libraries).

```bash
pip install socket
```

## Example Usage
Start a node:
```sh
python hashverse.py 10.18.3.183 8000
```
Add a Peer:
```sh
add 10.18.3.183 8000
```
Send a message:
```sh
send Hello, peers!
```
List of Peers:
```sh
list
```
Query a Peer:
```sh
query 10.18.3.183 8000
```





## Team
Developed by **Team Hashverse**.

## Contributors
1) Kushagra Mishra - 230041017

2) Anjanayae Chaurasia - 230021002

3) Shrish Shriyans - 230003072
