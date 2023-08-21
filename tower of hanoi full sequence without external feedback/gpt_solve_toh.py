import openai
from gen_start_config import *
import time
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


parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--openai_api_key', type = str, help='openai key', required= True)
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)

args = parser.parse_args()
print(args)

openai.api_key = args.openai_api_key

for i in range(26):
	A=all_As[i] 

	B=all_Bs[i]

	C=all_Cs[i]
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
	Please format your answer as below:
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

	another_cur_try = 0
	while another_cur_try <5:
		try:
			response = openai.ChatCompletion.create(
				engine='gpt-4-32k',
				messages=input,temperature=0.0,top_p = 0,
					max_tokens=2000)

			num_input_tokens= response["usage"]["prompt_tokens"]
			num_output_tokens= response["usage"]["completion_tokens"]

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(60)
			another_cur_try+=1
			
			continue

	


	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)
	
	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write("\n\n Number of input tokens = {} \n Number of output tokens = {}".format(num_input_tokens,num_output_tokens))
	
	print("done solving problem {}".format(i+1))

