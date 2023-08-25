
move_validator_icl_exs = """ 
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

"""
