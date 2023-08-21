# few shot examples for solving tower of hanoi
# problem1.log, problem3.log, problem19.log, problem22.log, problem24.log
#

standard_prompt = '''

	Example 1:

	This is the starting configuration:
	A = [0, 1, 2]
	B = []
	C = []
	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]

	Here is the sequence of minimum number of moves to reach the goal configuration from the starting configuration:

	Step 1. Move 2 from A to C.
	A = [0, 1]
	B = []
	C = [2]

	Step 2. Move 1 from A to B.
	A = [0]
	B = [1]
	C = [2]

	Step 3. Move 2 from C to B.
	A = [0]
	B = [1, 2]
	C = []

	Step 4. Move 0 from A to C.
	A = []
	B = [1, 2]
	C = [0]

	Step 5. Move 2 from B to A.
	A = [2]
	B = [1]
	C = [0]

	Step 6. Move 1 from B to C.
	A = [2]
	B = []
	C = [0, 1]

	Step 7. Move 2 from A to C.
	A = []
	B = []
	C = [0, 1, 2]


	Example 2:

	This is the starting configuration:
	A = []
	B = [0, 2]
	C = [1]
	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]

	Here is the sequence of minimum number of moves to reach the goal configuration from the starting configuration:

	Step 1. Move 1 from C to A.
	A = [1]
	B = [0, 2]
	C = []

	Step 2. Move 2 from B to A.
	A = [1, 2]
	B = [0]
	C = []

	Step 3. Move 0 from B to C.
	A = [1, 2]
	B = []
	C = [0]

	Step 4. Move 2 from A to B.
	A = [1]
	B = [2]
	C = [0]

	Step 5. Move 1 from A to C.
	A = []
	B = [2]
	C = [0, 1]

	Step 6. Move 2 from B to C.
	A = []
	B = []
	C = [0, 1, 2]


	Example 3:

	This is the starting configuration:
	A = [0, 1]
	B = [2]
	C = []
	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]
	
	Here is the sequence of minimum number of moves to reach the goal configuration from the starting configuration:

	Step 1. Move 2 from B to C.
	A = [0, 1]
	B = []
	C = [2]

	Step 2. Move 1 from A to B.
	A = [0]
	B = [1]
	C = [2]

	Step 3. Move 2 from C to B.
	A = [0]
	B = [1, 2]
	C = []

	Step 4. Move 0 from A to C.
	A = []
	B = [1, 2]
	C = [0]

	Step 5. Move 2 from B to A.
	A = [2]
	B = [1]
	C = [0]

	Step 6. Move 1 from B to C.
	A = [2]
	B = []
	C = [0, 1]

	Step 7. Move 2 from A to C.
	A = []
	B = []
	C = [0, 1, 2]
	

	Example 4:

	This is the starting configuration::
	A = [1]
	B = [0]
	C = [2]
	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]

	Here is the sequence of minimum number of moves to reach the goal configuration from the starting configuration:

	Step 1. Move 2 from C to A.
	A = [1, 2]
	B = [0]
	C = []

	Step 2. Move 0 from B to C.
	A = [1, 2]
	B = []
	C = [0]

	Step 3. Move 2 from A to B.
	A = [1]
	B = [2]
	C = [0]

	Step 4. Move 1 from A to C.
	A = []
	B = [2]
	C = [0, 1]

	Step 5. Move 2 from B to C.
	A = []
	B = []
	C = [0, 1, 2]

	
	Example 5:

	This is the starting configuration::
	A = [1]
	B = [2]
	C = [0]
	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]

	Here is the sequence of minimum number of moves to reach the goal configuration from the starting configuration:

	Step 1. Move 1 from A to C.
	A = []
	B = [2]
	C = [0, 1]

	Step 2: Move 2 from B to C.
	A = []
	B = []
	C = [0, 1, 2]



	
'''




