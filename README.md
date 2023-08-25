# This repository contains code for building modules using LLMs inspired by the different functions of the prefrontal cortex.

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

