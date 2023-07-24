import openai
from gen_start_config import *
from copy import deepcopy
from reflexion_few_shot_examples import reflexion_prompt
import time
import re
import numpy as np
import os

openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"
openai.api_key = "f48b5a4f15dc4e58991738ab066ba465"
all_As, all_Bs, all_Cs = generate_all_start_config()
optimal_steps_3_4_numbers_problemwise = np.load('optimal_steps_3_4_numbers_problemwise.npy')
number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
char_int_mapping = {'A':0,'B':1,'C':2}

for trial_no in range(2,10):
	


	for i in range(106):
		A=all_As[i] 

		B=all_Bs[i]

		C=all_Cs[i]
		num_disks = max(A+B+C)+1
		
		start_configuration = [A,B,C]
		if num_disks ==3:

			target_configuration = [[],[],[0,1,2]]
		elif num_disks ==4:

			target_configuration = [[],[],[0,1,2,3]]
		else:


			target_configuration = [[],[],[0,1,2,3,4]]

		current_configuration = deepcopy(start_configuration)
		if trial_no==0:



			file_baseline = open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 zeroshot step by step external feedback/problem{}.log'.format(i+1), 'r')
			lines_baseline = file_baseline.read().splitlines()
			file_baseline.close()

			scenario = """
"""
			previous_memory = """
"""
			for l in lines_baseline:
			  
			    scenario+=l+'\n'

			
			query = """You will be given the history of a past experience in which you were placed in an environment and asked to give a sequence of moves to solve a problem. You were either unsuccessful in solving the problem or solved it using more number of moves than required. Do not summarize your environment, but rather think about the strategy you took to attempt to complete the task. Devise a concise, new plan of moves that accounts for your mistake with reference to specific moves that you should have taken. For example, if you tried X and Y but forgot Z, then devise a plan to achieve Z with environment-specific moves. You will need this later when you are solving the same task. Give your plan after "Plan". Here are three examples:

					{}

					Here is the scenario:

					{}
""".format(reflexion_prompt,scenario)

			query += '\n\nNew plan:'
		else:
			if 'problem{}.log'.format(i+1) in os.listdir('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 zeroshot trialwise new reflexion step by step external feedback/trial{}/'.format(trial_no)):

				file_baseline = open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 zeroshot trialwise new reflexion step by step external feedback/trial{}/problem{}.log'.format(trial_no,i+1), 'r')
				lines_baseline = file_baseline.read().splitlines()
				file_baseline.close()
			else:
				print("File problem{}.log not there for trial no {} because it was solved optimally before".format(i+1,trial_no))
				continue




			task_index=0
			for q in range(len(lines_baseline)):
			    if "Here is the task:" in lines_baseline[q]:
			        task_index=q
			        break

			for q in range(task_index,len(lines_baseline)):
				if "Solved problem" in lines_baseline[q]:

                  

                  
					num_moves = float(lines_baseline[q].split(".")[0].split(" ")[-2])
				else:
					num_moves = 50

			if num_moves == optimal_steps_3_4_numbers_problemwise[i]:
				print("problem{}.log solved in optimal number of steps={}. Success!!!!".format(i+1,num_moves))
				continue

			memory_index=0
			for q in range(len(lines_baseline)):
			    if "Your memory for the task below:" in lines_baseline[q]:
			        memory_index=q
			        break
			
			scenario="""
"""
			for idx,l in enumerate(lines_baseline):
			    if idx>task_index:
			        scenario+=l+'\n'
	    
			previous_memory = """
"""

			for idx,l in enumerate(lines_baseline):
				if idx>memory_index and idx<task_index:
					previous_memory+=l+'\n'



		
			# print("previous memory>>",previous_memory)
			query = """You will be given the history of a past experience in which you were placed in an environment and asked to give a sequence of moves to solve a problem. You were either unsuccessful in solving the problem or solved it using more number of moves than required. Do not summarize your environment, but rather think about the strategy you took to attempt to complete the task. Devise a concise, new plan of moves that accounts for your mistake with reference to specific moves that you should have taken. For example, if you tried X and Y but forgot Z, then devise a plan to achieve Z with environment-specific moves. You will need this later when you are solving the same task. Give your plan after "Plan". Here are three examples:

					{}

					Here is the scenario:

					{}
""".format(reflexion_prompt,scenario)



			query += '\n\nFor your reference, here are the plans from past trials:\n'
			query += previous_memory

			query += '\n\nPlease generate the plan for the current trial. Your answer should contain only the description of the plan.'


			query += '\n\nNew plan:'



		# print("Reflexion query for trial {} problem {}".format(trail_no,i+1))
		
		reflexion_input = [{
		    "role": "system",
		    "content": "you are an AI assistant",
		}]

		reflexion_input.append({
		    "role": "user",
		    "content": query,
		})
		num_try=0
		while num_try<5:

			try:

				reflexion_response = openai.ChatCompletion.create(
				    engine='gpt-4-32k',
				    messages=reflexion_input,temperature=0.0,top_p=0,
				        max_tokens=500)
				num_try+=1
				break

			except Exception as e:
				err = f"Error: {str(e)}"
				print(err)
				time.sleep(60)
				
				continue

		# print("response>>",reflexion_response)


		if trial_no==0:

			prompt = """
Your memory for the task below:
Trial #{}:
{}

Here is the task:

Consider the following puzzle problem:

Problem description:
- There are three lists labeled A, B, and C.
- There are {} distributed among those three lists.
- You can only move numbers from the rightmost end of one list to the rightmost end of another list.

Goal: The goal is to end up in the configuration where all numbers are in list C, in ascending order.

Rule #1: You can only move a number if it is at the rightmost end of its current list.
Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.

This is the starting configuration:
{}
{}
{}
This is the goal configuration:
A = []
B = []
{}

Give me only the next move from the starting configuration, that would help in reaching the goal configuration using as few moves as possible. 
Your answer should be in the format as below:
Move <N> from list <src> to list <trg>.

			""".format(trial_no, reflexion_response.choices[0].message.content, number_message_mapping[num_disks],"A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])


		else:

			prompt = """
Your memory for the task below:
{}
Trial #{}:
{}

Here is the task:

Consider the following puzzle problem:

Problem description:
- There are three lists labeled A, B, and C.
- There are {} distributed among those three lists.
- You can only move numbers from the rightmost end of one list to the rightmost end of another list.

Goal: The goal is to end up in the configuration where all numbers are in list C, in ascending order.

Rule #1: You can only move a number if it is at the rightmost end of its current list.
Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.

This is the starting configuration:
{}
{}
{}
This is the goal configuration:
A = []
B = []
{}

Give me only the next move from the starting configuration, that would help in reaching the goal configuration using as few moves as possible. 
Your answer should be in the format as below:
Move <N> from list <src> to list <trg>.

			""".format(previous_memory,trial_no, reflexion_response.choices[0].message.content, number_message_mapping[num_disks],"A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])

		
		input = [{
				"role": "system",
				"content": "you are an AI assistant",
			}]

		input.append({
			"role": "user",
			"content": prompt,
		})

		flag=0
		total_reward = 0
		for step in range(50):
			# print("prompt>>",prompt)
	   
	   
		
	 	

			# input = [{
			# 	"role": "system",
			# 	"content": "you are an AI assistant",
			# }]

			# input.append({
			# 	"role": "user",
			# 	"content": prompt,
			# })

			cur_try = 0
			while cur_try <5:
				try:

					response = openai.ChatCompletion.create(
						engine='gpt-4-32k',
						messages=input,temperature=0.0,top_p=0,
							max_tokens=200)

					cur_try+=1
					
					

					for k in range(len(response.choices[0].message.content) - 27):
						sub_str = response.choices[0].message.content[k:k+28]
						if 'Move' in sub_str and 'from list' in sub_str and 'to list' in sub_str and (('A' in sub_str and 'B' in sub_str ) or ('C' in sub_str and 'B' in sub_str ) or ('A' in sub_str and 'C' in sub_str )) :


							gpt_truncated_response = sub_str
					# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :

					break

				except Exception as e:
					err = f"Error: {str(e)}"
					print(err)
					time.sleep(60)
					
					continue

			# print("gpt full response>>>",response.choices[0].message.content)
			# print("gpt truncated response>>>",gpt_truncated_response)
			# gpt_orig_message = response.choices[0].message.content
			# if "apolog" in gpt_orig_message:
			# 	move_index =0 
			# 	for idx,split_str in enumerate(gpt_orig_message.split(":")):
			# 	    if "correct next move" in split_str or "next move" in split_str or "correct move" in split_str or "next valid move" in split_str:
			# 	        move_index = idx+1
						

			# 	gpt_response = gpt_orig_message.split(":")[move_index].split(".")[0].replace(".","")
			# else:

			# 	gpt_response = gpt_orig_message.split(".")[0].replace(".","")
			
			no_to_move = int(gpt_truncated_response.split(" ")[1])
			source_list = gpt_truncated_response.split(" ")[4]
			target_list = gpt_truncated_response.split(" ")[7]
			# print(gpt_response,no_to_move,source_list,target_list)
			total_reward+=-1
			response_flag =0
			if no_to_move not in current_configuration[char_int_mapping[source_list]]:
				user_message = gpt_truncated_response + "\nInvalid move because {} is not in list {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
				reward_message = "Invalid move because {} is not in list {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
				response_flag =1
			else:
				if current_configuration[char_int_mapping[source_list]][-1]!= no_to_move:
					user_message = gpt_truncated_response + "\nInvalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
					reward_message = "Invalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
					response_flag =1
				else:
					if len(current_configuration[char_int_mapping[target_list]]):
						max_target_list = max(current_configuration[char_int_mapping[target_list]])
					else:
						max_target_list = -1

					if no_to_move < max_target_list:
						user_message = gpt_truncated_response + "\nInvalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
						reward_message = "Invalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
						response_flag=1
					else:
						user_message = gpt_truncated_response+'.'+'\nFor each move you get a penalty of -1.'
						reward_message = "For each move you get a penalty of -1."
						current_configuration[char_int_mapping[source_list]].pop()
						current_configuration[char_int_mapping[target_list]].append(no_to_move)

			if response_flag==1:
				total_reward+=-10

			configuration_msg = """This is the current configuration:
			{}
			{}
			{}

			This is the goal configuration:
			A = []
			B = []
			{}

			Give me only the next move from the current configuration, that would help in reaching the goal configuration using as few moves as possible. 
			Your answer should be in the format as below:
			Move <N> from list <src> to list <trg>.

			""".format("A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]),number_target_mapping[num_disks])

			


			prompt+="\n"+user_message+"\n"+configuration_msg

			# print("feedback>>",reward_message+"\n"+configuration_msg)

			input.append({
			"role": "assistant",
			"content": response.choices[0].message.content,
		})
			input.append({
			"role": "user",
			"content": reward_message+"\n"+configuration_msg,
		})

			if current_configuration == target_configuration:
				flag=1
				total_reward+=100
				with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 zeroshot trialwise new reflexion step by step external feedback/trial{}/problem{}.log'.format(trial_no+1,i+1), 'a') as w:
					w.write(prompt +'\n'+"Solved problem in {} steps. Total reward = {}".format(step+1,total_reward))

				break

		if flag==0:
			with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 zeroshot trialwise new reflexion step by step external feedback/trial{}/problem{}.log'.format(trial_no+1,i+1), 'a') as w:
				w.write(prompt +'\n'+"Timed out. Couldn't solve problem in 50 steps. Total reward = {}".format(total_reward))


		


	
		print("done solving problem {} for trial {}".format(i+1,trial_no))

