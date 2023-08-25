# This repository contains code for building modules using LLMs inspired by the different functions of the prefrontal cortex.

Inspired by the different functions of the prefrontal cortex, we built the state predictor, monitor and the planner module. There is also an actor module which is either a GPT-4 (zero-shot) which has inputs the problem description, the current state, and the goal state, or GPT-4 (ICL) which also has access to a few incontext learning examples. When only GPT-4 (zero-shot) or GPT-4 (ICL), it is asked to propose all the actions along with the updated states after each action leading to the goal state. When used with the other modules (except planner), actor proposes just the next action from the current state. The state predictor module predicts the next state given as input, the proposed next action by the actor and the current state. The monitor module checks whether the proposed action is valid or invalid, if it is invalid then the actor is asked to try to propose the next action again with feedback from the monitor. When the planner module is used, the actor is asked to propose two actions from the current state, which is checked for validity by the monitor module, and then using a depth-first tree search procedure asked to propose two actions each from the next two states until a depth of 2. An evaluator module evaluates the final four states of the tree based on how far they are from the goal state. The final state that is closest to the goal state is chosen, and the action from the current state (root of the tree) that led to this final state is chosen as the next proposed action. Each of the modules are built using GPT-4 via prompting and a few shot incontext learning examples.


We evaluated our approach on two tasks, first one is a simplified formulation of the Tower of Hanoi task involving numbers instead of disks and lists instead of pegs. So a set of numbers is arranged in three lists (A, B, C) at the start, and the goal is to move all the numbers to list C in ascending order. The rules are you can only move a number if it is at the end of its current list, and you can move a number to the end of the list if it is larger than all the numbers in that list. The second one consists of two sub-tasks from the CogEval protocol, Valuepath - where there is a graph structure and there are two nodes containing rewards with different values, and the goal is to find the shortest path that gives the most reward. The second subtask is Steppath -  where there is a graph structure, and the goal is to find the shortest path (could be either 2-step, 3-step, or 4-step path) between two nodes.

Below we describe the different models that are implemented for the two tasks and instructions on how to run and evaluate them.

## Tower of Hanoi

The models implemented and their corresponding files are:

Optimal policy - `tower of hanoi without external feedback/solve_toh.py`

GPT-4(zero-shot) - `tower of hanoi full sequence without external feedback/gpt_solve_toh.py`

GPT-4(ICL) - `tower of hanoi full sequence without external feedback/gpt_standard_icl_solve_toh.py`

GPT-4(zero-shot) + State predictor - `tower of hanoi without external feedback/gpt_zeroshot_stepbystep_state_prediction.py`

GPT-4(ICL) + State predictor - `tower of hanoi without external feedback/gpt_standard_icl_stepbystep_state_prediction.py`

GPT-4(zero-shot) + State predictor + Monitor - `tower of hanoi without external feedback/gpt_zeroshot_error_monitor_stepbystep_state_prediction.py`

GPT-4(ICL) + State predictor + Monitor - `tower of hanoi without external feedback/gpt_standard_icl_error_monitor_stepbystep_state_prediction.py`

GPT-4(ICL) + State predictor + Monitor + Planner - `tower of hanoi without external feedback/gpt_standard_icl_error_monitor_generic_planner_stepbystep.py`

To run the optimal policy, `cd tower\ of\ hanoi\ without\ external\ feedback`, then `python solve_toh.py`
The first 26 generated log files (problem1.log to problem26.log) are tower of hanoi problems with three disks, the next 80 log files (problem27.log to problem106.log) are with four disks.

To run any of the above GPT-4 models you need to specify two required arguments- 1) openai API key 2) directory name where output log files will be stored

For e.g. to run GPT-4(ICL) + State predictor + Monitor + Planner, `cd tower\ of\ hanoi\ without\ external\ feedback`, then `python gpt_standard_icl_error_monitor_generic_planner_stepbystep.py --openai_api_key '<YOUR OPENAI KEY>' --output_dir '<OUTPUT DIRECTORY NAME>'`

By default, all GPT-4 runs are on problems with 3 disks. To run on 4 disks, add `--start_idx 26 --end_idx 106` to the arguments and also specify a different output directory to store the log files.

### Evaluation

There are four files in folder `eval scripts` named `gpt_zeroshot_fullsequence_eval_script.py, gpt_icl_fullsequence_eval_script.py, gpt_zeroshot_stepbystep_eval_script.py, gpt_icl_stepbystep_eval_script.py`

To run them you need to specify three required arguments- 1) number of disks 2) maximum number of moves allowed 3) directory name where output log files are stored

To evaluate only GPT-4(zero-shot) `cd eval\ scripts`, and then run `python gpt_zeroshot_fullsequence_eval_script.py --num_disks 3 --max_moves 10 --output_dir '<OUTPUT DIRECTORY NAME>'`

To evaluate only GPT-4(ICL), `cd eval\ scripts`, and then run `python gpt_icl_fullsequence_eval_script.py --num_disks 3 --max_moves 10 --output_dir '<OUTPUT DIRECTORY NAME>'`

To evaluate GPT-4(zero-shot) combined with other modules, `cd eval\ scripts`, and then run `python gpt_zeroshot_stepbystep_eval_script.py --num_disks 3 --max_moves 10 --output_dir '<OUTPUT DIRECTORY NAME>'`

To evaluate GPT-4(ICL) combined with other modules, `cd eval\ scripts`, and then run `python gpt_icl_stepbystep_eval_script.py --num_disks 3 --max_moves 10 --output_dir '<OUTPUT DIRECTORY NAME>'`


To evaluate on 4 disks just change to `--num_disks 4 --max_moves 20`

## CogEval

### Valuepath

The models implemented are:

GPT-4(zero-shot) - `cogeval full sequence without external feedback/gpt_zeroshot_valuepath.py`

GPT-4(ICL) - `cogeval full sequence without external feedback/gpt_standard_icl_valuepath.py`

GPT-4(zero-shot) + State predictor - `cogeval without external feedback/valuepath/gpt_zeroshot_valuepath_stepbystep.py`

GPT-4(ICL) + State predictor - `cogeval without external feedback/valuepath/gpt_standard_icl_valuepath_stepbystep.py`

GPT-4(zero-shot) + State predictor + Monitor - `cogeval without external feedback/valuepath/gpt_zeroshot_error_monitor_valuepath_stepbystep.py`

GPT-4(ICL) + State predictor + Monitor - `cogeval without external feedback/valuepath/gpt_standard_icl_error_monitor_valuepath_stepbystep.py`

To run any of the above GPT-4 models you need to specify two required arguments- 1) openai API key 2) directory name where output log files will be stored

For e.g. to run GPT-4(ICL) + State predictor + Monitor, `cd cogeval\ without\ external\ feedback/valuepath`, then `python gpt_standard_icl_error_monitor_valuepath_stepbystep.py --openai_api_key '<YOUR OPENAI KEY>' --output_dir '<OUTPUT DIRECTORY NAME>'`

#### Evaluation
There are two files in folder `eval scripts` named `gpt_valuepath_fullsequence_eval_script.py` and `gpt_valuepath_stepbystep_eval_script.py`

To run them you need to specify the directory name where output log files are stored

To evaluate only GPT-4(zero-shot) or GPT-4(ICL) `cd eval\ scripts`, and then run `python gpt_valuepath_fullsequence_eval_script.py --output_dir '<OUTPUT DIRECTORY NAME>'`

To evaluate all other GPT-4 models `cd eval\ scripts`, and then run `python gpt_valuepath_stepbystep_eval_script.py --output_dir '<OUTPUT DIRECTORY NAME>'`


### Steppath

The models implemented are:

GPT-4(zero-shot) - `cogeval full sequence without external feedback/gpt_zeroshot_steppath.py`

GPT-4(ICL) - `cogeval full sequence without external feedback/gpt_standard_icl_steppath.py`

GPT-4(zero-shot) + State predictor - `cogeval without external feedback/steppath/gpt_zeroshot_steppath_stepbystep.py`

GPT-4(ICL) + State predictor - `cogeval without external feedback/steppath/gpt_standard_icl_steppath_stepbystep.py`

GPT-4(zero-shot) + State predictor + Monitor - `cogeval without external feedback/steppath/gpt_zeroshot_error_monitor_steppath_stepbystep.py`

GPT-4(ICL) + State predictor + Monitor - `cogeval without external feedback/steppath/gpt_standard_icl_error_monitor_steppath_stepbystep.py`

To run any of the above GPT-4 models you need to specify two required arguments- 1) openai API key 2) directory name where output log files will be stored

For e.g. to run GPT-4(ICL) + State predictor + Monitor, `cd cogeval\ without\ external\ feedback/steppath`, then `python gpt_standard_icl_error_monitor_steppath_stepbystep.py --openai_api_key '<YOUR OPENAI KEY>' --output_dir '<OUTPUT DIRECTORY NAME>'`

#### Evaluation
There are two files in folder `eval scripts` named `gpt_steppath_fullsequence_eval_script.py` and `gpt_steppath_stepbystep_eval_script.py`

To run them you need to specify the directory name where output log files are stored

To evaluate only GPT-4(zero-shot) or GPT-4(ICL) `cd eval\ scripts`, and then run `python gpt_steppath_fullsequence_eval_script.py --output_dir '<OUTPUT DIRECTORY NAME>'`

To evaluate all other GPT-4 models `cd eval\ scripts`, and then run `python gpt_steppath_stepbystep_eval_script.py --output_dir '<OUTPUT DIRECTORY NAME>'`

