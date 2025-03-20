import time
from collections import deque
from process import Process
 
class MLFQScheduler:
    def __init__(self, num_queues=3, time_slices=[4, 8, 16]):
        """num_queues: number of queue levels"""
        self.num_queues = num_queues
        self.time_slices = time_slices
 
        # Each queue is a deque that holds processes
        self.queues = [deque() for _ in range(num_queues)]
 
        # List of processes that haven't arrived yet (waiting for arrival_time)
        self.pending_processes = []
 
        self.current_time = 0

 
    def add_process(self, process):
        """
        Add a process to the list of pending processes.
        When current_time reaches arrival_time, move it to queue[0].
        """
        self.pending_processes.append(process)
        print(f"[PEND] Process {process.pid} scheduled (arrival_time={process.arrival_time})")
 
    def check_arrivals(self):
        """
        Check if there are processes whose arrival_time <= current_time.
        If there are, place them in the highest priority queue (0).
        """
        arrived = [p for p in self.pending_processes if p.arrival_time <= self.current_time]
        for p in arrived:
            print(f"[NEW] Process {p.pid} arrived at {self.current_time}s -> queue 0")
            self.queues[0].append(p)
            self.pending_processes.remove(p)
 
    def handle_io(self):
        """
        Decrease io_burst for processes in the Waiting state.
        When io_burst <= 0, return the process to the Ready state.
        """
        for level in range(self.num_queues):
            for proc in list(self.queues[level]):
                if proc.status == "Waiting":
                    proc.io_burst -= 1
                    if proc.io_burst <= 0:
                        proc.status = "Ready"
                        print(f"[I/O DONE] Process {proc.pid} returned to Ready state")
 
    def aging(self, threshold=10):
        """
        If a process waits too long (waiting_time >= threshold) in lower queues,
        promote it to a higher level (decrease queue_level).
        """
        for level in range(1, self.num_queues):
            for proc in list(self.queues[level]):
                proc.waiting_time += 1
                if proc.waiting_time >= threshold:
                    new_level = max(0, proc.queue_level - 1)
                    print(f"[AGING] Process {proc.pid} waited too long -> promoted to queue {new_level}")
                    self.queues[level].remove(proc)
                    proc.queue_level = new_level
                    proc.waiting_time = 0
                    self.queues[new_level].append(proc)
 
    def pick_process(self):
        """
        Pick a process from the highest priority non-empty queue.
        If all queues are empty, return None.
        """
        for level in range(self.num_queues):
            if self.queues[level]:
                return level, self.queues[level][0]  # Take from the head of the queue
        return None, None
 
    def execute(self):
        """
        Run the simulation until all processes are done:
        - while there are processes in pending_processes or in queues
        """
        while self.pending_processes or any(self.queues):
            # 1) Check for new arrivals
            self.check_arrivals()
 
            # 2) Handle I/O (processes that were in Waiting)
            self.handle_io()
 
            # 3) Aging - promote processes that have been waiting for too long
            self.aging()
 
            # 4) Look for a process to execute 
            level, proc = self.pick_process()
            if not proc:
                # No ready processes, just "idle" for 1 second
                print(f"  > Time {self.current_time}s: No processes, waiting 1s...")
                self.current_time += 1
                time.sleep(1)
                continue
 
            # Check the quantum for this level
            quantum = self.time_slices[level]
 
            # Remove the process from the queue as we'll now "run" it
            self.queues[level].popleft()
 
            print(f"[RUN] Process {proc.pid} (Queue {level}, quantum={quantum}) - 1s step")
 
            proc.execute(1)
            proc.time_in_current_queue += 1
            self.current_time += 1
            time.sleep(1)
 

            if proc.status == "Finished":
                print(f"[FINISHED] Process {proc.pid} finished at {self.current_time}s")
            elif proc.needs_io():
                proc.status = "Waiting"
                print(f"[WAITING] Process {proc.pid} going to wait for I/O")
                self.queues[level].append(proc)
            else:
                if proc.time_in_current_queue >= quantum:
                    # Lower priority
                    if level < self.num_queues - 1:
                        proc.queue_level += 1
                        print(f"[PRIORITY↓] Process {proc.pid} moved to queue {proc.queue_level}")
                        proc.time_in_current_queue = 0  # reset the quantum counter
                        self.queues[proc.queue_level].append(proc)
                    else:
                        self.queues[level].append(proc)
                else:
                    self.queues[level].append(proc)
 
