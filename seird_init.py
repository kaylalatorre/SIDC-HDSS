import numpy as np


# Python program to get average of a list
def get_ave(lst):
    return sum(lst) / len(lst)


"""
for int-type values
"""
# nStart = int(input("Enter start n: "))
# nStop = int(input("Enter stop n: "))
# nInterv = int(input("Enter interv n: "))
# num_range = range(nStart,(nStop+1),nInterv)                        # start, stop+1, interval n

# num_list = list(num_range)      # convert range into a list

# num_ave = round(get_ave(num_list), 2)     # get average of the list


"""
for float-type values
"""
nStart = float(input("Enter start n: "))
nStop = float(input("Enter stop n: "))
nInterv = float(input("Enter interv n: "))

num_list = np.arange(nStart,(nStop+1.0),nInterv) # range() for float-type

num_ave = round(get_ave(num_list), 2)           # get average of the list

print("AVERAGE: " + str(num_ave))
