# Byte researcher

This is a frequency analysis tool for TCP/UDP payloads from .pcap(ng) dumps.
It supports two types of analysis: positional and package-positional.

Executing script results can help when writing RegExp expressions to filter traffic.

>Tip: results of the analysis directly depend on the quality of the dump, so it is advisable to consider traffic in only one direction.

**Tshark** is used to parse dumps and **SQLite** is used to store information.


The tool has a command-line interface. Use `-h` to get a list of arguments.
```bash
usage: researcher.py [-h] {analyze,pcap} ...

positional arguments:
  {analyze,pcap}
    analyze       Options for analyze .pcap(ng) files. More info -h.
    pcap          Options for parse .pcap(ng) files. More info -h.  

options:
  -h, --help      show this help message and exit 
```

Dump processing is performed in two steps: parsing and applying analysis methods.

You can control the amount of information displayed through the parameters:

- `range` - the number of positions in the payload;
- `length` - number of displayed variants per position;
- `count` - number of packets (relevant for the batch-positional method).

Sample output for a packet-positional method:

| pkt | pos | open% | items |
| ----- | ----- | ----- | ----- |
| 1 | 1 | 7.8 | ('26', 106, 1.1%) ('78', 99, 1.0%) ('22', 95, 0.9%) ... |
| 1 | 2 | 100 | ('00', 13890, 95.7%) ('01', 272, 1.8%) ('08', 180, 1.2%) ('3f', 158, 1.0%) |

The `open%` column shows the percentage of `items` displayed on the screen. `Item` contains a byte, its frequency, and its percentage of the total.

# Analysis Methods

## Positional method

This method analyzes all dump packets at once. It is based on frequency analysis of paylod bytes that have the same position index.

![pos method pic](https://github.com/Serj57/Researcher/blob/main/blob/pos_method.png)

Result:

| position | items |
| ----- | ----- |
| 1 | ('aa', 4)|
| 2 | ('ff', 4)|
| 3 | ('01', 2) ('ed', 2) |
| 4 | ('a0', 1) ('4b', 1) ('c7', 1) ('09', 1) |


## Packet-positional method

In the packet-positional method, packets are first split into streams based on [5-Tuple](https://www.ietf.org/rfc/rfc6146.txt).

The example below shows that packets #1 and #3 are from stream #1 (yellow), and #2 and #4 are from stream #2 (green). Then the first packets are taken from each stream. In the example, these are #1 and #2. For them, the positional method is used. Next, the second packets of streams are taken (No. 3 and No. 4) and the positional method is applied again, etc.

![pkt-pos method pic](https://github.com/Serj57/Researcher/blob/main/blob/pkt_pos_method.png)

Result:

| packet | position | items |
| ----- | ----- | ----- |
| 1 | 1 | ('aa', 2) |
| 1 | 2 | ('ff', 2) |
| 1 | 3 | ('01', 1) ('ed', 1)|
| 1 | 4 | ('a0', 1) ('4b', 1)|
| 2 | 1 | ('aa', 2) |
| 2 | 2 | ('ff', 2) |
| 2 | 3 | ('01', 1) ('ed', 1)|
| 2 | 4 | ('c7', 1) ('09', 1)|

# Deploy

First of all, you need to install Tshark. Detailed instructions are available on the [website](https://tshark.dev/setup/install/).

Next, we need a bundle of command-line tools for managing SQLite database files. For Windows, you can download the bundle from the official [website](https://www.sqlite.org/2022/sqlite-tools-win32-x86-3390400.zip). For Linux bundle is available in the repository.

If you're on Windows, don't forget to set the path to the .exe in your environment variables.

Finally need to install Python packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```
