import openai
from gen_start_config import *
import time
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"
openai.api_key = "60be7ed5e0ca4e3c983ab7e70929f704"
all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}

for i in range(106):
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


		prompt = """Consider the following puzzle problem:

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
		{}

		Answer:

		""".format("A = "+str(A),"B = "+str(B),"C = "+str(C),msg)

		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 move validity detector more detailed instructions eight shot with 4 numbers examples/problem{}_move{}.log'.format(i+1,idx+1), 'a') as w:
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



		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 move validity detector more detailed instructions eight shot with 4 numbers examples/problem{}_move{}.log'.format(i+1,idx+1), 'a') as w:
			w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)
		
		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 move validity detector more detailed instructions eight shot with 4 numbers examples/problem{}_move{}.log'.format(i+1,idx+1), 'a') as w:
			w.write("\nCorrect response>>>>>>>\n"+move_messages_labels[idx])
		
	print("done solving problem {}".format(i+1))

