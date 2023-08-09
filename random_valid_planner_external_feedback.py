import openai
from gen_start_config import *
from toh_few_shot_examples_only import standard_prompt
from copy import deepcopy
import time
import re
import json
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"
openai.api_key = "60be7ed5e0ca4e3c983ab7e70929f704"
all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
char_int_mapping = {'A':0,'B':1,'C':2}




def random_agent_propose_two_actions(temp_current_configuration,num_disks):

	
	all_moves = []
	valid_moves = []
	for j in range(num_disks):
		if j in temp_current_configuration[0]:
			max_B = max(temp_current_configuration[1]) if len(temp_current_configuration[1]) else -1
			max_C = max(temp_current_configuration[2]) if len(temp_current_configuration[2]) else -1
			all_moves.append("Move {} from A to B".format(j))
			if j==temp_current_configuration[0][-1] and j>max_B:
				valid_moves.append("yes")
			else:
				valid_moves.append("no")

			all_moves.append("Move {} from A to C".format(j))
			if j==temp_current_configuration[0][-1] and j>max_C:
				valid_moves.append("yes")
			else:
				valid_moves.append("no")


		elif j in temp_current_configuration[1]:
			max_A = max(temp_current_configuration[0]) if len(temp_current_configuration[0]) else -1
			max_C = max(temp_current_configuration[2]) if len(temp_current_configuration[2]) else -1

			all_moves.append("Move {} from B to A".format(j))
			if j==temp_current_configuration[1][-1] and j>max_A:
				valid_moves.append("yes")
			else:
				valid_moves.append("no")



			all_moves.append("Move {} from B to C".format(j))

			if j==temp_current_configuration[1][-1] and j>max_C:
				valid_moves.append("yes")
			else:
				valid_moves.append("no")


		else:
			max_A = max(temp_current_configuration[0]) if len(temp_current_configuration[0]) else -1
			max_B = max(temp_current_configuration[1]) if len(temp_current_configuration[1]) else -1


			all_moves.append("Move {} from C to A".format(j))
			if j==temp_current_configuration[2][-1] and j>max_A:
				valid_moves.append("yes")
			else:
				valid_moves.append("no")



			all_moves.append("Move {} from C to B".format(j))
			if j==temp_current_configuration[2][-1] and j>max_B:
				valid_moves.append("yes")
			else:
				valid_moves.append("no")



	total_valid_moves_possible = valid_moves.count("yes")
	two_different_valid_move_index = np.random.choice(total_valid_moves_possible,size=2,replace=False)
	# print(total_valid_moves_possible,valid_move_index)
	move_proposals = []

	count = 0
	for k in range(len(valid_moves)):
		if valid_moves[k] == 'yes':
			if count == two_different_valid_move_index[0]:
				valid_move_to_take = all_moves[k]
				move_proposals.append(valid_move_to_take)
				break
			else:
				count+=1

	count = 0
	for k in range(len(valid_moves)):
		if valid_moves[k] == 'yes':
			if count == two_different_valid_move_index[1]:
				valid_move_to_take = all_moves[k]
				move_proposals.append(valid_move_to_take)
				break
			else:
				count+=1

	return move_proposals
	




def state_predictor_module(state_A,state_B,state_C,move_msg):

	state_predictor_prompt = """Consider the following puzzle problem:

			Problem description:
			- There are three lists labeled A, B, and C.
			- There is a set of numbers distributed among those three lists.
			- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
			Rule #1: You can only move a number if it is at the rightmost end of its current list.
			Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
			

			Goal: The goal is to predict the configuration of the three lists, if the proposed move is applied to the current configuration.


			Here are two examples:
			
			Example 1:

			
			This is the current configuration:
			A = []
			B = [1]
			C = [0, 2]
			
			Proposed move:
			Move 2 from list C to list B.

			Answer:
			A = []
			B = [1, 2]
			C = [0]


			Example 2:

			
			This is the current configuration:
			A = []
			B = [1]
			C = [0, 2]
			
			Proposed move:
			Move 1 from list B to list A.

			Answer:
			A = [1]
			B = []
			C = [0, 2]
			


			Here is the task:

			
			This is the current configuration:
			{}
			{}
			{}
			Proposed move:
			{}.

			Answer:

			""".format("A = "+str(state_A),"B = "+str(state_B),"C = "+str(state_C),move_msg)


	state_predictor_input = [{
	    "role": "system",
	    "content": "you are an AI assistant",
	}]

	state_predictor_input.append({
	    "role": "user",
	    "content": state_predictor_prompt,
	})

	cur_try=0
	while cur_try<10:

		try:

			predictor_response = openai.ChatCompletion.create(
			    engine='gpt-4-32k',
			    messages=state_predictor_input,temperature=0.0,top_p=0,
			        max_tokens=200)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(60)
			cur_try+=1
			continue

	print("predictor_response>>",predictor_response)
	state_predictor_output = []
	splits = predictor_response.choices[0].message.content.split("=")
	for sp in splits:

		if '[' in sp and ']' in sp:

			state_predictor_output.append(json.loads(sp[sp.index('['):sp.index(']')+1]))

	
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[0].split("=")[-1]))
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[1].split("=")[-1]))
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[2].split("=")[-1]))
	return state_predictor_output




def state_evaluator_module(state_A,state_B,state_C,goal_config):

	state_evaluator_prompt = """Consider the following puzzle problem:

		Problem description:
		- There are three lists labeled A, B, and C.
		- There is a set of numbers distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2
		
		Goal: The goal is to predict the minimum number of valid moves required to reach the goal configuration from the current configuration.
		

		Here are ten examples:
		
		Example 1:
		
		This is the current configuration:
		A = [0, 1, 2]
		B = []
		C = []
		
		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]
		
		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 7.
		
		
		Example 2:
		
		This is the current configuration:
		A = [1, 2]
		B = [0]
		C = []

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 4.

		
		Example 3:
		
		This is the current configuration:
		A = [2]
		B = []
		C = [0, 1]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 1.

		
		Example 4:
		
		This is the current configuration:
		A = [1]
		B = []
		C = [0, 2]
		
		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 3.


		Example 5:
		
		This is the current configuration:
		A = []
		B = [1, 2]
		C = [0]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 3.


		Example 6:
		
		This is the current configuration:
		A = []
		B = [1]
		C = [0, 2]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 3.


		Example 7:
		
		This is the current configuration:
		A = [0, 2]
		B = [1]
		C = []

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 5.


		Example 8:
		
		This is the current configuration:
		A = []
		B = [0, 2]
		C = [1]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 6.


		Example 9:
		
		This is the current configuration:
		A = [0]
		B = [2]
		C = [1]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 7.


		Example 10:
		
		This is the current configuration:
		A = [2]
		B = [0]
		C = [1]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 7.
		
		Here is the task:
		
		This is the current configurations:
		{}
		{}
		{}
		
		This is the goal configuration:
		A = []
		B = []
		{}
		
		Answer:

		""".format("A = "+str(state_A),"B = "+str(state_B),"C = "+str(state_C),goal_config)

	state_evaluator_input = [{
		    "role": "system",
		    "content": "you are an AI assistant",
		}]

	state_evaluator_input.append({
	    "role": "user",
	    "content": state_evaluator_prompt,
	})

	cur_try=0
	while cur_try<10:

		try:

			evaluator_response = openai.ChatCompletion.create(
			    engine='gpt-4-32k',
			    messages=state_evaluator_input,temperature=0.0,top_p=0,
			        max_tokens=500)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(60)
			cur_try+=1
			continue

	for k in range(len(evaluator_response.choices[0].message.content) - 107):
		if evaluator_response.choices[0].message.content[k:k+108] == 'The minimum number of valid moves required to reach the goal configuration from the current configuration is':

			return int(evaluator_response.choices[0].message.content[k+109])



for i in range(82,106):
	A=all_As[i] 

	B=all_Bs[i]

	C=all_Cs[i]
	num_disks = max(A+B+C)+1
	
	start_configuration = [A,B,C]
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
	- There is a set of numbers distributed among those three lists.
	- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
	
	Goal: The goal is to end up in the configuration where all numbers are in list C, in ascending order.
	
	Rule #1: You can only move a number if it is at the rightmost end of its current list.
	Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.


	This is the starting configuration:
	{}
	{}
	{}
	This is the goal configuration:
	A = []
	B = []
	{}

	Give me only the next move from the starting configuration, that would help in reaching the goal configuration using as few moves as possible. 
	Your answer should be in the format as below:
	Move <N> from <src> to <trg>.

	""".format("A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])




	
	print("starting prompt>>",prompt)

	
	flag=0
	total_reward = 0
	step = 0
	num_tries=0
	max_content_limit_exceed_count = 0
	depth_flag=0
	
	while step < 50:

		
	
		
		first_temp_current_configuration = deepcopy(current_configuration)

		print("step>>",step)
		print("first config>>",first_temp_current_configuration)
		move_proposals = random_agent_propose_two_actions(first_temp_current_configuration,num_disks)
		print("move proposals>>",move_proposals)
		# print("input now>>>",input)
			
		
		
		next_temp_current_configuration1 = state_predictor_module(first_temp_current_configuration[0], first_temp_current_configuration[1], first_temp_current_configuration[2] ,move_proposals[0])
		next_temp_current_configuration2 = state_predictor_module(first_temp_current_configuration[0], first_temp_current_configuration[1], first_temp_current_configuration[2] ,move_proposals[1])

		print("next config 1>>",next_temp_current_configuration1)
		print("next config 2>>",next_temp_current_configuration2)

		if (next_temp_current_configuration1 == target_configuration) or (next_temp_current_configuration2 == target_configuration):

			moves_from_next_temp_current_configuration1 = state_evaluator_module(next_temp_current_configuration1[0],next_temp_current_configuration1[1],next_temp_current_configuration1[2],number_target_mapping[num_disks])
			moves_from_next_temp_current_configuration2 = state_evaluator_module(next_temp_current_configuration2[0],next_temp_current_configuration2[1],next_temp_current_configuration2[2],number_target_mapping[num_disks])

			if moves_from_next_temp_current_configuration1 < moves_from_next_temp_current_configuration2:
				next_move_chosen_for_system = move_proposals[0]
			elif moves_from_next_temp_current_configuration2 < moves_from_next_temp_current_configuration1:
				next_move_chosen_for_system = move_proposals[1]
			else:
				next_move_chosen_for_system = move_proposals[np.random.randint(0,2)]

			print("target reached at first rollout and move chosen>>>",next_move_chosen_for_system)

		else:
			depth_flag=1

			

			

			next_move_proposals1 = random_agent_propose_two_actions(next_temp_current_configuration1,num_disks)
			print("move proposals from config 1>>",next_move_proposals1)

			

			


			next_move_proposals2 = random_agent_propose_two_actions(next_temp_current_configuration2,num_disks)
			
			print("move proposals from config 2>>",next_move_proposals2)

			# print("input now>>>",input)

			next_next_temp_current_configuration1_1 = state_predictor_module(next_temp_current_configuration1[0], next_temp_current_configuration1[1], next_temp_current_configuration1[2] ,next_move_proposals1[0])
			
			next_next_temp_current_configuration1_2 = state_predictor_module(next_temp_current_configuration1[0], next_temp_current_configuration1[1], next_temp_current_configuration1[2] ,next_move_proposals1[1])

			print("next next config 1_1>>",next_next_temp_current_configuration1_1)
			print("next next config 1_2>>",next_next_temp_current_configuration1_2)


			next_next_temp_current_configuration2_1 = state_predictor_module(next_temp_current_configuration2[0], next_temp_current_configuration2[1], next_temp_current_configuration2[2] ,next_move_proposals2[0])
			
			next_next_temp_current_configuration2_2 = state_predictor_module(next_temp_current_configuration2[0], next_temp_current_configuration2[1], next_temp_current_configuration2[2] ,next_move_proposals2[1])

			print("next next config 2_1>>",next_next_temp_current_configuration2_1)
			print("next next config 2_2>>",next_next_temp_current_configuration2_2)


			moves_from_next_next_temp_current_configuration1_1 = state_evaluator_module(next_next_temp_current_configuration1_1[0],next_next_temp_current_configuration1_1[1],next_next_temp_current_configuration1_1[2],number_target_mapping[num_disks])
			moves_from_next_next_temp_current_configuration1_2 = state_evaluator_module(next_next_temp_current_configuration1_2[0],next_next_temp_current_configuration1_2[1],next_next_temp_current_configuration1_2[2],number_target_mapping[num_disks])
			
			moves_from_next_next_temp_current_configuration2_1 = state_evaluator_module(next_next_temp_current_configuration2_1[0],next_next_temp_current_configuration2_1[1],next_next_temp_current_configuration2_1[2],number_target_mapping[num_disks])
			moves_from_next_next_temp_current_configuration2_2 = state_evaluator_module(next_next_temp_current_configuration2_2[0],next_next_temp_current_configuration2_2[1],next_next_temp_current_configuration2_2[2],number_target_mapping[num_disks])
			
			four_configs_moves = []
			four_configs_moves.append(moves_from_next_next_temp_current_configuration1_1)
			four_configs_moves.append(moves_from_next_next_temp_current_configuration1_2)
			four_configs_moves.append(moves_from_next_next_temp_current_configuration2_1)
			four_configs_moves.append(moves_from_next_next_temp_current_configuration2_2)

			min_moves = min(moves_from_next_next_temp_current_configuration1_1, moves_from_next_next_temp_current_configuration1_2, moves_from_next_next_temp_current_configuration2_1,moves_from_next_next_temp_current_configuration2_2)

			index_min_moves = []
			for idx,config_moves in enumerate(four_configs_moves):
				if config_moves == min_moves:
					index_min_moves.append(idx)

			min_move_index_chosen = np.random.choice(index_min_moves)
			if min_move_index_chosen>1:
				next_move_chosen_for_system = move_proposals[1]
			else:
				next_move_chosen_for_system = move_proposals[0]


			print("num moves from 4 configs, move chosen>>>",moves_from_next_next_temp_current_configuration1_1,moves_from_next_next_temp_current_configuration1_2,moves_from_next_next_temp_current_configuration2_1,moves_from_next_next_temp_current_configuration2_2,next_move_chosen_for_system)




			

		

		# print("error monitor gpt full response>>",validator_response.choices[0].message.content)
		# print("move_validity>>",move_validity)
		
		step+=1
		
		no_to_move = int(next_move_chosen_for_system.split(" ")[1])
		source_list = next_move_chosen_for_system.split(" ")[3]
		target_list = next_move_chosen_for_system.split(" ")[5]
		# print(gpt_response,no_to_move,source_list,target_list)
		total_reward+=-1
		response_flag =0
		if no_to_move not in current_configuration[char_int_mapping[source_list]]:
			user_message = next_move_chosen_for_system + "\nInvalid move because {} is not in {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
			reward_message = "Invalid move because {} is not in {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
			response_flag =1
		else:
			if current_configuration[char_int_mapping[source_list]][-1]!= no_to_move:
				user_message = next_move_chosen_for_system + "\nInvalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
				reward_message = "Invalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
				response_flag =1
			else:
				if len(current_configuration[char_int_mapping[target_list]]):
					max_target_list = max(current_configuration[char_int_mapping[target_list]])
				else:
					max_target_list = -1

				if no_to_move < max_target_list:
					user_message = next_move_chosen_for_system + "\nInvalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
					reward_message = "Invalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
					response_flag=1
				else:
					user_message = next_move_chosen_for_system+'.'+'\nFor each move you get a penalty of -1.'
					reward_message = "For each move you get a penalty of -1."
					current_configuration[char_int_mapping[source_list]].pop()
					current_configuration[char_int_mapping[target_list]].append(no_to_move)

		if response_flag==1:
			total_reward+=-10

		configuration_msg = """This is the current configuration:
		{}
		{}
		{}

		This is the goal configuration:
		A = []
		B = []
		{}

		Give me only the next move from the current configuration, that would help in reaching the goal configuration using as few moves as possible. 
		Your answer should be in the format as below:
		Move <N> from <src> to <trg>.

		""".format("A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]),number_target_mapping[num_disks])

		


		prompt+="\n"+user_message+"\n"+configuration_msg

		print("external feedback>>",reward_message+"\n"+configuration_msg)

		
		
		if current_configuration == target_configuration:
			flag=1
			total_reward+=100
			with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/random valid moves, planner step by step external feedback/problem{}.log'.format(i+1), 'a') as w:
				w.write(prompt +'\n'+"Solved problem in {} steps. Total reward = {}".format(step+1,total_reward))

			break

		
	

			# print("error monitor feedback>>>",validator_response.choices[0].message.content + "\n"+configuration_msg)

	if flag==0:
		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/random valid moves, planner step by step external feedback/problem{}.log'.format(i+1), 'a') as w:
			w.write(prompt +'\n'+"Timed out. Couldn't solve problem in 50 steps. Total reward = {}".format(total_reward))


	


	
	print("done solving problem {}".format(i+1))
