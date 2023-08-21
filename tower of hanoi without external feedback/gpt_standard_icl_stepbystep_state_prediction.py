import openai
from gen_start_config import *
from toh_five_shot_examples import standard_prompt
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

def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)

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

parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--openai_api_key', type = str, help='openai key', required= True)
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)

args = parser.parse_args()
print(args)

openai.api_key = args.openai_api_key

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
char_int_mapping = {'A':0,'B':1,'C':2}
num_input_tokens = 0 
num_output_tokens = 0
for i in range(26):
	if (i+1)!=3 and (i+1)!=22:
		
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
		

		

		

		prompt = """

		Consider the following puzzle problem:

		Problem description:
		- There are three lists labeled A, B, and C.
		- There is a set of numbers distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.

		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2.


		Goal: The goal is to end up in the configuration where all numbers are in list C, in ascending order using minimum number of moves.

		Here are five examples:

		{}

		Here is the task:

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

		""".format(standard_prompt,"A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])

		external_environment_prompt = deepcopy(prompt)

		
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
		for step in range(50):
			print("step, num input tokens, num output tokens>>",step,num_input_tokens,num_output_tokens)
			# print("prompt>>",prompt)
	   
			first_temp_current_configuration = deepcopy(next_state_prediction)
		
		

			# input = [{
			# 	"role": "system",
			# 	"content": "you are an AI assistant",
			# }]

			# input.append({
			# 	"role": "user",
			# 	"content": prompt,
			# })

			cur_try = 0
			check_flag=0
			while cur_try <10:
				try:
					if check_flag==1:
						

						response = openai.ChatCompletion.create(
						engine='gpt-4-32k',
						messages=input,temperature=0.1*cur_try,
							max_tokens=200)
						num_input_tokens+=response["usage"]["prompt_tokens"]
						num_output_tokens+=response["usage"]["completion_tokens"]

					else:
						

						response = openai.ChatCompletion.create(
						engine='gpt-4-32k',
						messages=input,temperature=0.0,top_p=0,
							max_tokens=200)
						num_input_tokens+=response["usage"]["prompt_tokens"]
						num_output_tokens+=response["usage"]["completion_tokens"]

									
					
					gpt_truncated_response = None
					for k in range(len(response.choices[0].message.content) - 17):
						sub_str = response.choices[0].message.content[k:k+18]
						if 'Move' in sub_str and 'from' in sub_str and 'to' in sub_str and (('A' in sub_str and 'B' in sub_str ) or ('C' in sub_str and 'B' in sub_str ) or ('A' in sub_str and 'C' in sub_str )) :


							gpt_truncated_response = sub_str
					# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :
					print("gpt full response>>",response.choices[0].message.content)
					if gpt_truncated_response is not None:

						break
					else:
						cur_try+=1
						check_flag=1
						continue

				except Exception as e:
					err = f"Error: {str(e)}"
					print(err)
					time.sleep(60)
					cur_try+=1
					
					continue

			
			if gpt_truncated_response is None:
				gpt_truncated_response = previous_gpt_truncated_response
			else:
				previous_gpt_truncated_response = gpt_truncated_response
			# print("gpt full response>>>",response.choices[0].message.content)
			# print("gpt truncated response>>>",gpt_truncated_response)
			# gpt_orig_message = response.choices[0].message.content
			# if "apolog" in gpt_orig_message:
			# 	move_index =0 
			# 	for idx,split_str in enumerate(gpt_orig_message.split(":")):
			# 	    if "correct next move" in split_str or "next move" in split_str or "correct move" in split_str or "next valid move" in split_str:
			# 	        move_index = idx+1
						

			# 	gpt_response = gpt_orig_message.split(":")[move_index].split(".")[0].replace(".","")
			# else:

			# 	gpt_response = gpt_orig_message.split(".")[0].replace(".","")
			print("gpt truncated response>>>",gpt_truncated_response)
			no_to_move = int(gpt_truncated_response.split(" ")[1])
			source_list = gpt_truncated_response.split(" ")[3]
			target_list = gpt_truncated_response.split(" ")[5]
			# print(gpt_response,no_to_move,source_list,target_list)
			total_reward+=-1
			response_flag =0
			if no_to_move not in current_configuration[char_int_mapping[source_list]]:
				user_message = gpt_truncated_response + "." + "\nInvalid move because {} is not in {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
				reward_message = "Invalid move because {} is not in {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
				response_flag =1
			else:
				if current_configuration[char_int_mapping[source_list]][-1]!= no_to_move:
					user_message = gpt_truncated_response + "." + "\nInvalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
					reward_message = "Invalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
					response_flag =1
				else:
					if len(current_configuration[char_int_mapping[target_list]]):
						max_target_list = max(current_configuration[char_int_mapping[target_list]])
					else:
						max_target_list = -1

					if no_to_move < max_target_list:
						user_message = gpt_truncated_response + "." + "\nInvalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
						reward_message = "Invalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
						response_flag=1
					else:
						user_message = gpt_truncated_response+'.'+'\nFor each move you get a penalty of -1.'
						reward_message = "For each move you get a penalty of -1."
						current_configuration[char_int_mapping[source_list]].pop()
						current_configuration[char_int_mapping[target_list]].append(no_to_move)

			if response_flag==1:
				total_reward+=-10

			next_state_prediction,num_input_tokens,num_output_tokens = state_predictor_module(first_temp_current_configuration[0], first_temp_current_configuration[1], first_temp_current_configuration[2] ,gpt_truncated_response,num_input_tokens,num_output_tokens)
				

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
			Move <N> from <src> to <trg>.

			""".format("A = "+str(next_state_prediction[0]),"B = "+str(next_state_prediction[1]),"C = "+str(next_state_prediction[2]),number_target_mapping[num_disks])

			


			

			prompt+="\n"+gpt_truncated_response+ "." +"\n"+internal_configuration_msg

			external_environment_prompt+="\n"+user_message +"\n"+configuration_msg


			print("feedback>>",reward_message+"\n"+configuration_msg)

			print("state predicitor configurations>>",internal_configuration_msg)
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

