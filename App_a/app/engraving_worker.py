import os
import time
import requests
import serial
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from rq import get_current_job
from sqlalchemy.orm import Session
from .models import EngravingStatus, EngravingQueue, EngravingHistory
from .database import SessionLocal
from .engraving_queue import EngravingQueueManager
import qrcode
import uuid

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
            
            # Assuming the job contains a G-code file URL instead of an SVG
            gcode_data = self._download_svg(job.svg_url)  # Reusing the download method for G-code
            if not gcode_data:
                raise Exception(f"Failed to download G-code from {job.svg_url}")

            self._connect_serial()
            
            # Update GRBL settings for max travel dimensions
            self._update_grbl_settings()
            
            self._send_gcode_to_arduino(gcode_data)
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
    
    def _send_gcode_to_arduino(self, gcode_data: str):
        """Send G-code commands to the Arduino via GRBL."""
        if not self.serial_connection or not self.serial_connection.is_open:
            raise Exception("No serial connection")

        try:
            logger.info("Sending G-code to Arduino")

            for line in gcode_data.splitlines():
                command = line.strip()
                if command:
                    response = self._send_command(command)
                    logger.debug(f"Command: {command}, Response: {response}")

            logger.info("G-code transmission complete")
        except Exception as e:
            logger.error(f"Error sending G-code: {str(e)}")
            raise
    
    def _send_gcode_to_arduino_with_delay(self, gcode_data: str, delay: int):
        """Send G-code commands to the Arduino with a delay between each command."""
        if not self.serial_connection or not self.serial_connection.is_open:
            raise Exception("No serial connection")

        try:
            logger.info("Sending G-code to Arduino with delay")

            for line in gcode_data.splitlines():
                command = line.strip()
                if command:
                    response = self._send_command(command)
                    logger.debug(f"Command: {command}, Response: {response}")
                    time.sleep(delay)  # Add delay between commands

            logger.info("G-code transmission complete")
        except Exception as e:
            logger.error(f"Error sending G-code: {str(e)}")
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
    
    def _update_grbl_settings(self):
        """Update GRBL settings for max travel dimensions to 250x250mm."""
        if not self.serial_connection or not self.serial_connection.is_open:
            raise Exception("No serial connection")

        try:
            settings = {
                "$130": 250.0,  # X max travel
                "$131": 250.0,  # Y max travel
                "$132": 250.0   # Z max travel
            }

            for key, value in settings.items():
                command = f"{key}={value}"
                response = self._send_command(command)
                logger.info(f"Updated {key} to {value}, Response: {response}")

        except Exception as e:
            logger.error(f"Error updating GRBL settings: {str(e)}")
            raise

    def process_batch(self, batch_id: int, delay: int):
        """Process a batch of engraving jobs with a delay between each job."""
        jobs = self.db.query(EngravingQueue).filter(EngravingQueue.batch_id == batch_id).all()
        if not jobs:
            logger.error(f"No jobs found for batch {batch_id}")
            return {"status": "error", "message": "No jobs found for batch"}

        try:
            for job in jobs:
                logger.info(f"Processing job {job.id} in batch {batch_id}")
                self.process_job(job.id)
                logger.info(f"Completed job {job.id}, waiting for {delay} seconds before next job")
                time.sleep(delay)

            return {"status": "success", "message": "Batch processing completed"}
        except Exception as e:
            logger.error(f"Error processing batch {batch_id}: {str(e)}")
            return {"status": "error", "message": str(e)}

    def stop_engraving(self):
        """Stop the engraving process immediately."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self._send_command("!\n")  # GRBL feed hold command
                logger.info("Engraving process stopped")
            except Exception as e:
                logger.error(f"Error stopping engraving: {str(e)}")
        else:
            logger.warning("No active serial connection to stop engraving")

    def fetch_qr_codes(self, batch_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch QR codes from the database, optionally filtered by batch ID."""
        try:
            if batch_id:
                qr_codes = self.db.query(EngravingQueue).filter(EngravingQueue.batch_id == batch_id).all()
            else:
                qr_codes = self.db.query(EngravingQueue).all()

            return [
                {
                    "id": qr.id,
                    "qr_code": qr.qr_code,
                    "status": qr.status,
                    "batch_id": qr.batch_id
                }
                for qr in qr_codes
            ]
        except Exception as e:
            logger.error(f"Error fetching QR codes: {str(e)}")
            return []

    def generate_qr_code(self, data: str, batch_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate a QR code based on user input and store it in the database."""
        try:
            # Generate QR code image
            qr = qrcode.QRCode(box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Save QR code image to a temporary location
            temp_path = f"/tmp/{uuid.uuid4().hex}.png"
            img.save(temp_path)

            # Store QR code in the database
            qr_entry = EngravingQueue(
                qr_code=data,
                batch_id=batch_id,
                status="ready",
                image_path=temp_path
            )
            self.db.add(qr_entry)
            self.db.commit()

            return {
                "status": "success",
                "message": "QR code generated and stored successfully",
                "qr_code": data,
                "batch_id": batch_id
            }
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            return {"status": "error", "message": str(e)}

def process_engraving_job(job_id: int) -> Dict[str, Any]:
    worker = EngravingWorker()
    return worker.process_job(job_id)
