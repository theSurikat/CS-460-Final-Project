#include "stdio.h"
#include <stdlib.h>
#include "unistd.h"
#include "string.h"
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <signal.h>


//shell script to call memlockd
#define memlockd_script "\
#/bin/bash \n\
memlockd /etc/tempCFG4daemon.cfg \n\
"

//shell script to clear kernel message log
#define clear_log_script "\
#/bin/bash \n\
tee /var/log/kern.log </dev/null \n\
"

void kill_memlockd(void){
	char pidStr[20]; //arbitrary value that is long enough
	FILE * pipe = popen("pidof memlockd","r");

	fgets(pidStr, 20, pipe);
	pid_t pid = strtoul(pidStr, NULL, 10);
	pclose(pipe);
	kill(pid, 9);
}

pid_t pidOfChild(const char * path){
	char pidofWithPath[100]; 
	pidofWithPath[0] = 'p';	
	pidofWithPath[1] = 'i';
	pidofWithPath[2] = 'd';
	pidofWithPath[3] = 'o';
	pidofWithPath[4] = 'f';
	pidofWithPath[6] = ' ';
	pidofWithPath[7] = '\0';

	strcat(pidofWithPath, path);


	char pidStr[20]; //arbitrary value that is long enough
	FILE * pipe = popen(pidofWithPath,"r");

	fgets(pidStr, 20, pipe);
	pid_t pid = strtoul(pidStr, NULL, 10);
	return pid;
}

void enable_memlockd(char * path2Executable, FILE ** cfg_fd){
	*cfg_fd = fopen("/etc/tempCFG4daemon.cfg", "w+"); //create cfg file for memlockd
	fputs(path2Executable, *cfg_fd); //put executable path into the cfg file
	system(memlockd_script); //call memlockd on our cfg file
}


int main(){
	system(clear_log_script);
	char executableName[80];
	char path2Executable[160];
	getcwd(path2Executable,(size_t)160);
	char userDoubleCheckBuffer[4];
	
	size_t sizeOfPath = strlen(path2Executable);
	path2Executable[sizeOfPath] = '/';
	path2Executable[sizeOfPath + 1] = '\0';

	char f = 'f';
	char * ff = &f;
	char ** fff = &ff;

	while(strncmp(userDoubleCheckBuffer, "yes", 3)){
		printf("Input name of your exec within the directory you are calling this program from\n");
		scanf("%79s",executableName);
		printf("Are you sure this is the path?\nIf you give the wrong path you could damage the kernel.\nInput yes or no\n");
		scanf("%3s", userDoubleCheckBuffer);
		userDoubleCheckBuffer[3] = '\0';
	}
	strcat(path2Executable,executableName);

	printf("%s\n",path2Executable);

	FILE * cfg_fd;
printf("here\n");
	enable_memlockd(path2Executable, &cfg_fd);


	
//	pid_t parent_pid = getpid();

	volatile int ready_to_execute = 0;

	pid_t pid = fork();
	if(pid == -1){ //failed to fork
		printf("failure to fork, exiting program. No memory is locked the system is safe still.\n");
	}else if(pid > 0){ //parent waits here

	}else{ //child executes here
		while(ready_to_execute == 0){;}
		execl(path2Executable, path2Executable, NULL);
	}

	printf("hey we didn't die!\n");

	int status;
	printf("pid = %d\n", pid);

	while(ready_to_execute == 0){
		printf("Enter 1 to start child process\n");
		scanf("%d",&ready_to_execute);	
	}



	waitpid(pid, &status, 0);
	if(WIFSIGNALED(status))
		printf("was signal killed!\n");
	else
		printf("was not signaled!\n");

	kill_memlockd();

	fclose(cfg_fd);
	chdir("/etc/");
	remove("tempCFG4daemon.cfg");

	return 0;
}

