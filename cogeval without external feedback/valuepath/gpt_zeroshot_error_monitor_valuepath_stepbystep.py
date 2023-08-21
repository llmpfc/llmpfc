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






def move_validator_module(source_room, target_room):

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

			print("validator response>>>", validator_response)
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
	return move_validity,validator_response


def actor_module_propose_action(actor_input,current_room):

	num_tries=0
	while num_tries<10:

		cur_try=0
		check_flag =0
		while cur_try <10:
			try:
				if check_flag==1:
					actor_response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=actor_input,temperature=0.1*cur_try,
						max_tokens=200)
				else:



					actor_response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=actor_input,temperature=0.0,top_p=0,
						max_tokens=200)

				print("GPT-4 full response>>>",actor_response.choices[0].message.content)
				actor_truncated_response = None

				for k in range(len(actor_response.choices[0].message.content) - 11):
					sub_str = actor_response.choices[0].message.content[k:k+12]
					if 'Go from room' in sub_str:
						break

				for t in range(k, len(actor_response.choices[0].message.content)):
					if actor_response.choices[0].message.content[t] == '.':
						break
				actor_truncated_response = actor_response.choices[0].message.content[k:t]


				

				if 'Go from room' in actor_truncated_response and 'to room' in actor_truncated_response and len(actor_truncated_response.split(" ")) ==7:
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

		print("GPT-4 truncated response>>",actor_truncated_response)
		source_room = int(actor_truncated_response.split(" ")[3])
		target_room = int(actor_truncated_response.split(" ")[6])
		
		move_validity, move_validator_response = move_validator_module(source_room,target_room)

		if move_validity == "yes":
			break
		else:

			actor_input.append({
				"role": "assistant",
				"content": actor_response.choices[0].message.content,
			})

			internal_configuration_msg = """
			{}

			This is the current room:
			room {}
				
			
			Please try again to give me the next room to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
			Go from room <N> to room <N>.

			""".format(move_validator_response,current_room)


			actor_input.append({
			"role": "user",
			"content": internal_configuration_msg,
		})
			
			num_tries+=1



	return actor_truncated_response



	
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



for start_room in range(1,16):
	if start_room!=8 and start_room!=15:
		rooms_visited = []
		rooms_visited.append(start_room)


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

		Give me the next room to go to from the starting room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
		Go from room <N> to room <N>.

		""".format(start_room)

		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": prompt,
		})

		current_room = start_room
		reward_rooms = [8,15]
		reward_values = [50,10]
		flag=0
		total_reward = 0
		for step in range(20):
			


			truncated_response = actor_module_propose_action(input,current_room)
			source_room = int(truncated_response.split(" ")[3])
			target_room = int(truncated_response.split(" ")[6])
			rooms_visited.append(target_room)
			current_room = target_room

			

			configuration_msg = """This is the current room:
				room {}
				
			
				Give me the next room to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
				Go from room <N> to room <N>.

				""".format(current_room)

			prompt+="\n"+truncated_response+"."+"\n"+configuration_msg

			

			input = [{
					"role": "system",
					"content": "you are an AI assistant",
				}]

			input.append({
				"role": "user",
				"content": prompt,
				})
			if current_room in reward_rooms:
				flag=1

				test_dir = './logs/'
				check_path(test_dir)
				output_dir = test_dir + args.output_dir + '/'
				check_path(output_dir)

			
				
				with open(output_dir+'problem{}.log'.format(start_room), 'a') as w:
					w.write(prompt +'\n'+"List of rooms visited = {}".format(rooms_visited))

				
				

				break

		if flag==0:

			test_dir = './logs/'
			check_path(test_dir)
			output_dir = test_dir + args.output_dir + '/'
			check_path(output_dir)

		
			
			with open(output_dir+'problem{}.log'.format(start_room), 'a') as w:
				w.write(prompt +'\n'+"List of rooms visited = {}".format(rooms_visited))

		

		print("done solving problem {}".format(start_room))
				





