''' 
TO DO:
 - Add position index to traces, e.g. using instruction count.
'''
import sys
import os
import csv
import numpy as np

# rw,baseaddr,size,gtid,tgid,wid,ltid,pc
# Initialize arguments
trace_file = ""
line_size = 1
max_group_size = 4
min_addr = 1000000000
max_addr = 0
read_addrs = []
write_addrs = []

if (len(sys.argv) > 1):
    trace_file = sys.argv[1]

if (len(sys.argv) > 2):
    line_size = int(sys.argv[2])

# Read in trace file
mem_list = {}
with open(trace_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:

        rw = row[0]
        baseaddr = int(np.right_shift(int(row[1],16), int(np.log2(line_size))))
        size = int(row[2])
        gtid = int(row[3])
        tgid = int(row[4])
        wid = int(row[5])
        ltid = int(row[6])
        pc = int(row[7],16)
        if rw == 'r':
            read_addrs.append(baseaddr)
        else:
            write_addrs.append(baseaddr)
            
        if gtid in mem_list.keys():
            mem_list[gtid].append(baseaddr)
        else:
            mem_list[gtid] = [baseaddr]

# Calculate distances between traces
distance_lists = {}
for k in mem_list:
    distance_list = {}
    for j in mem_list:
        if k != j:
            dist = np.abs(np.array(j) - np.array(k))
            if dist in distance_list.keys():
                distance_list[dist].append(j)
            else:
                distance_list[dist] = [j]
    if k in distance_lists:
        distance_lists[k].append(distance_list)
    else:
        distance_lists[k] = [distance_list]

# Print stats
num_threads = len(distance_lists)
min_read_addr = min(read_addrs)
max_read_addr = max(read_addrs)
min_write_addr = min(write_addrs)
max_write_addr = max(write_addrs)
read_addr_space_size = max_read_addr - min_read_addr
write_addr_space_size = max_write_addr - min_write_addr
print("Num threads: " + str(num_threads))
print("Min read addr: " + str(hex(min_read_addr)))
print("Max read addr: " + str(hex(max_read_addr)))
print("Read address space size: " + str(hex(read_addr_space_size)))
print("Min write addr: " + str(hex(min_write_addr)))
print("Max write addr: " + str(hex(max_write_addr)))
print("Write address space size: " + str(hex(write_addr_space_size)))

# Print distances
for k in distance_lists:
    i = 0
    for distance in distance_lists[k]:
        if i < max_group_size - 1:
            for dist in sorted(distance.keys()):
                for j in distance[dist]:
                    i += 1
                    if i <= max_group_size - 1:
                        print(str(k) + ' ' + str(j) + ' ' + str(dist))
        else:
            break

# Calculate direction of memory accesses as a function of thread id
# E.g. Thread 0 accesses addr 0x0, thread 1 accesses addr 0x4, then this is increasing
# E.g. Thread 0 accesses addr 0x10, therad 1 accesses addr 0xc, then this is decreasing

mem_list_keys = list(mem_list.keys())
dir_vec = []
print("Direction")
for i in range(0,len(mem_list_keys)-1):
    j = mem_list[mem_list_keys[i]]
    k = mem_list[mem_list_keys[i+1]]
    dir = np.sum(np.abs(np.array(j) - np.array(k)))
    dir_vec.append(dir)

print(dir_vec)
