import openai
from gen_start_config import *
from copy import deepcopy
import time
import re
import json
import os
import argparse
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"

all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
char_int_mapping = {'A':0,'B':1,'C':2}

def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)

def move_validator_module(state_A, state_B, state_C, gpt_truncated_move_proposal,num_input_tokens,num_output_tokens):

	move_validator_prompt = """Consider the following puzzle problem:

		Here are two examples:
		Example 1:

		Problem description:
		- There are three lists labeled A, B, and C.
		- There is a set of numbers distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2.

		Goal: The goal is to check if the proposed move satisfies or violates Rule #1 and Rule #2 and based on that if it is a valid or invalid move.

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

		Problem description:
		- There are three lists labeled A, B, and C.
		- There is a set of numbers distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2.
		
		Goal: The goal is to check if the proposed move satisfies or violates Rule #1 and Rule #2 and based on that if it is a valid or invalid move.

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


		Here is the task:

		Problem description:
		- There are three lists labeled A, B, and C.
		- There is a set of numbers distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2.
		
		Goal: The goal is to check if the proposed move satisfies or violates Rule #1 and Rule #2 and based on that if it is a valid or invalid move.

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
	while another_cur_try <5:
		try:
			
			validator_response = openai.ChatCompletion.create(
				engine='gpt-4-32k',
				messages=move_validator_input,temperature=0.0,top_p=0,
					max_tokens=500)

			num_input_tokens+=validator_response["usage"]["prompt_tokens"]
			num_output_tokens+=validator_response["usage"]["completion_tokens"]

			another_cur_try+=1
			
			print("validator response>>",validator_response.choices[0].message.content)
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
			time.sleep(60)
			
			continue

	return move_validity,validator_response.choices[0].message.content,num_input_tokens,num_output_tokens


def state_predictor_module(state_A,state_B,state_C,move_msg,num_input_tokens,num_output_tokens):

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
	check_flag=0
	while cur_try<10:

		try:

			if check_flag==0:


				predictor_response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=state_predictor_input,temperature=0.0,top_p=0,
						max_tokens=200)

			else:
				predictor_response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=state_predictor_input,temperature=0.1*cur_try,
						max_tokens=200)


			num_input_tokens+=predictor_response["usage"]["prompt_tokens"]
			num_output_tokens+=predictor_response["usage"]["completion_tokens"]

			print("predictor_response>>",predictor_response)
			state_predictor_output = []
			splits = predictor_response.choices[0].message.content.split("=")
			for sp in splits:

				if '[' in sp and ']' in sp:

					state_predictor_output.append(json.loads(sp[sp.index('['):sp.index(']')+1]))

			if len(state_predictor_output) >0:



				break
			else:
				check_flag=1
				cur_try+=1
				continue

			

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue

	
	
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[0].split("=")[-1]))
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[1].split("=")[-1]))
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[2].split("=")[-1]))
	return state_predictor_output,num_input_tokens,num_output_tokens



def actor_module_propose_action(previous_move,actor_input,temp_current_configuration,goal_config,step,max_content_limit_exceed_count,num_input_tokens,num_output_tokens):


	num_tries = 0
	while num_tries < 10:
		cur_try = 0
		check_flag = 0
		while cur_try <10:
			try:
				if check_flag==1:
					


					actor_response = openai.ChatCompletion.create(
						engine='gpt-4-32k',
						messages=actor_input,temperature=0.1*cur_try,
							max_tokens=200)

					num_input_tokens+=actor_response["usage"]["prompt_tokens"]
					num_output_tokens+=actor_response["usage"]["completion_tokens"]

				else:
					
					actor_response = openai.ChatCompletion.create(
						engine='gpt-4-32k',
						messages=actor_input,temperature=0.0,top_p=0,
							max_tokens=200)

					num_input_tokens+=actor_response["usage"]["prompt_tokens"]
					num_output_tokens+=actor_response["usage"]["completion_tokens"]


				
				
				
				
				actor_truncated_response = None
				for k in range(len(actor_response.choices[0].message.content) - 27):
					sub_str = actor_response.choices[0].message.content[k:k+28]
					if 'Move' in sub_str and 'from list' in sub_str and 'to list' in sub_str and (('A' in sub_str and 'B' in sub_str ) or ('C' in sub_str and 'B' in sub_str ) or ('A' in sub_str and 'C' in sub_str )) :
						

						actor_truncated_response = sub_str

				print("actor_response>>",actor_response)
				if actor_truncated_response is not None:
					break
				else:
					# hallucination_msg = """
					# Current configuration doesn't match the goal configuration, so the puzzle is not solved yet. It is possible to provide a next move from the current configuration.
			
					# This is the current configuration:
					# {}
					# {}
					# {}
					
					# This is the goal configuration:
					# A = []
					# B = []
					# {}



					# Please try again to give me the next move from the current configuration that would help in reaching the goal configuration using as few moves as possible.
					# Your answer should be in the format as below:
					# Move <N> from <src> to <trg>.


					# """.format("A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), goal_config)
						

					# actor_input.append({
					# 		"role": "assistant",
					# 		"content": actor_response.choices[0].message.content,
					# 	})
						
					# actor_input.append({
					# 	"role": "user",
					# 	"content": hallucination_msg,
						# })
							


					cur_try+=1
					check_flag =1
					# print("move response not found for problem {}, step {}. Here is the original full response>> {}".format(i+1,step,response.choices[0].message.content))
					continue
				# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :
				
				# print("configuration>>",current_configuration)
				# print("gpt response>>",gpt_truncated_response)
			

			except Exception as e:
				
				err = f"Error: {str(e)}"

				# if "This model's maximum context length is 32768 tokens" in err:
				# 	print("length of input before and step number>>",len(actor_input),step)
				# 	if max_content_limit_exceed_count==0:
				# 		print("first time for an example")

				# 		actor_input = [{"role": "system","content": "you are an AI assistant",}] +[{"role": "user","content": reduced_prompt,}]  + actor_input[101:] # skip first 50 conversations between user and assistant
				# 	else:
				# 		print("not first time for an example")
				# 		actor_input = [{"role": "system","content": "you are an AI assistant",}] +[{"role": "user","content": reduced_prompt,}]  + actor_input[102:]

				# 	max_content_limit_exceed_count+=1


				print(err)
				print("Length of input now>>",len(actor_input))
				time.sleep(60)
				cur_try+=1
				continue

		if actor_truncated_response is None:
			actor_truncated_response = previous_move
		else:
			previous_move = actor_truncated_response

		move_validity, move_validator_response,num_input_tokens,num_output_tokens = move_validator_module(temp_current_configuration[0],temp_current_configuration[1],temp_current_configuration[2],actor_truncated_response,num_input_tokens,num_output_tokens)

		if move_validity == "yes":
			break
		else:

			actor_input.append({
				"role": "assistant",
				"content": actor_response.choices[0].message.content,
			})

			internal_configuration_msg = """
			{}

			This is the current configuration:
			{}
			{}
			{}

			This is the goal configuration:
			A = []
			B = []
			{}

			Please try again to give me the next move from the current configuration, that would help in reaching the goal configuration using as few moves as possible. Please make sure that the next move satisfies both Rule #1 and Rule #2. 
			Your answer should be in the format as below:
			Move <N> from list <src> to list <trg>.

			""".format(move_validator_response,"A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]),goal_config)


			actor_input.append({
			"role": "user",
			"content": internal_configuration_msg,
		})
			
			num_tries+=1



	return actor_truncated_response,previous_move, max_content_limit_exceed_count,num_tries+1,num_input_tokens,num_output_tokens

parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--openai_api_key', type = str, help='openai key', required= True)
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)

args = parser.parse_args()
print(args)

openai.api_key = args.openai_api_key

num_input_tokens = 0 
num_output_tokens = 0
num_move_validator_interactions_allprobs_eachstep = []

for i in range(26):
	previous_move = None

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

	next_state_prediction = deepcopy(start_configuration)
	current_configuration = deepcopy(start_configuration)


	prompt = """Consider the following puzzle problem:
	
	Problem description:
	- There are three lists labeled A, B, and C.
	- There is a set of numbers distributed among those three lists.
	- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
	Rule #1: You can only move a number if it is at the rightmost end of its current list.
	Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.

	A move is valid if it satisfies both Rule #1 and Rule #2.
	A move is invalid if it violates either Rule #1 or Rule #2.

	
	Goal: The goal is to end up in the configuration where all numbers are in list C, in ascending order using minimum number of moves.
	

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
	Move <N> from list <src> to list <trg>.

	""".format("A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])


	
	external_environment_prompt = deepcopy(prompt)

	# print("starting prompt>>",prompt)

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
	for step in range(50):


		# print("step number>>",step)
		# print("current_configuration>>",current_configuration)
   
   
	
	

		

		first_temp_current_configuration = deepcopy(next_state_prediction)


	
		


		print("step, num input tokens, num output tokens>>",step,num_input_tokens,num_output_tokens)
		print("config from state predictor>>",first_temp_current_configuration)
		move_proposal,previous_move, max_content_limit_exceed_count,num_move_validator_interactions,num_input_tokens,num_output_tokens = actor_module_propose_action(previous_move,input,first_temp_current_configuration,number_target_mapping[num_disks],step,max_content_limit_exceed_count,num_input_tokens,num_output_tokens)
		
		num_move_validator_interactions_allprobs_eachstep.append(num_move_validator_interactions)
		print("number of move validator interactions>>",num_move_validator_interactions)
		print("move proposal>>",move_proposal)
		

		# print("error monitor gpt full response>>",validator_response.choices[0].message.content)
		# print("move_validity>>",move_validity)
		
		
		no_to_move = int(move_proposal.split(" ")[1])
		source_list = move_proposal.split(" ")[4]
		target_list = move_proposal.split(" ")[7]

		# print(gpt_response,no_to_move,source_list,target_list)
		# external environment evaluation
		total_reward+=-1
		response_flag =0
		if no_to_move not in current_configuration[char_int_mapping[source_list]]:
			user_message = move_proposal+"." + "\nInvalid move because {} is not in list {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
			reward_message = "Invalid move because {} is not in list {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
			response_flag =1
		else:
			if current_configuration[char_int_mapping[source_list]][-1]!= no_to_move:
				user_message = move_proposal + "." + "\nInvalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
				reward_message = "Invalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
				response_flag =1
			else:
				if len(current_configuration[char_int_mapping[target_list]]):
					max_target_list = max(current_configuration[char_int_mapping[target_list]])
				else:
					max_target_list = -1

				if no_to_move < max_target_list:
					user_message = move_proposal +"." + "\nInvalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
					reward_message = "Invalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
					response_flag=1
				else:
					user_message = move_proposal+'.'+'\nFor each move you get a penalty of -1.'
					reward_message = "For each move you get a penalty of -1."
					current_configuration[char_int_mapping[source_list]].pop()
					current_configuration[char_int_mapping[target_list]].append(no_to_move)

		if response_flag==1:
			total_reward+=-10

		next_state_prediction,num_input_tokens,num_output_tokens = state_predictor_module(first_temp_current_configuration[0], first_temp_current_configuration[1], first_temp_current_configuration[2] ,move_proposal,num_input_tokens,num_output_tokens)
		
		internal_configuration_msg = """This is the current configuration:
		{}
		{}
		{}

		This is the goal configuration:
		A = []
		B = []
		{}

		Give me only the next move from the current configuration, that would help in reaching the goal configuration using as few moves as possible. 
		Your answer should be in the format as below:
		Move <N> from list <src> to list <trg>.

		""".format("A = "+str(next_state_prediction[0]),"B = "+str(next_state_prediction[1]),"C = "+str(next_state_prediction[2]),number_target_mapping[num_disks])

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
		Move <N> from list <src> to list <trg>.

		""".format("A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]),number_target_mapping[num_disks])

		


		prompt+="\n"+move_proposal+ "." +"\n"+internal_configuration_msg

		external_environment_prompt+="\n"+user_message +"\n"+configuration_msg

		print("external feedback>>",user_message+"\n"+configuration_msg)

	# 	input.append({
	# 	"role": "assistant",
	# 	"content": response.choices[0].message.content,
	# })
	# 	input.append({
	# 	"role": "user",
	# 	"content": reward_message+"\n"+configuration_msg,
	# })


		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": prompt,
		})

		
		if next_state_prediction == target_configuration:
			flag=1
			if current_configuration==target_configuration:

				total_reward+=100
			
			test_dir = './logs/'
			check_path(test_dir)
			output_dir = test_dir + args.output_dir + '/'
			check_path(output_dir)

			with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
				w.write(prompt +'\n'+"Solved problem in {} steps. Total reward = {}".format(step+1,total_reward))

			with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
				w.write("\nExternal environment feedback>>>>\n"+external_environment_prompt +'\n'+"Solved problem in {} steps. Total reward = {}".format(step+1,total_reward))


			
			
			break

	
		
			
			

			# print("error monitor feedback>>>",validator_response.choices[0].message.content + "\n"+configuration_msg)

	if flag==0:

		test_dir = './logs/'
		check_path(test_dir)
		output_dir = test_dir + args.output_dir + '/'
		check_path(output_dir)

		with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
			w.write(prompt +'\n'+"Timed out. Couldn't solve problem in 50 steps. Total reward = {}".format(total_reward))

		with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
			w.write("\nExternal environment feedback>>>>\n"+external_environment_prompt +'\n'+"Timed out. Couldn't solve problem in 50 steps. Total reward = {}".format(total_reward))


		


	

	print("number of input and output tokens to gpt till now>>",num_input_tokens,num_output_tokens)
	
	print("done solving problem {}".format(i+1))


