import openai
from copy import deepcopy
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


for source_room in range(1,16):
	for target_room in range(1,16):
		if source_room!=target_room:
			if A[source_room-1,target_room-1]==1:
				target = 'valid'
			else:
				target = 'invalid'



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


			input = [{
		    "role": "system",
		    "content": "you are an AI assistant",
			}]

			input.append({
			    "role": "user",
			    "content": prompt,
			})

			with open('/jukebox/griffiths/people/smondal/cogeval/logs/gpt4 valuepath move validity detector two shot/problem_move_{}_{}.log'.format(source_room,target_room), 'a') as w:
				w.write(prompt +'\n')

			cur_try=0
			while cur_try<5:

				try:

					response = openai.ChatCompletion.create(
					    engine='gpt-4-32k',
					    messages=input,temperature=0.0,top_p=0,
					        max_tokens=500)

					break

				except Exception as e:
					err = f"Error: {str(e)}"
					print(err)
					time.sleep(60)
					cur_try+=1
					continue



			with open('/jukebox/griffiths/people/smondal/cogeval/logs/gpt4 valuepath move validity detector two shot/problem_move_{}_{}.log'.format(source_room,target_room), 'a') as w:
				w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)
		
			with open('/jukebox/griffiths/people/smondal/cogeval/logs/gpt4 valuepath move validity detector two shot/problem_move_{}_{}.log'.format(source_room,target_room), 'a') as w:
				w.write("\nCorrect response>>>>>>>\n"+target)
		
			print("done solving problem move from room {} to room {}".format(source_room,target_room))


