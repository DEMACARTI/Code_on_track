import time
from queue import Queue
from threading import Thread, Event, Lock
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timezone
import uuid

class InMemoryQueue:
    def __init__(self):
        self.queue = Queue()
        self.jobs = {}
        self._stop_event = Event()
        self._worker_thread = None
        self._lock = Lock()
        self._start_worker()

    def enqueue(self, func: Callable, *args, **kwargs) -> str:
        """Add a job to the queue and return its ID"""
        job_id = str(uuid.uuid4())
        
        with self._lock:
            self.jobs[job_id] = {
                'id': job_id,
                'status': 'queued',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'result': None,
                'error': None,
                'args': args,
                'kwargs': kwargs,
                'original_job_id': kwargs.pop('job_id', None)  # Store the original job ID if provided
            }
            self.queue.put((job_id, func, args, kwargs))
        
        print(f"Added job {job_id} to queue")
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status by ID"""
        with self._lock:
            # First try direct lookup
            if job_id in self.jobs:
                return self.jobs[job_id]
            
            # Then try to find by original_job_id
            for job in self.jobs.values():
                if job.get('original_job_id') == job_id:
                    return job
            
            return None

    def _worker(self):
        """Worker thread that processes jobs from the queue"""
        while not self._stop_event.is_set():
            try:
                job_id, func, args, kwargs = self.queue.get(timeout=1)
                
                with self._lock:
                    job = self.jobs.get(job_id)
                    if not job:
                        print(f"Job {job_id} not found in jobs dictionary")
                        continue
                        
                    job['status'] = 'started'
                    job['started_at'] = datetime.now(timezone.utc).isoformat()
                
                print(f"Starting job {job_id}")
                try:
                    result = func(*args, **kwargs)
                    with self._lock:
                        job['status'] = 'completed'
                        job['result'] = result
                        job['completed_at'] = datetime.now(timezone.utc).isoformat()
                    print(f"Job {job_id} completed successfully")
                    
                except Exception as e:
                    with self._lock:
                        job['status'] = 'failed'
                        job['error'] = str(e)
                        job['completed_at'] = datetime.now(timezone.utc).isoformat()
                    print(f"Job {job_id} failed: {e}")
                
                self.queue.task_done()
                
            except Exception as e:
                if not self._stop_event.is_set():
                    print(f"Worker error: {e}")
                time.sleep(0.1)

    def _start_worker(self):
        """Start the worker thread"""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._stop_event.clear()
            self._worker_thread = Thread(target=self._worker, daemon=True)
            self._worker_thread.start()

    def stop(self):
        """Stop the worker thread"""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join()

# Create a global queue instance
queue = InMemoryQueue()

def test_engraving_job(job_id: str) -> str:
    """Test function that simulates engraving"""
    print(f"Starting engraving job {job_id}")
    time.sleep(2)  # Simulate work (reduced from 5 to 2 seconds for testing)
    return f"Engraved item {job_id}"

def add_test_job(job_id=None):
    """Add a test job to the queue"""
    if job_id is None:
        job_id = str(uuid.uuid4())
    print(f"Adding job {job_id} to queue...")
    # Pass the job_id through kwargs so we can track it
    queue_job_id = queue.enqueue(test_engraving_job, job_id, job_id=job_id)
    return job_id  # Return the original job ID for tracking

if __name__ == "__main__":
    print("Testing in-memory queue system...")
    
    # Add test jobs
    print("\n=== Adding test jobs ===")
    job1 = add_test_job()
    job2 = add_test_job()
    
    print(f"\nJob 1 ID: {job1}")
    print(f"Job 2 ID: {job2}")
    
    # Monitor job status
    print("\n=== Monitoring job status ===")
    try:
        while True:
            print("\n--- Current Status ---")
            all_done = True
            
            for job_id in [job1, job2]:
                job = queue.get_job(job_id)
                if job:
                    status = job.get('status', 'unknown')
                    result = job.get('result', 'N/A')
                    error = job.get('error', 'None')
                    print(f"Job {job_id} (Queue ID: {job.get('id', 'N/A')}):")
                    print(f"  Status: {status}")
                    print(f"  Result: {result}")
                    print(f"  Error: {error}")
                    
                    if status not in ['completed', 'failed']:
                        all_done = False
                else:
                    print(f"Job {job_id}: Not found in queue")
                    all_done = False
            
            if all_done:
                print("\n=== All jobs completed! ===")
                break
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n=== Stopping worker... ===")
    finally:
        queue.stop()
        print("Queue worker stopped")
