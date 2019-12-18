import sys
import os
import csv
import numpy as np

# rw,baseaddr,size,gtid,tgid,wid,ltid,pc

trace_file = ""
line_size = 0
max_group_size = 4

if (len(sys.argv) > 1):
    trace_file = sys.argv[1]

if (len(sys.argv) > 2):
    line_size = int(sys.argv[2])

mem_list = {}
with open(trace_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:

        rw = row[0]
        baseaddr = int(row[1],16)
        size = int(row[2])
        gtid = int(row[3])
        tgid = int(row[4])
        wid = int(row[5])
        ltid = int(row[6])
        pc = int(row[7],16)
        if gtid in mem_list.keys():
            mem_list[gtid].append(baseaddr)
        else:
            mem_list[gtid] = [baseaddr]

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
        
    
