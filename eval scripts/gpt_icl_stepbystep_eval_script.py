
import json
import os
import argparse
import numpy as np

from copy import deepcopy

parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--num_disks', type = int, help='number of disks', required= True)
parser.add_argument('--max_moves', type = int, help='maximum muber of moves allowed for evaluation', required= True)

parser.add_argument('--output_dir',type=str, help='directory name where output log files are stored', required= True)

args = parser.parse_args()
print(args)


all_rewards = []
all_frac_invalid_moves = []
all_solved = []
for file in os.listdir(args.output_dir):
 
	file_baseline = open(os.path.join(args.output_dir,file), 'r')
	lines_baseline = file_baseline.read().splitlines()
	file_baseline.close()

	initial_A_B_C = []
	char_int_mapping = {'A':0,'B':1,'C':2}
	if args.num_disks==3:

		target_configuration = [[],[],[0,1,2]]
	elif args.num_disks==4:
		target_configuration = [[],[],[0,1,2,3]]


	task_index=0
	for i in range(len(lines_baseline)):
		if "Here is the task:" in lines_baseline[i]:
			task_index=i

			break

	env_feedback_index=0
	for i in range(len(lines_baseline)):
		if "External environment feedback" in lines_baseline[i]:
			env_feedback_index=i

			break

	for i in range(task_index,env_feedback_index):

		if 'This is the starting configuration' in lines_baseline[i]:# or 'Initial configuration' in lines_baseline[i]:
			initial_A_B_C.append(json.loads(lines_baseline[i+1].split("=")[-1]))
			initial_A_B_C.append(json.loads(lines_baseline[i+2].split("=")[-1]))
			initial_A_B_C.append(json.loads(lines_baseline[i+3].split("=")[-1]))
			break

	moves_decoded_tuples = []
	all_configuration_after_moves = []
	all_configuration_after_moves.append(deepcopy(initial_A_B_C))
	for i in range(task_index,env_feedback_index):


		if 'Move' in lines_baseline[i] and 'from' in lines_baseline[i] and 'to' in lines_baseline[i] and (('A' in lines_baseline[i] and 'B' in lines_baseline[i] ) or ('C' in lines_baseline[i] and 'B' in lines_baseline[i] ) or ('A' in lines_baseline[i] and 'C' in lines_baseline[i] )):




			move_line = lines_baseline[i].replace('.','').strip() # for random valid only


			moves_decoded_tuples.append((int(move_line.split(" ")[1]),move_line.split(" ")[3],move_line.split(" ")[5]))
			count = i

			while ("A =" not in lines_baseline[count]):
				count+=1

			state_output = []

			state_output.append(json.loads(lines_baseline[count].split("=")[-1]))
			state_output.append(json.loads(lines_baseline[count+1].split("=")[-1]))
			state_output.append(json.loads(lines_baseline[count+2].split("=")[-1]))

			all_configuration_after_moves.append(state_output)

	total_reward =0
	num_invalid_moves = 0
	solved_without_invalid = 0 
	num_moves = min(args.max_moves,len(moves_decoded_tuples))
	for k in range(num_moves):

		current_configuration = all_configuration_after_moves[k]

		no_to_move = moves_decoded_tuples[k][0]
		source_list = moves_decoded_tuples[k][1]
		target_list = moves_decoded_tuples[k][2]
#         print(no_to_move,source_list,target_list)
		total_reward+=-1

		if no_to_move not in current_configuration[char_int_mapping[source_list]]:

#             print("Invalid move because {} is not in {}".format(no_to_move,source_list))

			total_reward+=-10
			num_invalid_moves+=1
		else:
			if current_configuration[char_int_mapping[source_list]][-1]!= no_to_move:

#                 print("Invalid move because it violates Rule #1.")
				total_reward+=-10
				num_invalid_moves+=1
			else:
				if len(current_configuration[char_int_mapping[target_list]]):
					max_target_list = max(current_configuration[char_int_mapping[target_list]])
				else:
					max_target_list = -1

				if no_to_move < max_target_list:

#                     print("Invalid move because it violates Rule #2")

					total_reward+=-10
					num_invalid_moves+=1

	if all_configuration_after_moves[num_moves] == target_configuration and num_invalid_moves==0:


		solved_without_invalid=1

		total_reward+=100

# print(total_reward,num_invalid_moves/num_moves,solved_without_invalid)
	all_rewards.append(total_reward)
	all_frac_invalid_moves.append(num_invalid_moves/num_moves)
	all_solved.append(solved_without_invalid)

print("fraction solved without invalid>>>",np.mean(np.array(all_solved)))
print("fraction invalid>>",np.mean(np.array(all_frac_invalid_moves)))
print("Average reward>>>",np.mean(np.array(all_rewards)))
# moves_decoded_tuples,all_configuration_after_moves