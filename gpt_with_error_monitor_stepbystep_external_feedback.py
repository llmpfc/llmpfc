import openai
from gen_start_config import *
from copy import deepcopy
import time
import re
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai7.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"
openai.api_key = "f48b5a4f15dc4e58991738ab066ba465"
all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
char_int_mapping = {'A':0,'B':1,'C':2}



for i in range(32,len(all_As)):
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


	prompt = """Consider the following puzzle problem:
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

	""".format(number_message_mapping[num_disks],"A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])


	reduced_prompt = """Consider the following puzzle problem:
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

	""".format(number_message_mapping[num_disks],"A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks])


	# print("starting prompt>>",prompt)

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
	step = 0
	num_tries=0
	max_content_limit_exceed_count = 0
	while step < 50:


		# print("step number>>",step)
		# print("current_configuration>>",current_configuration)
   
   
	
 	

		# input = [{
		# 	"role": "system",
		# 	"content": "you are an AI assistant",
		# }]

		# input.append({
		# 	"role": "user",
		# 	"content": prompt,
		# })

		cur_try = 0
		while cur_try <20:
			try:

				response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=input,temperature=0.0,top_p=0,
						max_tokens=200)

				
				
				

				for k in range(len(response.choices[0].message.content) - 27):
					sub_str = response.choices[0].message.content[k:k+28]
					if 'Move' in sub_str and 'from list' in sub_str and 'to list' in sub_str and (('A' in sub_str and 'B' in sub_str ) or ('C' in sub_str and 'B' in sub_str ) or ('A' in sub_str and 'C' in sub_str )) :


						gpt_truncated_response = sub_str

				# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :
				
				# print("configuration>>",current_configuration)
				# print("gpt response>>",gpt_truncated_response)
				break

			except Exception as e:
				err = f"Error: {str(e)}"

				if "This model's maximum context length is 32768 tokens" in err:
					print("length of input before and step number>>",len(input),step)
					if max_content_limit_exceed_count==0:
						print("first time for an example")

						input = [{"role": "system","content": "you are an AI assistant",}] +[{"role": "user","content": reduced_prompt,}]  + input[101:] # skip first 50 conversations between user and assistant
					else:
						print("not first time for an example")
						input = [{"role": "system","content": "you are an AI assistant",}] +[{"role": "user","content": reduced_prompt,}]  + input[102:]

					max_content_limit_exceed_count+=1


				print(err)
				print("Length of input now>>",len(input))
				time.sleep(60)
				cur_try+=1
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
		
		move_validator_prompt = """Consider the following puzzle problem:

		Here are two examples:
		Example 1:

		Problem description:
		- There are three lists labeled A, B, and C.
		- There are three numbers -- 0, 1, and 2 -- distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2.

		Goal: The goal is to check if the proposed move satisfies or violates Rule #1 and Rule #2 and based on that if it is a valid or invalid move.

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

		Problem description:
		- There are three lists labeled A, B, and C.
		- There are three numbers -- 0, 1, and 2 -- distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2.
		
		Goal: The goal is to check if the proposed move satisfies or violates Rule #1 and Rule #2 and based on that if it is a valid or invalid move.

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


		

		Here is the task:

		Problem description:
		- There are three lists labeled A, B, and C.
		- There are {} distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2.
		
		Goal: The goal is to check if the proposed move satisfies or violates Rule #1 and Rule #2 and based on that if it is a valid or invalid move.

		This is the initial configuration:
		{}
		{}
		{}
		Proposed move:
		{}.

		Answer:

		""".format(number_message_mapping[num_disks],"A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]),gpt_truncated_response)


		move_validator_input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		move_validator_input.append({
		"role": "user",
		"content": move_validator_prompt,
	})

		another_cur_try = 0
		while another_cur_try <5:
			try:

				validator_response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=move_validator_input,temperature=0.0,top_p=0,
						max_tokens=500)

				another_cur_try+=1
				
				
				char_list_response = validator_response.choices[0].message.content.split('\n')[-1].replace(".","").split(" ")
				if 'invalid' in char_list_response:
					move_validity = 'no'
				else:
					move_validity = 'yes'

				

						
				# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :

				break

			except Exception as e:
				err = f"Error: {str(e)}"
				print(err)
				time.sleep(60)
				
				continue

		# print("error monitor gpt full response>>",validator_response.choices[0].message.content)
		# print("move_validity>>",move_validity)
		if move_validity =='yes' or num_tries==10 :
			step+=1
			num_tries=0
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

			# print("external feedback>>",reward_message+"\n"+configuration_msg)

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
				with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 zeroshot with error monitor step by step external feedback/problem{}_new.log'.format(i+1), 'a') as w:
					w.write(prompt +'\n'+"Solved problem in {} steps. Total reward = {}".format(step+1,total_reward))

				break

		
		else:
			
			input.append({
			"role": "assistant",
			"content": response.choices[0].message.content,
		})
			internal_configuration_msg = """
			Invalid move. Please try again to give me the correct next move from the current configuration, that would help in reaching the goal configuration using as few moves as possible. Please make sure that the next move satisfies both Rule #1 and Rule #2. 
			Your answer should be in the format as below:
			Move <N> from list <src> to list <trg>.

			""" #.format("A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]),number_target_mapping[num_disks])


			input.append({
			"role": "user",
			"content": internal_configuration_msg,
		})
			num_tries+=1

			# print("error monitor feedback>>>",validator_response.choices[0].message.content + "\n"+configuration_msg)

	if flag==0:
		with open('/jukebox/griffiths/people/smondal/tower of hanoi/logs/gpt4 zeroshot with error monitor step by step external feedback/problem{}_new.log'.format(i+1), 'a') as w:
			w.write(prompt +'\n'+"Timed out. Couldn't solve problem in 50 steps. Total reward = {}".format(total_reward))


	


	
	print("done solving problem {}".format(i+1))

