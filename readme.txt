Team Members:
	Sahil Das  	   - 21110184
	Yashraj J Deshmukh - 21110245



Instruction for Q1:
	Command to run:
		sudo python3 <path_to_the_file>
	
	If an error is raised such as - 
	
		"Cannot find required executable ovs-controller"
					or
		"Could not find a default openFlow controller"
		
	then run this: sudo apt get install openvswitch-testcontroller
	
	
	Note: "sudo mn -c" is recommended before running the file 



Instruction for Q2:
	Command to run:
		sudo python <path_to_the_file> --config=<either_b_or_c> --congestion=<congestion_algo> --loss=<between_0_and_100(int)>
		
	Here,
		congestion_algo can be set as
		cubic, reno, vegas, bbt
		
	In case of any error refer to Q1 instructions 
	

