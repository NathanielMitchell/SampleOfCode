// Nathaniel Mitchell and Jordan Williams

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stdbool.h>
#include <sys/types.h>
#include <sys/wait.h>

// shell command structure that saves the length of the command, an input file and an output file if applicable, and an array of tokens in the input
struct shell_command 
{
    char* base_command;
	int mod_length;
	char* input_file;
	char* output_file;
    char* modifiers[];
};

// function prototypes
void command_prompt();
void build_shell_command(char *input);
void execute_command(struct shell_command *command);

// GLOBALS
struct shell_command *command;
char working_dir[256];
char user_input[256];
unsigned char input_sign = 0;
unsigned char output_sign = 0;
bool input_flag = false;
bool output_flag = false;
extern int errno;
bool exit_flag = false;
bool cd_flag = false;
bool input_flag2 = false;
bool output_flag2 = false;

int main() 
{
	while(1) 
	{
		
		command_prompt();
		build_shell_command(user_input);
		execute_command(command);
		
		// check if the function should be exiting in case of errors
		if (exit_flag)
				break;
	}
	return 0;
}

void command_prompt()
{

	// prompt user for input
    printf("%s$ ", getcwd(working_dir, 256)); //Probably need to chop the first two in workingDir
    
    // collect user input into an array using fgets
    fgets(user_input, 256, stdin);
    
    // chop the newline character off of the input array
    user_input[strcspn(user_input, "\n")] = 0;
    
    // check to see if we should be looking for < 
    if (strcspn(user_input, "<") != strlen(user_input))
        input_flag = true;
    else
    	input_flag = false;
    	
    // check to see if we should be looking for >
    if (strcspn(user_input, ">") != strlen(user_input))
	output_flag = true;
    else
	output_flag = false;

}

void execute_command(struct shell_command *command) 
{
	// set errno to 0 to start
	errno = 0;
	
	// check to see if the base command is exit
	if(strcmp(command->base_command, "exit") == 0) 
	{
		// exit the function (returns to the main loop and breaks)
		exit_flag = true;
		return;
		
	} 
	// check to see if there is input or output
	else if (input_flag2 || output_flag2) 
	{
		// if there is input and output
		if(input_flag2 && output_flag2)
		{
			// set both flags to false for the next run
			input_flag2 = false;
			output_flag2 = false;

			// make the list of commands to be executed smaller to remove files and create a new array to that length
			int exec_array_length = (command->mod_length-4);
			char* exec_array[exec_array_length];

			// place the correct commands into the array
			for(int i = 0; i < ((exec_array_length-1)); i++) 
			{
				exec_array[i] = command->modifiers[i];
			}
			
			// make the final charater of the array a null character
			exec_array[(exec_array_length-1)] = NULL;

			if(fork() == 0) 
			{
				// check to see if the given input file is a real file and throw an error and exit if not
				if (access(command->input_file, F_OK) != 0)
				{
					errno = 2;
					printf("Error %d (%s)\n", errno, strerror(errno));
					exit(0);
				}
				
				// redirect stdin from the file
				FILE* infile = fopen(command->input_file, "r");
				
				dup2(fileno(infile), 0);
				fclose(infile);
				
				// redirect stdout from the file
				FILE* outfile = fopen(command->output_file, "w");
				dup2(fileno(outfile), 1);
				fclose(outfile);
				
				// if there is an error at this point, print it
				if (errno != 0)
				{
					printf("Error %d (%s)\n", errno, strerror(errno));
					exit(0);
				}
				
				// if no error, run the command using execvp
				execvp(exec_array[0], exec_array);
				
				// if this has created an error, print it
				if (errno != 0)
					printf("Error %d (%s)\n", errno, strerror(errno));
				exit(0);
			} 
			else 
			{
				wait(NULL);
			}
		}
		// if there is input and no output
		else if (input_flag2)
		{
			// reset input flag to false for next run
			input_flag2 = false;
			
			// find the length of the exec array and initialize it to that length
			int exec_array_length = (command->mod_length-2);
			char* exec_array[exec_array_length];

			// copy elements from the command array into the exec array
			for(int i = 0; i < ((exec_array_length-1)); i++) 
			{
				exec_array[i] = command->modifiers[i];
			}
			
			// set the last element of the array to null
			exec_array[(exec_array_length-1)] = NULL;

			if(fork() == 0) {
				// check to see if the input file exists and exit if it doesn't
				if (access(command->input_file, F_OK) != 0)
				{
					errno = 2;
					printf("Error %d (%s)\n", errno, strerror(errno));
					exit(0);
				}
				
				// redirect stdin
				FILE* infile = fopen(command->input_file, "r");
				dup2(fileno(infile), 0);
				fclose(infile);
				
				// check for error before executing the command
				if (errno != 0)
					printf("Error %d (%s)\n", errno, strerror(errno));
					
				// execute the command
				execvp(exec_array[0], exec_array); // this will change
				
				// check for an error after executing the command
				if (errno != 0)
					printf("Error %d (%s)\n", errno, strerror(errno));
				exit(0);
			} 
			else 
			{
				wait(NULL);
			}
		}
		
		// if there is only output to be redirected
		else if (output_flag2)
		{
			// reset the output flag to false
			output_flag2 = false;

			// find the length for the array to be executed and inialize a new array to that length
			int exec_array_length = (command->mod_length-2);
			char* exec_array[exec_array_length];

			// copy over elements from the command array into the array to be executed
			for(int i = 0; i < ((exec_array_length-1)); i++) 
			{
				exec_array[i] = command->modifiers[i];
			}
			
			// set the last element of the exec array to null
			exec_array[(exec_array_length-1)] = NULL;

			if(fork() == 0)
			{
				// redirect stdout
				FILE* outfile = fopen(command->output_file, "w");
				dup2(fileno(outfile), 1);
				fclose(outfile);
				
				// check for an error before executing
				if (errno != 0)
					printf("Error %d (%s)\n", errno, strerror(errno));
					
				// execute the commands from the exec array
				execvp(exec_array[0], exec_array); // this will change
				
				// print any errors after executing
				if (errno != 0)
					printf("Error after execvp %d (%s)\n", errno, strerror(errno));
				exit(0);
				} 
			else 
			{
				wait(NULL);
			}
		}
		

	} 
	
	// if the base command is cd
	else if(strcmp(command->base_command, "cd") == 0) 
	{
		// change the directory
		chdir(command->modifiers[1]);
		
		// if this causes an error, print the error and exit
		if (errno != 0)
		{
			printf("Error %d (%s)\n", errno, strerror(errno));
			cd_flag = true;
		}
	} 
	else if(fork() == 0) 
	{
			// check if there is an error before executing
			// if there is, exit
			if (errno != 0)
			{
				printf("Error %d (%s)\n", errno, strerror(errno));
				return;
			}
			
			// execute the commands
		 	execvp(command->base_command, command->modifiers);
		 	
		 	// if there is a new error, print the error and exit
			if (errno != 0 && !(cd_flag))
			{
				printf("Error %d (%s)\n", errno, strerror(errno));
				cd_flag = false;
				exit(0);
			}
		 } 
		 else 
		 {
		 	wait(NULL);
		 }
}

void build_shell_command(char* input) 
{
	// declare and initialize local variables
	char* mod_array[256];
	char* comm_literal;
	int i;
	
	// set the index of the input and output to 0
	input_sign = 0;
	output_sign = 0;
	
	// input tokens from the input into mod_array
	mod_array[0] = strtok(input, " ");
	
	// set the final element in the mod_array to NULL
	i = 1;
	while((mod_array[i] = strtok(NULL, " ")) != NULL) 
 		i++;
	mod_array[i] = NULL;
	
	// copy the first element in mod_array into comm_literal to define the first index
	comm_literal = strdup(mod_array[0]);

	// create a command structure using the size of the command + the size of the memory location for each element
	command = malloc(sizeof(*command) + 8*(i+1));
	
	// set the mod_length to be equal to the number of tokens + 1 for the null token
	command->mod_length = (i+1);
	
	// set the base command (first command) to the value stored in comm_literal
	command->base_command = comm_literal;
	
	// copy each item from the array of tokens into commands
	for(int j = 0; j <= i; j++) 
	{
		command->modifiers[j] = mod_array[j];
		
		// if there is an input
		if (input_flag)
		{
			// is the input sign in this section?
			if (mod_array[j][0] == '<')
			{
				// set the location of the input flag and reset the flag
				input_sign = j;
				input_flag = false;
				input_flag2 = true;
			}
		}
		if (output_flag)
		{
			// is the output sign in this section?
			if (mod_array[j][0] == '>')
			{
				// set the location of the output flag and reset the flag
				output_sign = j;
				output_flag = false;
				output_flag2 = true;
			}
		}
	}
	// set the input file and output file in command to be accessed outside of this function
	command->input_file = command->modifiers[input_sign+1];
	command->output_file = command->modifiers[output_sign+1];
	}
