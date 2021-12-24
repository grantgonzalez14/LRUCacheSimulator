import sys
from collections import OrderedDict
import math

# Class containing functionality of LRU
class LRUCacheFunctionality:

    def __init__(self, num_lines):
        self.cache = OrderedDict()

        # Number of lines in the cache
        self.num_lines = num_lines

    def get(self, key):
        if key not in self.cache:
            return -1
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def insert(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)

        if len(self.cache) > self.num_lines:
            self.cache.popitem(False)

class CacheSimulator:

    def __init__(self, input_file):
        self.input_file = open(input_file, "r")

        # Number of sets, number of lines per set, size of each line in bytes
        self.sets, self.num_cache_lines, self.line_size = self.get_sizes()

        # Total number of lines
        self.num_blocks = self.sets * self.num_cache_lines

        # Tracking variables
        self.total_hits = 0
        self.total_misses = 0
        self.total_accesses = 0
        self.hit_ratio = 0
        self.miss_ratio = 0
        self.output_info = {}
        self.cache = {}
        for set in range(self.sets):
            self.cache[set] = LRUCacheFunctionality(self.num_cache_lines)

    def get_sizes(self):
        file = self.input_file
        num_sets = file.readline()
        num_sets = num_sets[5:]
        set_size = file.readline()
        set_size = set_size[9:]
        line_size = file.readline()
        line_size = line_size[10:]
        return int(num_sets), int(set_size), int(line_size)

    def read_data(self):
        file = self.input_file
        line = file.readline()

        if not line:
            # return None to indicate that there is no more data to be read
            return None, None

        operation = line[:1]
        address = line[2:]

        if address[-1:] == "\n":
            address = address[:-1]

        address = int(address, 16)

        if operation == "R":
            operation = "read"
        elif operation == "W":
            operation = "write"

        return operation, address

    def get_bits(self, address):
        offset_bits = int(math.log(self.line_size, 2))
        index_bits = int(math.log(self.sets, 2))
        offset_mask = 0
        index_mask = 0

        for i in range(offset_bits):
            offset_mask += 2 ** i

        for i in range(index_bits):
            index_mask += 2 ** i

        tag = address >> (index_bits + offset_bits)
        offset = address & offset_mask
        index = (address >> offset_bits) & index_mask

        return tag, index, offset

    def is_power_of_two(self, num):
        return (math.ceil(math.log(num, 2)) == math.floor(math.log(num, 2)))

    def validate(self):
        if not self.is_power_of_two(self.sets):
            print("The number of sets is not a power of two.")
            exit(1)
        if self.sets > 2 ** 13:
            print("The number of sets is too large.")
            exit(1)
        if not self.is_power_of_two(self.line_size):
            print("The line size is not a power of two.")
            exit(1)
        if self.line_size < 4:
            print("The line size is too small.")
            exit(1)

    def print_stats(self):
        colon = ":"
        print(f"sets: {self.sets}")
        print("Cache Configuration\n")
        print(f"\t\t{self.sets} {self.num_cache_lines}-way set associative entries")
        print(f"\t\tof line size {self.line_size} bytes\n")
        print("Access Address\t Tag   Index Offset Status Memrefs")
        print("-"*len("Access"), "-"*len("Address"), "-"*(len("Tag") + 4), "-"*len("Index"), "-"*len("Offset"), "-"*len("Status"), "-"*len("Memrefs"))
        for statistic in range(len(self.output_info)):
            print(f"{self.output_info[statistic][0]:>6}{self.output_info[statistic][1]:>8}{self.output_info[statistic][2]:>8}{self.output_info[statistic][3]:>6}{self.output_info[statistic][4]:>7}{self.output_info[statistic][5]:>7}{self.output_info[statistic][6]:>8}")
        print("\nSimulation Summary Statistics")
        print("-"*len("Simulation Summary Statistics"))
        print(f"Total hits{colon:>8} {self.total_hits}")
        print(f"Total misses{colon:>6} {self.total_misses}")
        print(f"Total accesses{colon:>4} {self.total_accesses}")
        print(f"Hit ratio{colon:>9} {self.hit_ratio:<08}")
        print(f"Miss ratio{colon:>8} {self.miss_ratio:<08}")

    def run(self):
        self.validate()
        iteration = 0

        while True:
            operation, address = self.read_data()

            if not operation:
                self.input_file.close()
                self.hit_ratio = self.total_hits / self.total_accesses
                self.miss_ratio = self.total_misses / self.total_accesses
                self.print_stats()
                return

            tag, index, offset = self.get_bits(address)
            set_num = address % self.sets

            #LRU functionality
            if self.cache[set_num].get(set_num) == -1:
                status = "miss"
                memref = 1
                self.total_misses += 1
            else:
                status = "hit"
                memref = 0
                self.total_hits += 1

            print(f"set_num: {set_num} self.cache[set_num].get(set_num): {self.cache[set_num].get(set_num)}")

            self.cache[set_num].insert(set_num, set_num)

            address = hex(address)
            self.output_info[iteration] = []
            self.output_info[iteration].append(operation)
            self.output_info[iteration].append(address)
            self.output_info[iteration].append(tag)
            self.output_info[iteration].append(index)
            self.output_info[iteration].append(offset)
            self.output_info[iteration].append(status)
            self.output_info[iteration].append(memref)
            iteration += 1
            self.total_accesses += 1

if len(sys.argv) != 2:
    print("Incorrect command line arguments")
    exit(1)

cache_simulator = CacheSimulator(sys.argv[1])
cache_simulator.run()