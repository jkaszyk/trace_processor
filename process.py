''' 
TO DO:
 - Add position index to traces, e.g. using instruction count.
 - Find nearest after allocating threads to warps, i.e. remove from working set (naive approach)
 - Try clustering addresses (knn/k-means clustering)
 - Zero-extend vector & calculate distance
 - Implement metric for irregular workloads - distance doesn't really work, because one more/fewer access will dominate metric
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

# Standardize length
max_length_mem = 0
max_length_read = 0
max_length_write = 0

for gtid in mem_list:
    l = len(mem_list[gtid])
    if l > max_length_mem:
        max_length_mem = l
        
for gtid in mem_list:
    l = len(mem_list[gtid])
    if l < max_length_mem:
        mem_list[gtid].extend(np.zeros(max_length_mem - l))
        
# Calculate total distances between thread memory traces
distance_lists = {}
for gtid_1 in mem_list:
    distance_list = {}
    for gtid_2 in mem_list:
        if gtid_1 != gtid_2:
            dist = np.sum(np.abs(np.array(mem_list[gtid_2]) - np.array(mem_list[gtid_1])))
            if dist in distance_list.keys():
                distance_list[dist].append(gtid_2)
            else:
                distance_list[dist] = [gtid_2]
    if gtid_1 in distance_lists:
        distance_lists[gtid_1].append(distance_list)
    else:
        distance_lists[gtid_1] = [distance_list]

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
for gtid_1 in distance_lists:
    i = 0
    for distance in distance_lists[gtid_1]:
        if i < max_group_size - 1:
            for dist in sorted(distance.keys()):
                for gtid_2 in distance[dist]:
                    i += 1
                    if i <= max_group_size - 1:
                        print(str(gtid_1) + ' ' + str(gtid_2) + ' ' + str(dist))
        else:
            break

# Calculate direction of memory accesses as a function of thread id
# Number shows direction between current and next thread
# E.g. Thread 0 accesses addr 0x0, thread 1 accesses addr 0x4, then this is increasing
# E.g. Thread 0 accesses addr 0x10, thread 1 accesses addr 0xc, then this is decreasing

mem_list_keys = list(mem_list.keys())
sum_dir_vec = []
avg_dir_vec = []
print("Sum Direction")
for i in range(0,len(mem_list_keys)-1):
    j = mem_list[mem_list_keys[i]]
    k = mem_list[mem_list_keys[i+1]]
    dir = np.sum(np.abs(np.array(j) - np.array(k)))
    sum_dir_vec.append(dir)
    avg_dir_vec.append(dir*1.0/len(np.array(j)))
print(sum_dir_vec)
print("Average Direction")
print(avg_dir_vec)
