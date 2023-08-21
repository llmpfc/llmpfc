import openai
from copy import deepcopy
import time
import re
import json
import os
import argparse
import numpy as np
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"

def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)


def move_validator_module(source_room, target_room,num_input_tokens,num_output_tokens):

	move_validator_prompt = """
		Consider the following puzzle problem:

		Problem description:
		- Imagine a castle with 15 rooms. 
		- Room 1 is connected to room 7, room 10, room 13, and room 11. 
		- Room 2 is connected to room 5, room 8, room 11, and room 14. 
		- Room 3 is connected to room 6, room 9, room 12, and room 8. 
		- Room 4 is connected to room 7, room 10, room 13, and room 15. 
		- Room 5 is connected to room 8, room 11, and room 14. 
		- Room 6 is connected to room 9, room 12, and room 15. 
		- Room 7 is connected to room 10, and room 13. 
		- Room 8 is connected to room 14. 
		- Room 9 is connected to room 12, and room 15. 
		- Room 10 is connected to room 13. 
		- Room 11 is connected to room 14. 
		- Room 12 is connected to room 15. 
		- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
		- You can collect the reward only once and only from one chest. 

		Goal: The goal is to check whether the proposed step between the two rooms exists or not, and based on that if it is a valid or invalid step.

		Here are two examples:

		Example 1:

		Proposed step: 
		Go from room 1 to room 11. 

		Answer:
		First check the rooms, room 1 is connected to. Room 1 is connected to room 7, room 10, room 13, and room 11.
		Next check the rooms, room 11 is connected to. Room 11 is connected to room 1, room 2, room 5, and room 14.
		Since room 1 and room 11 are connected to each other, the proposed step exists and is valid.

		Example 2:

		Proposed step: 
		Go from room 4 to room 5.

		Answer:
		First check the rooms, room 4 is connected to. Room 4 is connected to room 7, room 10, room 13, and room 15.
		Next check the rooms, room 5 is connected to. Room 5 is connected to room 8, room 11, room 14, and room 2.
		Since room 4 and room 5 aren't connected to each other, the proposed step doesn't exist and is invalid.

		Here is the task:

		Proposed step:
		Go from room {} to room {}.

		Answer:


		""".format(source_room,target_room)


	move_validator_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	move_validator_input.append({
		"role": "user",
		"content": move_validator_prompt,
	})

	cur_try=0
	while cur_try<5:

		try:

			validator_response = openai.ChatCompletion.create(
				engine='gpt-4-32k',
				messages=move_validator_input,temperature=0.0,top_p=0,
					max_tokens=500)

			num_input_tokens+= validator_response["usage"]["prompt_tokens"]
			num_output_tokens+= validator_response["usage"]["completion_tokens"]

			print("validator response>>",validator_response.choices[0].message.content)
			char_list_response = validator_response.choices[0].message.content.split('\n')[-1].replace(".","").split(" ")
			if 'invalid' in char_list_response:
				move_validity = 'no'
			else:
				move_validity = 'yes'

			print("move_validity>>",move_validity)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(60)
			cur_try+=1
			continue
	return move_validity,validator_response.choices[0].message.content,num_input_tokens,num_output_tokens



parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--openai_api_key', type = str, help='openai key', required= True)
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)

args = parser.parse_args()
print(args)

openai.api_key = args.openai_api_key

graph_info_lists = [(1,7), (1,10),(1,13),(1,11), 
(2,5), (2,8),(2,11),(2,14) ,
(3,6), (3,9),(3,12),(3,8), 
(4,7), (4,10),(4,13),(4,15), 
(5,8), (5,11),(5,14), 
(6,9), (6,12),(6,15), 
(7,10), (7,13),  
(8,14), (9,12), (9,15),
			  (10,13), (11,14),(12,15)]

A=np.zeros((15,15))

for node_tup in graph_info_lists:
	
		
			
	A[node_tup[0]-1,node_tup[1]-1] = 1
	A[node_tup[1]-1,node_tup[0]-1] = 1


num_input_tokens =0
num_output_tokens =0
for start_room in range(1,16):
	if start_room!=8 and start_room!=15:


		prompt = """
		Consider the following puzzle problem:
		
		Problem description:
		- Imagine a castle with 15 rooms. 
		- Room 1 is connected to room 7, room 10, room 13, and room 11. 
		- Room 2 is connected to room 5, room 8, room 11, and room 14. 
		- Room 3 is connected to room 6, room 9, room 12, and room 8. 
		- Room 4 is connected to room 7, room 10, room 13, and room 15. 
		- Room 5 is connected to room 8, room 11, and room 14. 
		- Room 6 is connected to room 9, room 12, and room 15. 
		- Room 7 is connected to room 10, and room 13. 
		- Room 8 is connected to room 14. 
		- Room 9 is connected to room 12, and room 15. 
		- Room 10 is connected to room 13. 
		- Room 11 is connected to room 14. 
		- Room 12 is connected to room 15. 
		- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
		- You can collect the reward only once and only from one chest. 

		Goal: The goal is to find the shortest path from the starting room that yields the most reward.

		This is the starting room:
		room {}

		Starting from room {}, please list the room numbers in order, including {}, separated by commas. Please limit your answer to a maximum path length of 6.
		 
		Your answer should only be in the format as below:
		The shortest path from room {} that yields the most reward is: {}, 

		

		""".format(start_room,start_room,start_room,start_room,start_room)

		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": prompt,
		})

		test_dir = './logs/'
		check_path(test_dir)
		output_dir = test_dir + args.output_dir + '/'
		check_path(output_dir)


		with open(output_dir+'problem{}.log'.format(start_room), 'a') as w:
			w.write(prompt +'\n')

	

		
		num_tries = 0 
		while num_tries<5:

			cur_try=0
			
			while cur_try <10:
				try:
					



					response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=input,temperature=0.0,top_p=0,
						max_tokens=1000)

					print("GPT-4 full response>>>",response.choices[0].message.content)

					num_input_tokens+= response["usage"]["prompt_tokens"]
					num_output_tokens+= response["usage"]["completion_tokens"]

					index = 0 
					for m in range(len(response.choices[0].message.content) - 30):
						sub_str = response.choices[0].message.content[m:m+31]
						if 'that yields the most reward is:' in sub_str: #if 'correct' in sub_str and 'sequence' in sub_str:
							

							index = m 



					
					rooms_splits = response.choices[0].message.content[index:].split(":")[1].strip().split(",")

					print("rooms extracted>>",rooms_splits)

					break

						
				except Exception as e:
					
					err = f"Error: {str(e)}"

					

					print(err)
					
					time.sleep(60)
					cur_try+=1
					continue

			concatenated_invalid_moves_validator_responses = ""

			for k in range(len(rooms_splits)-1):

				move_validity,validity_response, num_input_tokens, num_output_tokens = move_validator_module(int(rooms_splits[k]),int(rooms_splits[k+1]),num_input_tokens,num_output_tokens)
				if move_validity == 'no':
					concatenated_invalid_moves_validator_responses+=validity_response+"\n\n"

			print("all invalid move responses>>>",concatenated_invalid_moves_validator_responses)

			if len(concatenated_invalid_moves_validator_responses)==0:
				break
			else:

				internal_configuration_msg = """This is the starting room:
				room {}
			
				Please try again. Starting from room {}, please list the room numbers in order, including {}, separated by commas. Please limit your answer to a maximum path length of 6.
		 
				Your answer should only be in the format as below:
				The shortest path from room {} that yields the most reward is: {}, 
				

				""".format(start_room,start_room,start_room,start_room,start_room)

				



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



			
		
		with open(output_dir+'problem{}.log'.format(start_room), 'a') as w:
			w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)


		print("number of input and output tokens till now>>", num_input_tokens,num_output_tokens)
	
		print("done solving problem {}".format(start_room))
				





