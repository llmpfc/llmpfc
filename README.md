# This repository contains code files for building modules using LLMs inspired by the different functions of the prefrontal cortex.

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

To run the optimal policy, `cd tower of hanoi without external feedback`, then `python solve_toh.py`
The first 26 generated log files (problem1.log to problem26.log) are tower of hanoi problems with three numbers, the next 80 log files (problem27.log to problem106.log) are with four numbers.

## CogEval

The models implemented are:

GPT-4(zero-shot)

GPT-4(ICL)

GPT-4(zero-shot) + State predictor

GPT-4(ICL) + State predictor

GPT-4(zero-shot) + State predictor + Monitor

GPT-4(ICL) + State predictor + Monitor




<!--
**llmpfc/llmpfc** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->
