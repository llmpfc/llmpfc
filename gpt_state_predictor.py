import openai
from gen_start_config import *
import time
from copy import deepcopy
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"
openai.api_key = "60be7ed5e0ca4e3c983ab7e70929f704"
all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
char_int_mapping = {'A':0,'B':1,'C':2}
for i in range(len(all_As)):
# for i in range(2):

	A=all_As[i] 

	B=all_Bs[i]

	C=all_Cs[i]
	num_disks = max(A+B+C)+1

	move_messages = []
	move_messages_labels = []
	for j in range(num_disks):
		if j in A:
			max_B = max(B) if len(B) else -1
			max_C = max(C) if len(C) else -1

			move_messages.append("Move {} from list A to list B.".format(j))
			if j==A[-1] and j>max_B:
				move_messages_labels.append("valid")
			else:
				move_messages_labels.append("invalid")
			move_messages.append("Move {} from list A to list C.".format(j))
			if j==A[-1] and j>max_C:
				move_messages_labels.append("valid")
			else:
				move_messages_labels.append("invalid")
		elif j in B:
			max_A = max(A) if len(A) else -1
			max_C = max(C) if len(C) else -1
			move_messages.append("Move {} from list B to list A.".format(j))
			if j==B[-1] and j>max_A:
				move_messages_labels.append("valid")
			else:
				move_messages_labels.append("invalid")

			move_messages.append("Move {} from list B to list C.".format(j))
			if j==B[-1] and j>max_C:
				move_messages_labels.append("valid")
			else:
				move_messages_labels.append("invalid")
		else:
			max_A = max(A) if len(A) else -1
			max_B = max(B) if len(B) else -1

			move_messages.append("Move {} from list C to list A.".format(j))
			if j==C[-1] and j>max_A:
				move_messages_labels.append("valid")
			else:
				move_messages_labels.append("invalid")
			move_messages.append("Move {} from list C to list B.".format(j))
			if j==C[-1] and j>max_B:
				move_messages_labels.append("valid")
			else:
				move_messages_labels.append("invalid")
		
		


	for idx,msg in enumerate(move_messages):
		if move_messages_labels[idx] == 'valid':



			prompt = """Consider the following puzzle problem:

			Here are two examples:
			Example 1:

			Problem description:
			- There are three lists labeled A, B, and C.
			- There are three numbers -- 0, 1, and 2 -- distributed among those three lists.
			- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
			Rule #1: You can only move a number if it is at the rightmost end of its current list.
			Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
			

			Goal: The goal is to predict the configuration of the three lists, if the proposed move is applied to the current configuration.

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

			Problem description:
			- There are three lists labeled A, B, and C.
			- There are three numbers -- 0, 1, and 2 -- distributed among those three lists.
			- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
			Rule #1: You can only move a number if it is at the rightmost end of its current list.
			Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
			
			
			Goal: The goal is to predict the configuration of the three lists, if the proposed move is applied to the current configuration.

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

			Problem description:
			- There are three lists labeled A, B, and C.
			- There are {} distributed among those three lists.
			- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
			Rule #1: You can only move a number if it is at the rightmost end of its current list.
			Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
			
			
			Goal: The goal is to predict the configuration of the three lists, if the proposed move is applied to the current configuration.

			This is the current configuration:
			{}
			{}
			{}
			Proposed move:
			{}

			Answer:

			""".format(number_message_mapping[num_disks],"A = "+str(A),"B = "+str(B),"C = "+str(C),msg)

			with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 state predictor two shot/problem{}_move{}.log'.format(i+1,idx+1), 'a') as w:
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
					        max_tokens=200)

					break

				except Exception as e:
					err = f"Error: {str(e)}"
					print(err)
					time.sleep(60)
					cur_try+=1
					continue



			with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 state predictor two shot/problem{}_move{}.log'.format(i+1,idx+1), 'a') as w:
				w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)


			no_to_move = int(msg.split(" ")[1])
			source_list = msg.split(" ")[4]
			target_list = msg.split(" ")[7][0]
			current_configuration = deepcopy([A,B,C])

			current_configuration[char_int_mapping[source_list]].pop()
			current_configuration[char_int_mapping[target_list]].append(no_to_move)
			
			with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 state predictor two shot/problem{}_move{}.log'.format(i+1,idx+1), 'a') as w:
				w.write("\nCorrect response>>>>>>>\n"+"A = "+str(current_configuration[0])+"\nB = "+str(current_configuration[1])+"\nC = "+str(current_configuration[2]))
		
	print("done solving problem {}".format(i+1))

