import os
import redis
from rq import Queue
from typing import Optional, Dict, Any, Union, Callable
from datetime import datetime
from .models import EngravingQueue, EngravingStatus, EngravingHistory
from sqlalchemy.orm import Session
import logging
import sys
from queue import Queue as ThreadQueue
from threading import Thread, Event
import time
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we're in test mode (no Redis available)
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

if not TEST_MODE:
    try:
        # Try to connect to Redis
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))
        redis_conn = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        redis_conn.ping()  # Test connection
        
        # Create RQ queue if Redis is available
        engraving_queue = Queue('engraving', connection=redis_conn, default_timeout=3600)
        logger.info("Connected to Redis for job queuing")
    except Exception as e:
        logger.warning(f"Could not connect to Redis, falling back to in-memory queue: {e}")
        TEST_MODE = True

class InMemoryQueue:
    """In-memory queue implementation for testing"""
    def __init__(self):
        self.queue = ThreadQueue()
        self.jobs = {}
        self._stop_event = Event()
        self._worker_thread = None
        self._start_worker()

    def enqueue(self, func: Callable, *args, **kwargs) -> str:
        job_id = str(uuid4())
        self.jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'created_at': datetime.utcnow(),
            'result': None,
            'error': None,
            'args': args,
            'kwargs': kwargs
        }
        self.queue.put((job_id, func, args, kwargs))
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                job_id, func, args, kwargs = self.queue.get(timeout=1)
                job = self.jobs[job_id]
                job['status'] = 'started'
                job['started_at'] = datetime.utcnow()
                
                try:
                    result = func(*args, **kwargs)
                    job['status'] = 'completed'
                    job['result'] = result
                except Exception as e:
                    job['status'] = 'failed'
                    job['error'] = str(e)
                
                job['completed_at'] = datetime.utcnow()
                self.queue.task_done()
            except:
                continue

    def _start_worker(self):
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._stop_event.clear()
            self._worker_thread = Thread(target=self._worker, daemon=True)
            self._worker_thread.start()

    def stop(self):
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join()

# Initialize the appropriate queue
if TEST_MODE:
    logger.info("Using in-memory queue for testing")
    memory_queue = InMemoryQueue()
    
    # Create a wrapper to match RQ's interface
    class TestQueue:
        def enqueue(self, func, *args, **kwargs):
            job_id = memory_queue.enqueue(func, *args, **kwargs)
            return type('Job', (), {'id': job_id})
    
    engraving_queue = TestQueue()

class EngravingQueueManager:
    """
    Manages the engraving queue and job processing
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.engrave_interval = int(os.getenv("ENGRAVE_INTERVAL_SECONDS", 5))
    
    def add_to_queue(self, item_uid: str, svg_url: str) -> Dict[str, Any]:
        """
        Add a new job to the engraving queue
        """
        # Create a new queue entry
        job = EngravingQueue(
            item_uid=item_uid,
            svg_url=svg_url,
            status=EngravingStatus.PENDING
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        # Add to history
        self._add_history(job.id, EngravingStatus.PENDING, "Added to engraving queue")
        
        # Get position in queue
        position = self._get_queue_position(job.id)
        
        return {
            "job_id": job.id,
            "item_uid": item_uid,
            "status": job.status.value,
            "position": position,
            "created_at": job.created_at.isoformat()
        }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get the current status of the engraving queue
        """
        # Get pending and in-progress jobs
        pending_jobs = self.db.query(EngravingQueue).filter(
            EngravingQueue.status.in_([EngravingStatus.PENDING, EngravingStatus.IN_PROGRESS, EngravingStatus.ENGRAVING])
        ).order_by(EngravingQueue.created_at.asc()).all()
        
        # Get recent completed/failed jobs
        recent_jobs = self.db.query(EngravingQueue).filter(
            EngravingQueue.status.in_([EngravingStatus.COMPLETED, EngravingStatus.FAILED])
        ).order_by(EngravingQueue.completed_at.desc()).limit(10).all()
        
        return {
            "pending": [self._format_job(job) for job in pending_jobs],
            "recent": [self._format_job(job) for job in recent_jobs]
        }
    
    def get_job_status(self, item_uid: str) -> Dict[str, Any]:
        """
        Get the status of a specific job by item UID
        """
        job = self.db.query(EngravingQueue).filter(
            EngravingQueue.item_uid == item_uid
        ).order_by(EngravingQueue.created_at.desc()).first()
        
        if not job:
            return {"status": "not_found"}
        
        # Get history for this job
        history = self.db.query(EngravingHistory).filter(
            EngravingHistory.engraving_job_id == job.id
        ).order_by(EngravingHistory.created_at.asc()).all()
        
        result = self._format_job(job)
        result["history"] = [{
            "status": h.status.value,
            "message": h.message,
            "timestamp": h.created_at.isoformat()
        } for h in history]
        
        return result
    
    def update_job_status(self, job_id: int, status: EngravingStatus, message: str = None) -> bool:
        """
        Update the status of a job and add to history
        """
        job = self.db.query(EngravingQueue).filter(EngravingQueue.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return False
        
        job.status = status
        
        # Update timestamps
        if status == EngravingStatus.IN_PROGRESS and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in [EngravingStatus.COMPLETED, EngravingStatus.FAILED]:
            job.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        # Add to history
        self._add_history(job_id, status, message)
        
        return True
    
    def _add_history(self, job_id: int, status: EngravingStatus, message: str = None):
        """
        Add an entry to the job history
        """
        history = EngravingHistory(
            engraving_job_id=job_id,
            status=status,
            message=message
        )
        self.db.add(history)
        self.db.commit()
        
        # Add to queue (works with both RQ and in-memory queue)
        job = engraving_queue.enqueue(
            'app.engraving_worker.process_engraving_job' if not TEST_MODE else process_engraving_job,
            job_id,
            job_id=f'engrave_{job_id}'
        )
    
    def _get_queue_position(self, job_id: int) -> int:
        """
        Get the position of a job in the queue (0 = currently processing)
        """
        # Get all pending jobs ordered by creation time
        pending_jobs = self.db.query(EngravingQueue.id).filter(
            EngravingQueue.status == EngravingStatus.PENDING
        ).order_by(EngravingQueue.created_at.asc()).all()
        
        # Find the position of our job
        for i, job in enumerate(pending_jobs):
            if job.id == job_id:
                return i + 1  # 1-based position
        
        return 0  # Job not found in pending queue (might be in progress or completed)
    
    def _format_job(self, job: EngravingQueue) -> Dict[str, Any]:
        """
        Format a job for API response
        """
        return {
            "job_id": job.id,
            "item_uid": job.item_uid,
            "status": job.status.value,
            "svg_url": job.svg_url,
            "attempts": job.attempts,
            "max_attempts": job.max_attempts,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message
        }
