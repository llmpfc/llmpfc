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

def subgoal_generator(given_state):

	subgoal_configs = []
	if 0 not in given_state[2]:
		if 0 in given_state[0]:

			subgoal_configs.append([[],[1,2,3],[0]])
		else:
			subgoal_configs.append([[1,2,3],[],[0]])
	else:
		if 1 not in given_state[2]:
			if 1 in given_state[0]:
				subgoal_configs.append([[],[2,3],[0,1]])
			else:
				subgoal_configs.append([[2,3], [], [0,1]])
		else:
			if 2 not in given_state[2]:
				if 2 in given_state[0]:
					subgoal_configs.append([[],[3],[0,1,2]])
				else:
					subgoal_configs.append([[3], [], [0,1,2]])

	return subgoal_configs






def move_validator_module(state_A, state_B, state_C, gpt_truncated_move_proposal):

	move_validator_prompt = """Consider the following puzzle problem:

		Problem description:
		- There are three lists labeled A, B, and C.
		- There is a set of numbers distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2.

		Goal: The goal is to check if the proposed move satisfies or violates Rule #1 and Rule #2 and based on that if it is a valid or invalid move.

		Here are eight examples:
		
		Example 1:

		This is the initial configuration:
		A = []
		B = [1]
		C = [0, 2]

		Proposed move:
		Move 0 from list C to list B.

		Answer:
		First check whether the move satisfies or violates Rule #1. 0 is not at the rightmost end of list C, because 2 is at the rightmost end of list C. Hence the move violates Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list B, to which 0 is moved. Maximum of list B is 1. 0 is not larger than 1. Hence the move violates Rule #2.
		Since the Move 0 from list C to list B violates both Rule #1 and Rule #2, it is invalid.

		Example 2:

		This is the initial configuration:
		A = []
		B = [1]
		C = [0, 2]

		Proposed move:
		Move 2 from list C to list B.

		Answer:
		First check whether the move satisfies or violates Rule #1. 2 is at the rightmost end of list C. Hence the move satisifies Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list B, to which 2 is moved. Maximum of list B is 1. 2 is larger than 1. Hence the move satisfies Rule #2.
		Since the Move 2 from list C to list B satisfies both Rule #1 and Rule #2, it is valid.

		Example 3:

		This is the initial configuration:
		A = [0, 1]
		B = []
		C = [2]

		Proposed move:
		Move 0 from list A to list B.

		Answer:
		First check whether the move satisfies or violates Rule #1. 0 is not at the rightmost end of list A, because 1 is at the rightmost end of list A. Hence the move violates Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list B, to which 0 is moved. Since list B is empty, there is no maximum value to compare with. Hence the move satisfies Rule #2.
		Since the Move 0 from list A to list B violates Rule #1, it is invalid.

		Example 4:

		This is the initial configuration:
		A = [0, 1, 2, 3]
		B = []
		C = []

		Proposed move:
		Move 0 from list A to list B.

		Answer:
		First check whether the move satisfies or violates Rule #1. 0 is not at the rightmost end of list A, because 3 is at the rightmost end of list A. Hence the move violates Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list B, to which 0 is moved. Since list B is empty, there is no maximum value to compare with. Hence the move satisfies Rule #2.
		Since the Move 0 from list A to list B violates Rule #1, it is invalid.

		Example 5:

		This is the initial configuration:
		A = [1]
		B = [0, 2 ,3]
		C = []

		Proposed move:
		Move 2 from list B to list C.

		Answer:
		First check whether the move satisfies or violates Rule #1. 2 is not at the rightmost end of list B, because 3 is at the rightmost end of list B. Hence the move violates Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list C, to which 2 is moved. Since list C is empty, there is no maximum value to compare with. Hence the move satisfies Rule #2.
		Since the Move 2 from list B to list C violates Rule #1, it is invalid.

		Example 6:

		This is the initial configuration:
		A = [0, 1]
		B = []
		C = [2, 3]

		Proposed move:
		Move 2 from list C to list B.

		Answer:
		First check whether the move satisfies or violates Rule #1. 2 is not at the rightmost end of list C, because 3 is at the rightmost end of list C. Hence the move violates Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list B, to which 2 is moved. Since list B is empty, there is no maximum value to compare with. Hence the move satisfies Rule #2.
		Since the Move 2 from list C to list B violates Rule #1, it is invalid.

		Example 7:

		This is the initial configuration:
		A = [0]
		B = [2, 3]
		C = [1]

		Proposed move:
		Move 2 from list B to list A.

		Answer:
		First check whether the move satisfies or violates Rule #1. 2 is not at the rightmost end of list B, because 3 is at the rightmost end of list B. Hence the move violates Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list A, to which 2 is moved. Maximum of list A is 0. 2 is larger than 0. Hence the move satisfies Rule #2.
		Since the Move 2 from list B to list A violates Rule #1, it is invalid.

		Example 8:

		This is the initial configuration:
		A = []
		B = [2, 3]
		C = [0, 1]

		Proposed move:
		Move 2 from list B to list C.

		Answer:
		First check whether the move satisfies or violates Rule #1. 2 is not at the rightmost end of list B, because 3 is at the rightmost end of list B. Hence the move violates Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list C, to which 2 is moved. Maximum of list C is 1. 2 is larger than 1. Hence the move satisfies Rule #2.
		Since the Move 2 from list B to list C violates Rule #1, it is invalid.

		Here is the task:

		This is the initial configuration:
		{}
		{}
		{}

		Proposed move:
		{}.

		Answer:

		""".format("A = "+str(state_A),"B = "+str(state_B),"C = "+str(state_C),gpt_truncated_move_proposal)


	move_validator_input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

	move_validator_input.append({
		"role": "user",
		"content": move_validator_prompt,
	})

	another_cur_try = 0
	while another_cur_try <10:
		try:

			validator_response = openai.ChatCompletion.create(
				engine='gpt-4-32k',
				messages=move_validator_input,temperature=0.0,top_p=0,
					max_tokens=500)

			another_cur_try+=1
			
			
			char_list_response = validator_response.choices[0].message.content.split('\n')[-1].replace(".","").split(" ")
			if 'invalid' in char_list_response:
				move_validity = 'no'
			else:
				move_validity = 'yes'

			

					
			# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			
			continue
	return move_validity


def actor_module_propose_two_actions(actor_input,temp_current_configuration,goal_config,reduced_prompt,step,max_content_limit_exceed_count):

	
	num_tries = 0
	while num_tries < 10:
		proposals = []
		cur_try = 0
		check_flag = 0
		one_response_flag = 0
		while cur_try <10:
			try:
				if check_flag == 1 or one_response_flag==1:

					actor_response = openai.ChatCompletion.create(
						engine='gpt-4-32k',
						messages=actor_input,temperature=0.1*cur_try,
							max_tokens=500)

				else:
					

					actor_response = openai.ChatCompletion.create(
						engine='gpt-4-32k',
						messages=actor_input,temperature=0.0, top_p= 0 ,
							max_tokens=500)

					# actor_response = openai.ChatCompletion.create(
					# 	engine='gpt-4-32k',
					# 	messages=actor_input,temperature=0.1*num_tries,
					# 		max_tokens=500)

				
				
				
				actor_truncated_response = []
				for k in range(len(actor_response.choices[0].message.content) - 17):
					sub_str = actor_response.choices[0].message.content[k:k+18]
					if 'Move' in sub_str and '.' not in sub_str and 'from' in sub_str and 'to' in sub_str and (('A' in sub_str and 'B' in sub_str ) or ('C' in sub_str and 'B' in sub_str ) or ('A' in sub_str and 'C' in sub_str )) :


						actor_truncated_response.append(sub_str)
					



				# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :
				print("actor_response>>",actor_response)
				if len(actor_truncated_response)>=2:

					break
				elif len(actor_truncated_response)==1:

					one_move_msg = """
					You provided just one valid next move. However it is possible to provide two valid next moves from the current configuration.
			
					This is the current configuration:
					{}
					{}
					{}
					
					This is the goal configuration:
					{}
					{}
					{}



					Please try again to give me only two different valid next moves possible from the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should be in the format as below:
					1. Move <N> from <src> to <trg>.


					""".format("A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
						
					actor_input.append({
							"role": "assistant",
							"content": actor_response.choices[0].message.content,
						})
						
					actor_input.append({
						"role": "user",
						"content": one_move_msg,
						})

					one_response_flag=1
					cur_try+=1
					continue

				else:

					hallucination_msg = """
					Current configuration is not the same as the goal configuration, so the puzzle is not solved yet. It is possible to provide valid next moves from the current configuration.
			
					This is the current configuration:
					{}
					{}
					{}
					
					This is the goal configuration:
					{}
					{}
					{}



					Please try again to give me only two different valid next moves possible from the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should be in the format as below:
					1. Move <N> from <src> to <trg>.


					""".format("A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
						
					actor_input.append({
							"role": "assistant",
							"content": actor_response.choices[0].message.content,
						})
						
					actor_input.append({
						"role": "user",
						"content": hallucination_msg,
						})
							

					cur_try+=1
					check_flag=1
					continue

			except Exception as e:
				err = f"Error: {str(e)}"

				if "This model's maximum context length is 32768 tokens" in err:
					print("length of input before and step number>>",len(actor_input),step)
					if max_content_limit_exceed_count==0:
						print("first time for an example")

						actor_input = [{"role": "system","content": "you are an AI assistant",}] +[{"role": "user","content": reduced_prompt,}]  + actor_input[101:] # skip first 50 conversations between user and assistant
					else:
						print("not first time for an example")
						actor_input = [{"role": "system","content": "you are an AI assistant",}] +[{"role": "user","content": reduced_prompt,}]  + actor_input[102:]

					max_content_limit_exceed_count+=1


				print(err)
				print("Length of input now>>",len(actor_input))
				time.sleep(120)
				cur_try+=1
				continue

		if len(actor_truncated_response)==2:
			proposals.append(actor_truncated_response[0])
			proposals.append(actor_truncated_response[1])


			move_validity1 = move_validator_module(temp_current_configuration[0],temp_current_configuration[1],temp_current_configuration[2],actor_truncated_response[0])
			move_validity2 = move_validator_module(temp_current_configuration[0],temp_current_configuration[1],temp_current_configuration[2],actor_truncated_response[1])
				
			if move_validity1 =='yes' and move_validity2 =='yes':
				break
				
			elif move_validity1 =='yes' and move_validity2 =='no':
				
				internal_configuration_msg = """
				{} is invalid. 
				
				This is the current configuration:
				{}
				{}
				{}
				
				This is the goal configuration:
				{}
				{}
				{}

				Please try again to give me only two different valid next moves possible from the current configuration that would help in reaching the goal configuration using as few moves as possible.
				Your answer should be in the format as below:
				1. Move <N> from <src> to <trg>.

				""" .format(actor_truncated_response[1],"A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
				num_tries+=1

			elif move_validity1 =='no' and move_validity2 =='yes':
				
				internal_configuration_msg = """
				{} is invalid. 
				
				This is the current configuration:
				{}
				{}
				{}

				This is the goal configuration:
				{}
				{}
				{}
				

				Please try again to give me only two different valid next moves possible from the current configuration that would help in reaching the goal configuration using as few moves as possible.
				Your answer should be in the format as below:
				1. Move <N> from <src> to <trg>.

				""" .format(actor_truncated_response[0],"A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
				num_tries+=1
			else:
				
				
				internal_configuration_msg = """
				{} is invalid. {} is invalid.
				
				This is the current configuration:
				{}
				{}
				{}
				
				This is the goal configuration:
				{}
				{}
				{}



				Please try again to give me only two different valid next moves possible from the current configuration that would help in reaching the goal configuration using as few moves as possible.
				Your answer should be in the format as below:
				1. Move <N> from <src> to <trg>.


				""".format(actor_truncated_response[0],actor_truncated_response[1],"A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))

				num_tries+=1
		else:
			proposals.append(actor_truncated_response[0])
			proposals.append(actor_truncated_response[0])

			move_validity1 = move_validator_module(temp_current_configuration[0],temp_current_configuration[1],temp_current_configuration[2],actor_truncated_response[0])
			if move_validity1 =='yes':
				break
				
			else:
				
				internal_configuration_msg = """
				{} is invalid. 
				
				This is the current configuration:
				{}
				{}
				{}
				

				This is the goal configuration:
				{}
				{}
				{}

				Please try again to give me only two different valid next moves possible from the current configuration that would help in reaching the goal configuration using as few moves as possible.
				Your answer should be in the format as below:
				1. Move <N> from <src> to <trg>.

				""" .format(actor_truncated_response[0],"A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
				num_tries+=1
				




		actor_input.append({
		"role": "assistant",
		"content": actor_response.choices[0].message.content,
		})
		
		actor_input.append({
		"role": "user",
		"content": internal_configuration_msg,
		})
			


	

	return proposals,actor_response, actor_input, max_content_limit_exceed_count




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
			time.sleep(120)
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
		{}
		{}
		{}
		
		Answer:

		""".format("A = "+str(state_A),"B = "+str(state_B),"C = "+str(state_C),"A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))

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
			time.sleep(120)
			cur_try+=1
			continue

	print("evaluator_response>>",evaluator_response)

	for k in range(len(evaluator_response.choices[0].message.content) - 107):
		if evaluator_response.choices[0].message.content[k:k+108] == 'The minimum number of valid moves required to reach the goal configuration from the current configuration is' or evaluator_response.choices[0].message.content[k:k+108] == 'the minimum number of valid moves required to reach the goal configuration from the current configuration is':

			return int(evaluator_response.choices[0].message.content[k+109])



for i in range(26,66):
	A=all_As[i] 

	B=all_Bs[i]

	C=all_Cs[i]
	num_disks = max(A+B+C)+1
	
	start_configuration = [A,B,C]

	all_subgoals = []
	if 0 in start_configuration[2]:
		generated_subgoal = subgoal_generator(start_configuration)

		if len(generated_subgoal)!=0:
			all_subgoals.append(generated_subgoal[0])
	else:
		if start_configuration == [[1,2,3],[0],[]] :
			all_subgoals.append([[],[2,3],[0,1]])
		elif start_configuration == [[0],[1,2,3],[]]:
			all_subgoals.append([[2,3],[],[0,1]])

		else:
#         if start_configuration[0]==[1] or start_configuration[1]==[1] or start_configuration[2]==[1] or
		
			generated_subgoal = subgoal_generator(start_configuration)
			if (1 in generated_subgoal[0][0] and 1 in start_configuration[0]) or (1 in generated_subgoal[0][1] and 1 in start_configuration[1]) or (1 in generated_subgoal[0][2] and 1 in start_configuration[2]) or (start_configuration == [[0,2,3],[],[1]]) or (start_configuration == [[],[0,2,3],[1]]) or (start_configuration == [[0,1],[],[2,3]]) or (start_configuration == [[],[0,1],[2,3]]) :
				all_subgoals.append(generated_subgoal[0])
				generated_subgoal = subgoal_generator(generated_subgoal[0])
				all_subgoals.append(generated_subgoal[0])

			else:

				file_baseline = open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/optimal policy/problem{}.log'.format(i+1), 'r')
				lines_baseline = file_baseline.read().splitlines()
				file_baseline.close()

				initial_A_B_C = []
				char_int_mapping = {'A':0,'B':1,'C':2}
				for t in range(len(lines_baseline)):

					if  'Initial configuration' in lines_baseline[t]:
						initial_A_B_C.append(json.loads(lines_baseline[t+1].split("=")[-1]))
						initial_A_B_C.append(json.loads(lines_baseline[t+2].split("=")[-1]))
						initial_A_B_C.append(json.loads(lines_baseline[t+3].split("=")[-1]))
						break
				valid_moves_decoded_tuples = []
				for t in range(len(lines_baseline)):


					if 'Move' in lines_baseline[t] and 'from' in lines_baseline[t] and 'to' in lines_baseline[t] and (('A' in lines_baseline[t] and 'B' in lines_baseline[t] ) or ('C' in lines_baseline[t] and 'B' in lines_baseline[t] ) or ('A' in lines_baseline[t] and 'C' in lines_baseline[t] )):



						valid_move_line = lines_baseline[t].split(':')[-1].strip()

						valid_moves_decoded_tuples.append((int(valid_move_line.split(" ")[1]),valid_move_line.split(" ")[3],valid_move_line.split(" ")[5]))



				all_optimal_configuration_after_moves = []
				all_optimal_configuration_after_moves.append(deepcopy(initial_A_B_C))
				for t in range(len(valid_moves_decoded_tuples)):



					num = initial_A_B_C[char_int_mapping[valid_moves_decoded_tuples[t][1]]].pop()
					initial_A_B_C[char_int_mapping[valid_moves_decoded_tuples[t][2]]].append(num)
					if (1 in generated_subgoal[0][0] and initial_A_B_C[0]==[1]) or (1 in generated_subgoal[0][1] and initial_A_B_C[1]==[1]) :

						all_subgoals.append(deepcopy(initial_A_B_C))
						break




				all_subgoals.append(generated_subgoal[0])
				generated_subgoal = subgoal_generator(generated_subgoal[0])
				all_subgoals.append(generated_subgoal[0])

		
			# generated_subgoal = subgoal_generator(start_configuration)
			# if 1 in generated_subgoal[0][0]:
			#     all_subgoals.append([[1],[0],[2,3]])
			# else:
			#     all_subgoals.append([[0],[1],[2,3]])

			# all_subgoals.append(generated_subgoal[0])
			# generated_subgoal = subgoal_generator(generated_subgoal[0])
			# all_subgoals.append(generated_subgoal[0])
			
		

	# all_subgoals = []
	
	# generated_subgoal = subgoal_generator(start_configuration)

	# while len(generated_subgoal)!=0:
	# 	all_subgoals.append(generated_subgoal[0])
	# 	generated_subgoal = subgoal_generator(generated_subgoal[0])

	print("all subgoals generated>>",all_subgoals)
	final_target_configuration = [[],[],[0,1,2,3]]
	all_subgoals.append(final_target_configuration)

	print("all subgoals generated plus final target>>",all_subgoals)


	

		
	# elif num_disks ==4:

	# 	if 0 not in C:
	# 		if 0 in A:
	# 			target_configuration = [[],[1,2,3],[0]]
	# 		else:
	# 			target_configuration = [[1,2,3],[],[0]]
	# 	else:
	# 		if 1 not in C:
	# 			if 1 in A:
	# 				target_configuration = [[],[2,3],[0,1]]
	# 			else:
	# 				target_configuration = [[2,3], [], [0,1]]

	# 		else:
	# 			if 2 not in C:
	# 				if 2 in A:

	# 					target_configuration = [[],[3],[0,1,2]]
	# 				else:
	# 					target_configuration = [[3], [], [0,1,2]]


	# 			else:

	# 				target_configuration = [[],[], [0,1,2,3]]

		# final_target_configuration = [[],[],[0,1,2,3]]




		# target_configuration = [[],[1,2,3],[0]]
	# else:


	# 	target_configuration = [[],[],[0,1,2,3,4]]

	current_configuration = deepcopy(start_configuration)

	count = 0
	



	prompt = """Consider the following puzzle problem:
	
	Problem description:
	- There are three lists labeled A, B, and C.
	- There is a set of numbers distributed among those three lists.
	- You can only move numbers from the rightmost end of one list to the rightmost end of another list.

	Rule #1: You can only move a number if it is at the rightmost end of its current list.
	Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.

	A move is valid if it satisfies both Rule #1 and Rule #2.
	A move is invalid if it violates either Rule #1 or Rule #2.
	
	Goal: The goal is to end up in the goal configuration. 


	Here are nine examples:

	{}

	Here is the task:

	This is the starting configuration:
	{}
	{}
	{}
	This is the goal configuration:
	{}
	{}
	{}

	Give me only two different valid next moves possible from the starting configuration that would help in reaching the goal configuration using as few moves as possible. 
	Your answer should be in the format as below:
	1. Move <N> from <src> to <trg>.

	""".format(standard_prompt,"A = "+str(A),"B = "+str(B),"C = "+str(C),"A = "+str(all_subgoals[count][0]),"B = "+str(all_subgoals[count][1]),"C = "+str(all_subgoals[count][2]))


	reduced_prompt = """Consider the following puzzle problem:
	
	Problem description:
	- There are three lists labeled A, B, and C.
	- There is a set of numbers distributed among those three lists.
	- You can only move numbers from the rightmost end of one list to the rightmost end of another list.

	Rule #1: You can only move a number if it is at the rightmost end of its current list.
	Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.

	A move is valid if it satisfies both Rule #1 and Rule #2.
	A move is invalid if it violates either Rule #1 or Rule #2.
	
	Goal: The goal is to end up in the goal configuration.
	

	Here are nine examples:

	{}

	Here is the task:

	This is the starting configuration:
	{}
	{}
	{}
	This is the goal configuration:
	{}
	{}
	{}

	""".format(standard_prompt,"A = "+str(A),"B = "+str(B),"C = "+str(C),"A = "+str(all_subgoals[count][0]),"B = "+str(all_subgoals[count][1]),"C = "+str(all_subgoals[count][2]))


	
	print("starting prompt>>",prompt)

	input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

	input.append({
		"role": "user",
		"content": prompt,
	})

	


	flag=0
	total_reward = 0
	step = 0
	num_tries=0
	max_content_limit_exceed_count = 0
	depth_flag=0
	
	for step in range(50):
		


		first_temp_current_configuration = deepcopy(current_configuration)
	
		


		print("step>>",step)
		print("first config>>",first_temp_current_configuration)
		move_proposals, response, input, max_content_limit_exceed_count = actor_module_propose_two_actions(input,first_temp_current_configuration,all_subgoals[count],reduced_prompt,step,max_content_limit_exceed_count)
		print("move proposals>>",move_proposals)
		# print("input now>>>",input)
			
		
		
		next_temp_current_configuration1 = state_predictor_module(first_temp_current_configuration[0], first_temp_current_configuration[1], first_temp_current_configuration[2] ,move_proposals[0])
		next_temp_current_configuration2 = state_predictor_module(first_temp_current_configuration[0], first_temp_current_configuration[1], first_temp_current_configuration[2] ,move_proposals[1])

		print("next config 1>>",next_temp_current_configuration1)
		print("next config 2>>",next_temp_current_configuration2)

		if (next_temp_current_configuration1 == all_subgoals[count]) or (next_temp_current_configuration2 == all_subgoals[count]):

			moves_from_next_temp_current_configuration1 = state_evaluator_module(next_temp_current_configuration1[0],next_temp_current_configuration1[1],next_temp_current_configuration1[2],all_subgoals[count])
			moves_from_next_temp_current_configuration2 = state_evaluator_module(next_temp_current_configuration2[0],next_temp_current_configuration2[1],next_temp_current_configuration2[2],all_subgoals[count])

			if moves_from_next_temp_current_configuration1 < moves_from_next_temp_current_configuration2:
				next_move_chosen_for_system = move_proposals[0]
			elif moves_from_next_temp_current_configuration2 < moves_from_next_temp_current_configuration1:
				next_move_chosen_for_system = move_proposals[1]
			else:
				next_move_chosen_for_system = move_proposals[np.random.randint(0,2)]

			print("target reached at first rollout and move chosen>>>",next_move_chosen_for_system)

		else:
			

			input.append({
			"role": "assistant",
			"content": response.choices[0].message.content,
				})


			internal_configuration_msg = """
			This is the current configuration:
			{}
			{}
			{}

			This is the goal configuration:
			{}
			{}
			{}
			
		
			Give me only two different valid next moves possible from the current configuration that would help in reaching the goal configuration using as few moves as possible.
			Your answer should be in the format as below:
			1. Move <N> from <src> to <trg>.

			""" .format("A = "+str(next_temp_current_configuration1[0]),"B = "+str(next_temp_current_configuration1[1]),"C = "+str(next_temp_current_configuration1[2]), "A = "+str(all_subgoals[count][0]),"B = "+str(all_subgoals[count][1]),"C = "+str(all_subgoals[count][2]))
	

			input.append({
			"role": "user",
			"content": internal_configuration_msg,
		})

			next_move_proposals1, response1, input, max_content_limit_exceed_count = actor_module_propose_two_actions(input,next_temp_current_configuration1,all_subgoals[count],reduced_prompt,step,max_content_limit_exceed_count)
			print("move proposals from config 1>>",next_move_proposals1)

			input.append({
			"role": "assistant",
			"content": response1.choices[0].message.content,
				})


			internal_configuration_msg = """
			This is the current configuration:
			{}
			{}
			{}

			This is the goal configuration:
			{}
			{}
			{}
			
			
			Give me only two different valid next moves possible from the current configuration that would help in reaching the goal configuration using as few moves as possible.
			Your answer should be in the format as below:
			1. Move <N> from <src> to <trg>.

			""" .format("A = "+str(next_temp_current_configuration2[0]),"B = "+str(next_temp_current_configuration2[1]),"C = "+str(next_temp_current_configuration2[2]), "A = "+str(all_subgoals[count][0]),"B = "+str(all_subgoals[count][1]),"C = "+str(all_subgoals[count][2]))
	

			input.append({
			"role": "user",
			"content": internal_configuration_msg,
		})


			next_move_proposals2, response2, input, max_content_limit_exceed_count = actor_module_propose_two_actions(input,next_temp_current_configuration2,all_subgoals[count],reduced_prompt,step,max_content_limit_exceed_count)
			
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


			moves_from_next_next_temp_current_configuration1_1 = state_evaluator_module(next_next_temp_current_configuration1_1[0],next_next_temp_current_configuration1_1[1],next_next_temp_current_configuration1_1[2],all_subgoals[count])
			moves_from_next_next_temp_current_configuration1_2 = state_evaluator_module(next_next_temp_current_configuration1_2[0],next_next_temp_current_configuration1_2[1],next_next_temp_current_configuration1_2[2],all_subgoals[count])
			
			moves_from_next_next_temp_current_configuration2_1 = state_evaluator_module(next_next_temp_current_configuration2_1[0],next_next_temp_current_configuration2_1[1],next_next_temp_current_configuration2_1[2],all_subgoals[count])
			moves_from_next_next_temp_current_configuration2_2 = state_evaluator_module(next_next_temp_current_configuration2_2[0],next_next_temp_current_configuration2_2[1],next_next_temp_current_configuration2_2[2],all_subgoals[count])
			
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
		
		
		
		no_to_move = int(next_move_chosen_for_system.split(" ")[1])
		source_list = next_move_chosen_for_system.split(" ")[3]
		target_list = next_move_chosen_for_system.split(" ")[5]
		# print(gpt_response,no_to_move,source_list,target_list)
		total_reward+=-1
		response_flag =0
		if no_to_move not in current_configuration[char_int_mapping[source_list]]:
			user_message = next_move_chosen_for_system + '.' + "\nInvalid move because {} is not in {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
			reward_message = "Invalid move because {} is not in {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
			response_flag =1
		else:
			if current_configuration[char_int_mapping[source_list]][-1]!= no_to_move:
				user_message = next_move_chosen_for_system + '.' + "\nInvalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
				reward_message = "Invalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
				response_flag =1
			else:
				if len(current_configuration[char_int_mapping[target_list]]):
					max_target_list = max(current_configuration[char_int_mapping[target_list]])
				else:
					max_target_list = -1

				if no_to_move < max_target_list:
					user_message = next_move_chosen_for_system + '.' + "\nInvalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
					reward_message = "Invalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
					response_flag=1
				else:
					user_message = next_move_chosen_for_system+'.'+'\nFor each move you get a penalty of -1.'
					reward_message = "For each move you get a penalty of -1."
					current_configuration[char_int_mapping[source_list]].pop()
					current_configuration[char_int_mapping[target_list]].append(no_to_move)

		if response_flag==1:
			total_reward+=-10

		
		if current_configuration == all_subgoals[count]:
			count+=1
			# target_configuration = final_target_configuration
			
			
		if current_configuration == final_target_configuration:
			flag=1
			total_reward+=100
			with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 standard icl with improved error monitor, generic planner, try propose two moves with temperature, no previous step context, max 3 subgoals generator 4 numbers step by step external feedback/problem{}.log'.format(i+1), 'a') as w:
				w.write(prompt +'\n'+"Solved problem in {} steps. Total reward = {}".format(step+1,total_reward))

			break


		configuration_msg = """This is the current configuration:
		{}
		{}
		{}

		This is the goal configuration:
		{}
		{}
		{}

		Give me only two different valid next moves possible from the current configuration that would help in reaching the goal configuration using as few moves as possible.
		Your answer should be in the format as below:
		1. Move <N> from <src> to <trg>.

		""".format("A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]),"A = "+str(all_subgoals[count][0]),"B = "+str(all_subgoals[count][1]),"C = "+str(all_subgoals[count][2]))

		


		prompt+="\n"+user_message+"\n"+configuration_msg

		print("external feedback>>",reward_message+"\n"+configuration_msg)

	# 	input.append({
	# 	"role": "assistant",
	# 	"content": response2.choices[0].message.content,
	# })
	# 	input.append({
	# 	"role": "user",
	# 	"content": user_message+"\n"+configuration_msg,
	# })
		
		

		
		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": prompt,
		})


		

		
		
	

			# print("error monitor feedback>>>",validator_response.choices[0].message.content + "\n"+configuration_msg)

	if flag==0:
		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 standard icl with improved error monitor, generic planner, try propose two moves with temperature, no previous step context, max 3 subgoals generator 4 numbers step by step external feedback/problem{}.log'.format(i+1), 'a') as w:
			w.write(prompt +'\n'+"Timed out. Couldn't solve problem in 50 steps. Total reward = {}".format(total_reward))


	


	
	print("done solving problem {}".format(i+1))

