from random import randint
 
class Process:
    def __init__(self, pid, burst_time, arrival_time=0):
        self.pid = pid
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.arrival_time = arrival_time
        self.waiting_time = 0      
        self.status = "Ready"      # Ready, Running, Waiting, Finished
        self.queue_level = 0       
        self.io_burst = randint(0, 3) if randint(0, 1) else 0  # Simulating I/O using random
        self.time_in_current_queue = 0
 
    def execute(self, seconds=1):
        self.remaining_time -= seconds
        if self.remaining_time <= 0:
            self.remaining_time = 0
            self.status = "Finished"
        else:
            self.status = "Running"
 
    def needs_io(self):
        """ Check if the process requires I/O (if not yet Finished). """
        return (self.io_burst > 0) and (self.status not in ("Finished", "Waiting"))
 
    def __str__(self):
        return (f"Process(pid={self.pid}, arr={self.arrival_time}, "
                f"remain={self.remaining_time}, queue={self.queue_level}, "
                f"io={self.io_burst}, status={self.status})")
