import time
from collections import deque
from process import Process

class MLFQScheduler:
    def __init__(self, num_queues=3, time_slices=[4, 8, 16]):
        """ Multi-Level Feedback Queue Scheduler with priority-based execution. """
        self.num_queues = num_queues
        self.time_slices = time_slices

        # Separate queues for priority levels
        self.critical_queue = deque()  # Critical processes (highest priority)
        self.user_queues = [deque() for _ in range(num_queues)]  # High, Medium, Low

        # List of processes waiting for their arrival time
        self.pending_processes = []
        self.finished_processes = []  # Store completed processes for performance analysis

        self.current_time = 0

    def add_process(self, process):
        """ Adds a process to the pending list until its arrival time is reached. """
        self.pending_processes.append(process)
        print(f"[PEND] Process {process.pid} scheduled (arrival_time={process.arrival_time}, priority={process.priority})")

    def check_arrivals(self):
        """ Moves processes from pending to the appropriate queue when they arrive. """
        arrived = [p for p in self.pending_processes if p.arrival_time <= self.current_time]
        for p in arrived:
            if p.priority == "Critical":
                print(f"[NEW] Critical Process {p.pid} arrived at {self.current_time}s -> critical queue")
                self.critical_queue.append(p)
            else:
                queue_idx = Process.PRIORITIES[p.priority] - 1  # Convert priority to index (High=0, Medium=1, Low=2)
                print(f"[NEW] Process {p.pid} arrived at {self.current_time}s -> queue {queue_idx}")
                self.user_queues[queue_idx].append(p)
            self.pending_processes.remove(p)

    def handle_io(self):
        """ Decreases I/O burst time for processes in 'Waiting' state. """
        for queue in self.user_queues:
            for proc in list(queue):
                if proc.status == "Waiting":
                    proc.io_burst -= 1
                    if proc.io_burst <= 0:
                        proc.status = "Ready"
                        print(f"[I/O DONE] Process {proc.pid} returned to Ready state")

    def aging(self, threshold=10):
        """ Promotes processes that have waited too long in lower queues. """
        for level in range(1, self.num_queues):
            for proc in list(self.user_queues[level]):
                proc.waiting_time += 1
                if proc.waiting_time >= threshold:
                    new_level = max(0, level - 1)
                    print(f"[AGING] Process {proc.pid} waited too long -> promoted to queue {new_level}")
                    self.user_queues[level].remove(proc)
                    proc.queue_level = new_level
                    proc.waiting_time = 0
                    self.user_queues[new_level].append(proc)

    def pick_process(self):
        """ Selects the highest-priority process available. """
        if self.critical_queue:
            return "Critical", self.critical_queue[0]

        for level in range(self.num_queues):
            if self.user_queues[level]:
                return level, self.user_queues[level][0]

        return None, None

    def execute(self):
        """ Runs the scheduling simulation. """
        while self.pending_processes or self.critical_queue or any(self.user_queues):
            self.check_arrivals()
            self.handle_io()
            self.aging()

            level, proc = self.pick_process()
            if not proc:
                print(f"  > Time {self.current_time}s: No processes, waiting 1s...")
                self.current_time += 1
                time.sleep(1)
                continue

            if level == "Critical":
                print(f"[RUN] Critical Process {proc.pid} - executes exclusively")
                self.critical_queue.popleft()
                while proc.remaining_time > 0:
                    proc.execute(1)
                    self.current_time += 1
                    time.sleep(1)

                print(f"[FINISHED] Critical Process {proc.pid} finished at {self.current_time}s")
                proc.turnaround_time = self.current_time - proc.arrival_time
                self.finished_processes.append(proc)
                continue  # Continue loop to check other processes

            quantum = self.time_slices[level]
            self.user_queues[level].popleft()
            print(f"[RUN] Process {proc.pid} (Queue {level}, quantum={quantum}) - 1s step")

            proc.execute(1)
            proc.time_in_current_queue += 1
            self.current_time += 1
            time.sleep(1)

            if proc.status == "Finished":
                print(f"[FINISHED] Process {proc.pid} finished at {self.current_time}s")
                proc.turnaround_time = self.current_time - proc.arrival_time
                self.finished_processes.append(proc)
            elif proc.needs_io():
                proc.status = "Waiting"
                print(f"[WAITING] Process {proc.pid} going to wait for I/O")
                self.user_queues[level].append(proc)
            else:
                if proc.time_in_current_queue >= quantum:
                    if level < self.num_queues - 1:
                        proc.queue_level += 1
                        print(f"[PRIORITY↓] Process {proc.pid} moved to queue {proc.queue_level}")
                        proc.time_in_current_queue = 0
                        self.user_queues[proc.queue_level].append(proc)
                    else:
                        self.user_queues[level].append(proc)
                else:
                    self.user_queues[level].append(proc)

        self.performance_summary()

    def performance_summary(self):
        """ Prints performance statistics after execution. """
        total_time = self.current_time
        total_waiting_time = sum(p.waiting_time for p in self.finished_processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.finished_processes)
        num_processes = len(self.finished_processes)

        avg_waiting_time = total_waiting_time / num_processes
        avg_turnaround_time = total_turnaround_time / num_processes

        print("\n=== Performance Summary ===")
        print(f"Total execution time: {total_time}s")
        print(f"Average waiting time: {avg_waiting_time:.2f}s")
        print(f"Average turnaround time: {avg_turnaround_time:.2f}s")
