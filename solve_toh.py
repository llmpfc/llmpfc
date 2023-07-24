
from gen_start_config import *
from copy import deepcopy
all_As, all_Bs, all_Cs = generate_all_start_config()
# all_As_copy = deepcopy(all_As)
# all_Bs_copy = deepcopy(all_Bs)
# all_Cs_copy = deepcopy(all_Cs)
for i in range(len(all_As)):
    # print(i,all_As[i],all_Bs[i],all_Cs[i])

    A=deepcopy(all_As[i]) 

    B=deepcopy(all_Bs[i])

    C=deepcopy(all_Cs[i])

    # print(i,all_As[i],all_Bs[i],all_Cs[i],all_As_copy[i],all_Bs_copy[i],all_Cs_copy[i])

    
    count =0 
    int_arr_mapping = {0:A,1:B,2:C}
    int_char_mapping = {0:'A',1:'B',2:'C'}
    with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/optimal policy/problem{}.log'.format(i+1), 'a') as w:
        w.write(f'Initial configuration:\nA = {A}\nB = {B}\nC = {C}\n')


# print("Starting state configuration: A = {}, B = {}, C = {}".format(A,B,C))

    def moveDisks(diskPositions, largestToMove, targetPeg):
       
        for badDisk in range(largestToMove, len(diskPositions)):

            currentPeg = diskPositions[badDisk]         
            if currentPeg != targetPeg:
                #found the largest disk on the wrong peg

                #sum of the peg numbers is 3, so to find the other one...
                otherPeg = 3 - targetPeg - currentPeg

                #before we can move badDisk, we have get the smaller ones out of the way
                moveDisks(diskPositions, badDisk+1, otherPeg)
                global count
                count+=1
               
                

                # print("Move ", badDisk, " from ", int_char_mapping[currentPeg], " to ", int_char_mapping[targetPeg])
                with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/optimal policy/problem{}.log'.format(i+1), 'a') as w:
                    w.write(f'Step {count}: Move {badDisk} from {int_char_mapping[currentPeg]} to {int_char_mapping[targetPeg]}\n')


                
                assert badDisk == int_arr_mapping[currentPeg].pop()
                int_arr_mapping[targetPeg].append(badDisk)

                with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/optimal policy/problem{}.log'.format(i+1), 'a') as w:
                    w.write(f'Current configuration:\nA = {A}\nB = {B}\nC = {C}\n')

                # print("Current state configuration: A = {}, B = {}, C = {}".format(A,B,C))

                diskPositions[badDisk]=targetPeg

                #now we can put the smaller ones in the right place
                moveDisks(diskPositions, badDisk+1, targetPeg)

                break;
            






   
    num_disks = max(A+B+C)+1

    position_list = []
    for j in range(num_disks):
        if j in A:
            position_list.append(0)
        elif j in B:
            position_list.append(1)
        else:
            position_list.append(2)

    moveDisks(position_list,0,2)
