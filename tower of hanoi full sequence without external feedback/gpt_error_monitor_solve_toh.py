import openai
from gen_start_config import *
import time
import json
import os
import argparse
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"

all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}


def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)



def move_validator_module(state_A, state_B, state_C, move_number,source_list,target_list,num_input_tokens,num_output_tokens):

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


		Here are two examples:
		
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


		Here is the task:

		This is the initial configuration:
		{}
		{}
		{}
		Proposed move:
		Move {} from list {} to list {}.

		Answer:

		""".format("A = "+str(state_A),"B = "+str(state_B),"C = "+str(state_C),move_number,source_list,target_list)


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


def extract_moves_configurations(start_config, gpt_full_response):

	moves_decoded_tuples = []
	all_configuration_after_moves = []
	all_configuration_after_moves.append(start_config)
	lines = gpt_full_response.split("\n")
	for l in range(len(lines)):


		if 'Move' in lines[l] and 'from list' in lines[l] and 'to list' in lines[l] and (('A' in lines[l] and 'B' in lines[l] ) or ('C' in lines[l] and 'B' in lines[l] ) or ('A' in lines[l] and 'C' in lines[l] )):
		



			move_line = lines[l].split('.')[1].replace('.','').strip() # for random valid only


			moves_decoded_tuples.append((int(move_line.split(" ")[1]),move_line.split(" ")[4],move_line.split(" ")[7]))
			count = l
			
			while ("A =" not in lines[count]):
				count+=1
				
			state_output = []
			
			state_output.append(json.loads(lines[count].split("=")[-1]))
			state_output.append(json.loads(lines[count+1].split("=")[-1]))
			state_output.append(json.loads(lines[count+2].split("=")[-1]))
			
			all_configuration_after_moves.append(state_output)

	return moves_decoded_tuples,all_configuration_after_moves


parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--openai_api_key', type = str, help='openai key', required= True)
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)

args = parser.parse_args()
print(args)

openai.api_key = args.openai_api_key

num_input_tokens =0
num_output_tokens=0
for i in range(26):
	A=all_As[i] 

	B=all_Bs[i]

	C=all_Cs[i]
	start_configuration = [A,B,C]
	num_disks = max(A+B+C)+1
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
	
	Give me the sequence of moves to solve the puzzle from the starting configuration, updating the lists after each move. Please try to use as few moves as possible, and make sure to follow the rules listed above. Please limit your answer to a maximum of 10 steps.
	Your answer should only be in the format as below:
	Step 1. Move <N> from list <src> to list <tgt>.
	A = []
	B = []
	C = []

	""".format("A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])

	
	test_dir = './logs/'
	check_path(test_dir)
	output_dir = test_dir + args.output_dir + '/'
	check_path(output_dir)


	
	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write(prompt +'\n')

	



	input = [{
		"role": "system",
		"content": "you are an AI assistant",
	}]

	input.append({
		"role": "user",
		"content": prompt,
	})

	num_tries=0
	while num_tries<5:


		another_cur_try = 0
		while another_cur_try <5:
			try:
				response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=input,temperature=0.0,top_p = 0,
						max_tokens=2000)

				num_input_tokens+= response["usage"]["prompt_tokens"]
				num_output_tokens+= response["usage"]["completion_tokens"]

				print("GPT-4 full response>>>",response.choices[0].message.content)
				index = 0 
				for m in range(len(response.choices[0].message.content) - 24):
					sub_str = response.choices[0].message.content[m:m+25]
					if 'is' in sub_str and 'the' in sub_str and 'solution' in sub_str: #if 'correct' in sub_str and 'sequence' in sub_str:
						

						index = m 



				extracted_moves,extracted_configs = extract_moves_configurations(start_configuration,response.choices[0].message.content[index:])

				print("extracted gpt moves>>>",extracted_moves)
				print("extracted gpt configs>>>",extracted_configs)




				
			


				break

			except Exception as e:
				err = f"Error: {str(e)}"
				print(err)
				time.sleep(60)
				another_cur_try+=1
				
				continue

		concatenated_invalid_moves_validator_responses = ""

		for k in range(len(extracted_moves)):

			move_validity,validity_response, num_input_tokens, num_output_tokens = move_validator_module(extracted_configs[k][0],extracted_configs[k][1],extracted_configs[k][2],extracted_moves[k][0],extracted_moves[k][1],extracted_moves[k][2],num_input_tokens,num_output_tokens)
			if move_validity == 'no':
				concatenated_invalid_moves_validator_responses+=validity_response+"\n\n"

		print("all invalid move responses>>>",concatenated_invalid_moves_validator_responses)

		if len(concatenated_invalid_moves_validator_responses)==0:
			break
		else:

			internal_configuration_msg = """This is the starting configuration:
			{}
			{}
			{}

			This is the goal configuration:
			A = []
			B = []
			{}

			Please try again to give me the sequence of moves to solve the puzzle from the starting configuration, updating the lists after each move. Please try to use as few moves as possible, and make sure to follow the rules listed above. Please limit your answer to a maximum of 10 steps.
			Your answer should only be in the format as below:
			Step 1. Move <N> from list <src> to list <tgt>.
			A = []
			B = []
			C = []


			""".format("A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])

			



			prompt+="\n\n"+response.choices[0].message.content+"\n\n"+concatenated_invalid_moves_validator_responses+"\n\n"+internal_configuration_msg

			print("updated prompt>>>",prompt)

			input = [{
			"role": "system",
			"content": "you are an AI assistant",
			}]

			input.append({
				"role": "user",
				"content": prompt,
			})

			num_tries+=1






	


	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)
	

	print("number of input and output tokens till now>>", num_input_tokens,num_output_tokens)
	print("done solving problem {}".format(i+1))

