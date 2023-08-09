import openai
from copy import deepcopy
from steppath_fewshot_examples import standard_prompt
import time
import re
import json
import numpy as np
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"
openai.api_key = "60be7ed5e0ca4e3c983ab7e70929f704"

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

step2_paths = [(9,4),(6,4),(12,4),(3,2),(8,11),(2,1),(11,10),(1,4),(13,15),(7,15)] 
step3_paths = [(9,13),(6,13),(12,13),(3,11),(8,1),(14,10),(2,10),(5,10),(5,13),(14,13)]
step4_paths = [(9,1),(9,11),(12,1),(6,1),(6,11),(12,11),(3,13),(8,13),(2,4),(3,7)]

icl_examples = [(9,4),(2,10),(7,3)]

all_step_paths = step2_paths + step3_paths + step4_paths

for start_target_tup in all_step_paths:
	if start_target_tup in step2_paths:
		optimal_num_steps = 2
		optimal_reward = 8
	elif start_target_tup in step3_paths:
		optimal_num_steps = 3
		optimal_reward = 7
	else:

		optimal_num_steps = 4
		optimal_reward = 6

	for count in range(2):
		if count==0:
			start_room = start_target_tup[0]
			final_target_room = start_target_tup[1]
		else:
			start_room = start_target_tup[1]
			final_target_room = start_target_tup[0]


		if (start_room,final_target_room) not in icl_examples:









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
			- Room 9 is connected to room 12 and room 15. 
			- Room 10 is connected to room 13. 
			- Room 11 is connected to room 14. 
			- Room 12 is connected to room 15. 
			 

			Goal: The goal is to find the shortest path from the starting room to the target room.

			Here are three examples:
			{}

			Here is the task:

			This is the starting room:
			room {}

			This is the target room:
			room {}

			Give me the next room to go to from the starting room that can help in reaching the target room using as few steps as possible. Please format your answer as:
			Go from room <N> to room <N>.

			""".format(standard_prompt, start_room,final_target_room)

			input = [{
			    "role": "system",
			    "content": "you are an AI assistant",
			}]

			input.append({
			    "role": "user",
			    "content": prompt,
			})

			current_room = start_room
			# reward_rooms = [8,15]
			# reward_values = [50,10]
			flag=0
			total_reward = 0
			for step in range(20):
				cur_try=0
				check_flag =0
				while cur_try <10:
					try:
						if check_flag==1:
							response = openai.ChatCompletion.create(
						    engine='gpt-4-32k',
						    messages=input,temperature=0.1*cur_try,
						        max_tokens=200)
						else:



							response = openai.ChatCompletion.create(
						    engine='gpt-4-32k',
						    messages=input,temperature=0.0,top_p=0,
						        max_tokens=200)

						print("GPT-4 full response>>>",response.choices[0].message.content)
						truncated_response = None

						for k in range(len(response.choices[0].message.content) - 11):
						    sub_str = response.choices[0].message.content[k:k+12]
						    if 'Go from room' in sub_str:
						        break

						for t in range(k, len(response.choices[0].message.content)):
						    if response.choices[0].message.content[t] == '.':
						        break
						truncated_response = response.choices[0].message.content[k:t]


						

						if 'Go from room' in truncated_response and 'to room' in truncated_response and len(truncated_response.split(" ")) ==7:
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


				print("GPT-4 truncated response>>",truncated_response)
				source_room = int(truncated_response.split(" ")[3])
				target_room = int(truncated_response.split(" ")[6])

				total_reward+=-1
				error_flag =0
				if source_room!=current_room:
					user_message = truncated_response+"." + "\nInvalid move because current room is not {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(source_room)
					reward_message = "Invalid move because current room is not {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(source_room)
					error_flag =1
				elif A[source_room-1,target_room-1]!=1:
						
					user_message = truncated_response + "." + "\nInvalid move because room {} is not connected to room {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(source_room,target_room)
					reward_message = "Invalid move because room {} is not connected to room {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(source_room,target_room)
					error_flag =1
						
				else:

					user_message = truncated_response+'.'+'\nFor each move you get a penalty of -1.'
					reward_message = "For each move you get a penalty of -1."
					current_room = target_room
				

				if error_flag==1:
					total_reward+=-10

				configuration_msg = """This is the current room:
					room {}

					This is the target room:
					room {}

				
					Give me the next room to go to from the current room that can help in reaching the target room using as few steps as possible. Please format your answer as:
					Go from room <N> to room <N>.

					""".format(current_room,final_target_room)

				prompt+="\n"+user_message+"\n"+configuration_msg

				print("external feedback>>",reward_message+"\n"+configuration_msg)

				input = [{
						"role": "system",
						"content": "you are an AI assistant",
					}]

				input.append({
					"role": "user",
					"content": prompt,
					})
				if current_room == final_target_room:
					flag=1
					total_reward+=10
					with open('/jukebox/griffiths/people/smondal/cogeval/logs/gpt4 standard icl steppath step by step external feedback/problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
						w.write(prompt +'\n'+"Solved problem in {} steps. Total reward = {}".format(step+1,total_reward))

					break

			if flag==0:
				with open('/jukebox/griffiths/people/smondal/cogeval/logs/gpt4 standard icl steppath step by step external feedback/problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
					w.write(prompt +'\n'+"Timed out. Couldn't solve problem in 20 steps. Total reward = {}".format(total_reward))

			print("done solving problem {} to {}".format(start_room,final_target_room))
				





