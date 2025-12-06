import os
import time
import requests
import serial
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from rq import get_current_job
from sqlalchemy.orm import Session
from .models import EngravingStatus, EngravingQueue, EngravingHistory
from .database import SessionLocal
from .engraving_queue import EngravingQueueManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EngravingWorker:
    def __init__(self):
        self.serial_port = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
        self.baud_rate = int(os.getenv("SERIAL_BAUD", 115200))
        self.engrave_interval = int(os.getenv("ENGRAVE_INTERVAL_SECONDS", 5))
        self.serial_connection = None
        self.db = SessionLocal()
        self.queue_manager = EngravingQueueManager(self.db)
    
    def process_job(self, job_id: int) -> Dict[str, Any]:
        job = self.db.query(EngravingQueue).filter(EngravingQueue.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"status": "error", "message": "Job not found"}
        
        try:
            self.queue_manager.update_job_status(
                job_id, 
                EngravingStatus.IN_PROGRESS,
                "Starting engraving process"
            )
            
            svg_data = self._download_svg(job.svg_url)
            if not svg_data:
                raise Exception(f"Failed to download SVG from {job.svg_url}")
            
            self._connect_serial()
            self._send_svg_to_arduino(svg_data)
            self._wait_for_engraving_completion(job_id)
            
            self.queue_manager.update_job_status(
                job_id,
                EngravingStatus.COMPLETED,
                "Engraving completed successfully"
            )
            
            return {"status": "success", "message": "Engraving completed"}
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            job.attempts += 1
            
            if job.attempts >= job.max_attempts:
                self.queue_manager.update_job_status(
                    job_id,
                    EngravingStatus.FAILED,
                    f"Failed after {job.attempts} attempts: {str(e)}"
                )
            else:
                job.status = EngravingStatus.PENDING
                self.queue_manager.update_job_status(
                    job_id,
                    EngravingStatus.PENDING,
                    f"Attempt {job.attempts} failed, will retry: {str(e)}"
                )
            
            return {"status": "error", "message": str(e)}
        
        finally:
            self._disconnect_serial()
            self.db.close()
    
    def _download_svg(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error downloading SVG: {str(e)}")
            return None
    
    def _connect_serial(self):
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baud_rate,
                timeout=10
            )
            time.sleep(2)
            logger.info(f"Connected to {self.serial_port}")
        except Exception as e:
            logger.error(f"Serial connection error: {str(e)}")
            raise
    
    def _disconnect_serial(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                logger.info("Serial connection closed")
            except Exception as e:
                logger.error(f"Error closing serial: {str(e)}")
    
    def _send_svg_to_arduino(self, svg_data: str):
        if not self.serial_connection or not self.serial_connection.is_open:
            raise Exception("No serial connection")
        
        try:
            self._send_command("START")
            
            chunk_size = 64
            for i in range(0, len(svg_data), chunk_size):
                chunk = svg_data[i:i+chunk_size]
                self._send_command(f"SEND_SVG:{chunk}")
            
            self._send_command("ENGRAVE")
            
        except Exception as e:
            logger.error(f"Error sending to Arduino: {str(e)}")
            raise
    
    def _send_command(self, command: str) -> str:
        if not self.serial_connection or not self.serial_connection.is_open:
            raise Exception("No serial connection")
        
        logger.debug(f"Sending: {command}")
        self.serial_connection.write(f"{command}\n".encode('utf-8'))
        
        start_time = time.time()
        while time.time() - start_time < 10:
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.readline().decode('utf-8').strip()
                logger.debug(f"Received: {response}")
                return response
            time.sleep(0.1)
        
        raise TimeoutError("Arduino response timeout")
    
    def _wait_for_engraving_completion(self, job_id: int):
        self.queue_manager.update_job_status(
            job_id,
            EngravingStatus.ENGRAVING,
            "Engraving in progress"
        )
        
        start_time = time.time()
        last_update = start_time
        
        while True:
            if not self.serial_connection or not self.serial_connection.is_open:
                raise Exception("Serial connection lost")
            
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.readline().decode('utf-8').strip()
                if response == "DONE":
                    logger.info("Engraving complete")
                    return
                elif response.startswith("ERROR:"):
                    raise Exception(f"Arduino error: {response[6:]}")
            
            if time.time() - last_update >= 5:
                elapsed = int(time.time() - start_time)
                self.queue_manager.update_job_status(
                    job_id,
                    EngravingStatus.ENGRAVING,
                    f"Engraving in progress ({elapsed}s)"
                )
                last_update = time.time()
            
            time.sleep(0.1)
            
            if time.time() - start_time > 3600:
                raise TimeoutError("Engraving timeout (1 hour)")

def process_engraving_job(job_id: int) -> Dict[str, Any]:
    worker = EngravingWorker()
    return worker.process_job(job_id)
