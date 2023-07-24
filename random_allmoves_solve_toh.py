import openai
from gen_start_config import *
from copy import deepcopy
import numpy as np

all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
char_int_mapping = {'A':0,'B':1,'C':2}
for run_no in range(1,6):
	for i in range(len(all_As)):
		A=all_As[i] 

		B=all_Bs[i]

		C=all_Cs[i]

		start_configuration = [A,B,C]
		num_disks = max(A+B+C)+1


		if num_disks ==3:

			target_configuration = [[],[],[0,1,2]]
		elif num_disks ==4:

			target_configuration = [[],[],[0,1,2,3]]
		else:


			target_configuration = [[],[],[0,1,2,3,4]]

		current_configuration = deepcopy(start_configuration)

		prompt = """Consider the following puzzle problem:
		Problem description:
		- There are three lists labeled A, B, and C.
		- There are {} distributed among those three lists.
		- You can move numbers from one list to another.
		Goal: The goal is to end up in the configuration where all numbers are in list C, in ascending order.
		Rule #1: You can only move a number if it is at the end of its current list.
		Rule #2: You can only move a number to a list if it is larger than the other numbers in that list.

		This is the starting configuration:
		{}
		{}
		{}
		This is the goal configuration:
		A = []
		B = []
		{}

		Give me the sequence of moves from the starting configuration, that would help in reaching the goal configuration using as few moves as possible. 
		Your answer should be in the format as below:
		Move <N> from list <src> to list <trg>.

		""".format(number_message_mapping[num_disks],"A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])

		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/random step by step all possible moves/run{}/problem{}.log'.format(run_no,i+1), 'a') as w:
			w.write(prompt +'\n'+"Random agent response>>>>\n")

		flag=0
		total_reward = 0

		for step in range(50):
			all_moves = []
			valid_moves = []
			for j in range(num_disks):
				if j in current_configuration[0]:
					max_B = max(current_configuration[1]) if len(current_configuration[1]) else -1
					max_C = max(current_configuration[2]) if len(current_configuration[2]) else -1
					all_moves.append("Move {} from A to B".format(j))
					if j==current_configuration[0][-1] and j>max_B:
						valid_moves.append("yes")
					else:
						valid_moves.append("no")

					all_moves.append("Move {} from A to C".format(j))
					if j==current_configuration[0][-1] and j>max_C:
						valid_moves.append("yes")
					else:
						valid_moves.append("no")


				elif j in current_configuration[1]:
					max_A = max(current_configuration[0]) if len(current_configuration[0]) else -1
					max_C = max(current_configuration[2]) if len(current_configuration[2]) else -1

					all_moves.append("Move {} from B to A".format(j))
					if j==current_configuration[1][-1] and j>max_A:
						valid_moves.append("yes")
					else:
						valid_moves.append("no")



					all_moves.append("Move {} from B to C".format(j))

					if j==current_configuration[1][-1] and j>max_C:
						valid_moves.append("yes")
					else:
						valid_moves.append("no")


				else:
					max_A = max(current_configuration[0]) if len(current_configuration[0]) else -1
					max_B = max(current_configuration[1]) if len(current_configuration[1]) else -1


					all_moves.append("Move {} from C to A".format(j))
					if j==current_configuration[2][-1] and j>max_A:
						valid_moves.append("yes")
					else:
						valid_moves.append("no")



					all_moves.append("Move {} from C to B".format(j))
					if j==current_configuration[2][-1] and j>max_B:
						valid_moves.append("yes")
					else:
						valid_moves.append("no")



			# total_valid_moves_possible = valid_moves.count("yes")
			move_index = np.random.randint(low=0 , high = len(all_moves))
			# print(total_valid_moves_possible,valid_move_index)
			move_to_take = all_moves[move_index]
			move_validity = valid_moves[move_index]
			



			

			no_to_move = int(move_to_take.split(" ")[1])
			source_list = move_to_take.split(" ")[3]
			target_list = move_to_take.split(" ")[5]
			total_reward+=-1

			if move_validity == "no":
				total_reward+=-10

			with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/random step by step all possible moves/run{}/problem{}.log'.format(run_no,i+1), 'a') as w:
				w.write('{}. Move {} from list {} to list {}. Valid = {}\n'.format(step+1,no_to_move,source_list,target_list,move_validity))


			if move_validity == "yes":
				current_configuration[char_int_mapping[source_list]].pop()
				current_configuration[char_int_mapping[target_list]].append(no_to_move)

			configuration_msg = """
				{}
				{}
				{}
				""".format("A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]))


			with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/random step by step all possible moves/run{}/problem{}.log'.format(run_no,i+1), 'a') as w:
				w.write(configuration_msg+'\n')



			if current_configuration == target_configuration:
				flag=1
				total_reward+=100
				with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/random step by step all possible moves/run{}/problem{}.log'.format(run_no,i+1), 'a') as w:
					w.write('\n'+"Solved problem in {} steps. Total reward = {}".format(step+1, total_reward))
					break

		if flag==0:
			with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/random step by step all possible moves/run{}/problem{}.log'.format(run_no,i+1), 'a') as w:
				w.write('\n'+"Timed out. Couldn't solve problem in 50 steps. Total reward = {}".format(total_reward))



		print("For run no {}, done solving problem {}".format(run_no,i+1))


	