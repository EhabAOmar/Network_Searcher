# Network Keyword Searcher


## Discription
A tool developed using FastAPI framework to search a network of routers/switches for keyword(s) in the configurations of the network devices and return the results with the matching lines in a web page.

The input file can be an Excel (.xlsx) or CSV (.csv) file, with the IP address and node vendor (Juniper, Cisco, Huawei, ... etc). There is a template as a aguide in the tool.

This tool is useful when we have a big network with a lot of routers/switches and need to find the configuration for a particular service or custom configurations on which nodes.


## Features
- Search with one keyword or two keywords with options (AND) or (OR)
- Search with a case-sensitive keywords
- Returning the list of configuration lines matching the keywords




## Installation
git clone https://github.com/EhabAOmar/Network_Searcher.git
cd repository
