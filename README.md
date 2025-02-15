# Network Keyword Searcher


## Discription
A tool developed using FastAPI framework to search a network of routers/switches for keyword(s) in the configurations of the network devices and return the results with the matching lines in a web page.

The input file must be a .CSV file, with the IP address and router vendor (Juniper, Cisco, Huawei, ... etc)

This tool is useful when we have a big network with a lot of routers/switches and need to find the configuration for a particular service or customer on which routers.


## Features
- Search with one keyword or two keywords with options (AND) or (OR)
- Search with a case-sensitive kewywords
- Returning the list of configuration lines matching the keywords




## Installation
git clone https://github.com/EhabAOmar/Network_Searcher.git
cd repository
