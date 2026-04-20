"""
Network Traffic Analysis
Question: Analyze a network traffic log to find the "Top N" IP addresses with the most requests. 
Challenge platform
Challenge platform
python
from collections import Counter
traffic = ['192.168.1.1', '10.0.0.1', '192.168.1.1', '172.16.0.1']
# Return top 1
Concepts: collections.Counter, dictionaries.
"""

from typing import List
from collections import Counter
import heapq

def find_highest_top_n_IPs():
    print("hello")
    traffic = ['192.168.1.1', '10.0.0.1', '192.168.1.1', '172.16.0.1', '192.168.1.1', '192.168.1.1', '10.0.0.1']
    counter = Counter(traffic)
    highestTwo = counter.most_common(2)
    print(highestTwo)


if __name__ == "__main__":
    print("1")
    find_highest_top_n_IPs()
