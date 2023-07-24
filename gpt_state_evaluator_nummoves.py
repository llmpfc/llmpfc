# start with problem 1 and problem 5 as incontext examples
import openai
from gen_start_config import *
import time
import numpy as np
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"
openai.api_key = "60be7ed5e0ca4e3c983ab7e70929f704"
all_As, all_Bs, all_Cs = generate_all_start_config()

incontext_example_numbers = [1,5,7,10,14,17,19,20,23,25]
# incontext_example_numbers = [1,5]

optimal_steps_3_4_numbers_problemwise = np.load('optimal_steps_3_4_numbers_problemwise.npy')
number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}

for i in range(106):
	if i+1 not in incontext_example_numbers:

		A=all_As[i] 

		B=all_Bs[i]

		C=all_Cs[i]
		num_disks = max(A+B+C)+1

		# prompt = """Consider the following puzzle problem:

		# Problem description:
		# - There are three lists labeled A, B, and C.
		# - There is a set of numbers distributed among those three lists.
		# - You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		# Rule #1: You can only move a number if it is at the rightmost end of its current list.
		# Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		# A move is valid if it satisfies both Rule #1 and Rule #2.
		# A move is invalid if it violates either Rule #1 or Rule #2
		
		# Goal: The goal is to predict the minimum number of valid moves required to reach the goal configuration from the current configuration.
		

		# Here are two examples:
		
		# Example 1:
		
		# This is the current configuration:
		# A = [0, 1, 2]
		# B = []
		# C = []
		
		# This is the goal configuration:
		# A = []
		# B = []
		# C = [0, 1, 2]
		
		# Answer:
		# The minimum number of valid moves required to reach the goal configuration from the current configuration is 7.
		
		
		# Example 2:
		
		# This is the current configuration:
		# A = [1, 2]
		# B = [0]
		# C = []

		# This is the goal configuration:
		# A = []
		# B = []
		# C = [0, 1, 2]

		# Answer:
		# The minimum number of valid moves required to reach the goal configuration from the current configuration is 4.
		

		
		# Here is the task:
		
		# This is the current configurations:
		# {}
		# {}
		# {}
		
		# This is the goal configuration:
		# A = []
		# B = []
		# {}
		
		# Answer:

		# """.format("A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])

				

		


		prompt = """Consider the following puzzle problem:

		Problem description:
		- There are three lists labeled A, B, and C.
		- There is a set of numbers distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2
		
		Goal: The goal is to predict the minimum number of valid moves required to reach the goal configuration from the current configuration.
		

		Here are ten examples:
		
		Example 1:
		
		This is the current configuration:
		A = [0, 1, 2]
		B = []
		C = []
		
		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]
		
		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 7.
		
		
		Example 2:
		
		This is the current configuration:
		A = [1, 2]
		B = [0]
		C = []

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 4.

		
		Example 3:
		
		This is the current configuration:
		A = [2]
		B = []
		C = [0, 1]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 1.

		
		Example 4:
		
		This is the current configuration:
		A = [1]
		B = []
		C = [0, 2]
		
		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 3.


		Example 5:
		
		This is the current configuration:
		A = []
		B = [1, 2]
		C = [0]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 3.


		Example 6:
		
		This is the current configuration:
		A = []
		B = [1]
		C = [0, 2]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 3.


		Example 7:
		
		This is the current configuration:
		A = [0, 2]
		B = [1]
		C = []

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 5.


		Example 8:
		
		This is the current configuration:
		A = []
		B = [0, 2]
		C = [1]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 6.


		Example 9:
		
		This is the current configuration:
		A = [0]
		B = [2]
		C = [1]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 7.


		Example 10:
		
		This is the current configuration:
		A = [2]
		B = [0]
		C = [1]

		This is the goal configuration:
		A = []
		B = []
		C = [0, 1, 2]

		Answer:
		The minimum number of valid moves required to reach the goal configuration from the current configuration is 7.
		
		Here is the task:
		
		This is the current configurations:
		{}
		{}
		{}
		
		This is the goal configuration:
		A = []
		B = []
		{}
		
		Answer:

		""".format("A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])









		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 nummoves evaluator prob 1,5,7,10,14,17,19,20,23,25 incontext examples/problem{}.log'.format(i+1), 'a') as w:
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



		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 nummoves evaluator prob 1,5,7,10,14,17,19,20,23,25 incontext examples/problem{}.log'.format(i+1), 'a') as w:
			w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)
		
		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 nummoves evaluator prob 1,5,7,10,14,17,19,20,23,25 incontext examples/problem{}.log'.format(i+1), 'a') as w:
			w.write("\nCorrect response>>>>>>>\n"+"The minimum number of valid moves required to reach the goal configuration from the current configuration is {}.".format(optimal_steps_3_4_numbers_problemwise[i]))
		
	print("done solving problem {}".format(i+1))

