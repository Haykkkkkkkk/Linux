# Multi-Level Feedback Queue (MLFQ) Scheduler
 
This project implements a Multi-Level Feedback Queue (MLFQ) scheduler with time quantum support, I/O waiting, and aging mechanisms.  
 
## **How the Scheduler Works**  
- **Process Addition**: Each process is created with an arrival time (`arrival_time`), burst time (`burst_time`), and queue level.  
- **Process Execution**:  
  - Processes execute in the highest-priority queue first.  
  - Execution time is limited by a time quantum; after that, the process either moves to a lower-priority queue or stays in the same one.  
  - If a process requires I/O, it moves to a waiting state.  
- **Aging Mechanism**: If a process remains in a lower-priority queue for too long, it moves up a level.  
- **Console Output**:  
  - The current execution state is displayed every second.  
  - After each time quantum, the total execution time of the process is displayed.  
  - Completed processes are removed from the system.   
 
## **How to Run**  
1. Ensure Python 3 is installed.  
2. Run `main.py`:  
python main.py
