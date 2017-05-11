//#include <linux/moduleparam.h>
//#include <linux/module.h>    // included for all kernel modules
#include <linux/kernel.h>    // included for KERN_INFO
#include <linux/init.h>      // included for __init and __exit macros
#include <linux/pid.h>	
#include  <linux/sched.h>
#include <linux/mm.h>


//#include <asm-x86/page.h>

int param_var = 0;

struct pid * PID;
struct task_struct * task;
struct mm_struct * mm;

unsigned long start_vaddr = 0;
unsigned long end_vaddr = 0xC0000000;	
unsigned long paddr;
int ret = 0;
void * kaddr;

module_param(param_var, i, S_IRUSR | S_IWUSR);

int pmem_iterator = 0;
unsigned long pmemory_array [1024];
void * kmemory_array [1024];
unsigned long peetee [1024];

void display(void){
	printk("TEST: param = %d", param_var);
}

int pte_function(pte_t * pte, unsigned long addr, unsigned long next, struct mm_walk * walk){
	peetee[pmem_iterator] = (unsigned long)pte;
	return 0;	
}

static int hello_init(void){
	int i = 0;
	struct mm_walk mm_walk= {
		.mm = mm,
		.pte_entry = pte_function,
	};
//	printk("TEST: Hello world, this is jacob moshi moshi\n");
	display();

	PID = find_get_pid(param_var);
	task = pid_task(PID, PIDTYPE_PID);
	mm = get_task_mm(task);

	down_read(&mm->mmap_sem);

	while(start_vaddr < end_vaddr){
		u32 end;

		end = ((start_vaddr + PMD_SIZE)&PMD_MASK);

		if(end < start_vaddr || end > end_vaddr)
			end = end_vaddr;

		ret = walk_page_range(start_vaddr, end, &mm_walk);

		i++;
	}
	for(i = 0; i < 1024; i++){
		kmemory_array[i] = 0;
	}
	for(i = 0; i < 1024; i++){
		if(pmemory_array[i] != 0){
			kmemory_array[i] = __va(pmemory_array[i]);
		}
	}
	for(i = 0; i < 1024; i++){
		printk("address : %ld",(unsigned long)kmemory_array[i]);
	}
	up_read(&mm->mmap_sem);
	mmput(mm);

	return 0;
}

static void hello_exit(void){
//	printk("TEST: Good byte, moshi man\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_AUTHOR("JACOB");
MODULE_DESCRIPTION("DO NOTHING");
MODULE_LICENSE("GPL");
