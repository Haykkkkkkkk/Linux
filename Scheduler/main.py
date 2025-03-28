from scheduler import MLFQScheduler
from process import Process

if __name__ == "__main__":
    scheduler = MLFQScheduler(num_queues=3, time_slices=[4, 8, 16])


    scheduler.add_process(Process(pid=1, burst_time=6, arrival_time=0, priority="High"))
    scheduler.add_process(Process(pid=2, burst_time=5, arrival_time=3, priority="Medium"))
    scheduler.add_process(Process(pid=3, burst_time=4, arrival_time=6, priority="Low"))
    scheduler.add_process(Process(pid=4, burst_time=3, arrival_time=6, priority="High"))
    scheduler.add_process(Process(pid=5, burst_time=7, arrival_time=0, priority="Medium"))
    
    
    scheduler.add_process(Process(pid=999, burst_time=10, arrival_time=2, priority="Critical"))

    scheduler.execute()
