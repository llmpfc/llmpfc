import openai
from gen_start_config import *
import time
import numpy as np
import os
def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)


openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"
openai.api_key = "60be7ed5e0ca4e3c983ab7e70929f704"
all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
all_move_messages = []
all_move_messages_labels = []
start_configs = []
for i in range(106):
	A=all_As[i] 

	B=all_Bs[i]

	C=all_Cs[i]
	num_disks = max(A+B+C)+1

	
	for j in range(num_disks):
		if j in A:
			max_B = max(B) if len(B) else -1
			max_C = max(C) if len(C) else -1

			all_move_messages.append("Move {} from list A to list B.".format(j))
			start_configs.append([A,B,C])
			if j==A[-1] and j>max_B:
				all_move_messages_labels.append("valid")
			else:
				all_move_messages_labels.append("invalid")
			all_move_messages.append("Move {} from list A to list C.".format(j))
			start_configs.append([A,B,C])
			if j==A[-1] and j>max_C:
				all_move_messages_labels.append("valid")
			else:
				all_move_messages_labels.append("invalid")
		elif j in B:
			max_A = max(A) if len(A) else -1
			max_C = max(C) if len(C) else -1
			all_move_messages.append("Move {} from list B to list A.".format(j))
			start_configs.append([A,B,C])
			if j==B[-1] and j>max_A:
				all_move_messages_labels.append("valid")
			else:
				all_move_messages_labels.append("invalid")

			all_move_messages.append("Move {} from list B to list C.".format(j))
			start_configs.append([A,B,C])
			if j==B[-1] and j>max_C:
				all_move_messages_labels.append("valid")
			else:
				all_move_messages_labels.append("invalid")
		else:
			max_A = max(A) if len(A) else -1
			max_B = max(B) if len(B) else -1

			all_move_messages.append("Move {} from list C to list A.".format(j))
			start_configs.append([A,B,C])
			if j==C[-1] and j>max_A:
				all_move_messages_labels.append("valid")
			else:
				all_move_messages_labels.append("invalid")
			all_move_messages.append("Move {} from list C to list B.".format(j))
			start_configs.append([A,B,C])
			if j==C[-1] and j>max_B:
				all_move_messages_labels.append("valid")
			else:
				all_move_messages_labels.append("invalid")

num_examples = 12
print(len(start_configs),len(all_move_messages),len(all_move_messages_labels))		
icl_ex_ids = np.random.choice(np.arange(len(start_configs)),num_examples)	

print("ICL example ids>>",icl_ex_ids)

exs ="""
"""

for ex_id in range(num_examples):

    
    exs+="Example {}:".format(ex_id+1)
    exs+="\n\n"
    exs+="This is the initial configuration:\n"
    exs+="{}".format("A = "+str(start_configs[icl_ex_ids[ex_id]][0]))
    exs+="\n"
    exs+="{}".format("B = "+str(start_configs[icl_ex_ids[ex_id]][1]))
    exs+="\n"
    exs+="{}".format("C = "+str(start_configs[icl_ex_ids[ex_id]][2]))
    exs+="\n\n"
    exs+="Proposed move:\n"
    exs+="{}".format(all_move_messages[icl_ex_ids[ex_id]])
    exs+="\n\n"
    exs+="Answer:\n"
    exs+="{}".format(all_move_messages_labels[icl_ex_ids[ex_id]])
    exs+="\n\n\n"

print("Generated ICL examples", exs)

check_path('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 move validity detector randomly generated {} shot examples with binary answer'.format(num_examples))
		
for idx in range(len(start_configs)):
	if idx not in icl_ex_ids:



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

Goal: The goal is to check if the proposed move is a valid or invalid move.

Here are {} examples:

{}


Here is the task:

This is the initial configuration:
{}
{}
{}

Proposed move:
{}

Answer:

		""".format(num_examples,exs,"A = "+str(start_configs[idx][0]),"B = "+str(start_configs[idx][1]),"C = "+str(start_configs[idx][2]),all_move_messages[idx])


		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 move validity detector randomly generated {} shot examples with binary answer/problem{}.log'.format(num_examples,idx), 'a') as w:
			w.write(prompt +'\n')



		input = [{
		    "role": "system",
		    "content": "you are an AI assistant",
		}]

		input.append({
		    "role": "user",
		    "content": prompt,
		})

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



		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 move validity detector randomly generated {} shot examples with binary answer/problem{}.log'.format(num_examples,idx), 'a') as w:
			w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)
		
		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 move validity detector randomly generated {} shot examples with binary answer/problem{}.log'.format(num_examples,idx), 'a') as w:
			w.write("\nCorrect response>>>>>>>\n"+all_move_messages_labels[idx])
		
		print("done solving problem {}".format(idx))

