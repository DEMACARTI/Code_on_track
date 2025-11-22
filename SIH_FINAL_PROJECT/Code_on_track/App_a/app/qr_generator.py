import qrcode
import qrcode.image.svg
from io import BytesIO
import os
from pathlib import Path
from typing import Tuple
import uuid

class QRGenerator:
    """
    A utility class for generating QR codes in PNG and SVG formats.
    """
    
    def __init__(self, output_dir: str = "./qr_codes"):
        """
        Initialize the QR generator with an output directory.
        
        Args:
            output_dir: Directory to save generated QR codes
        """
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_qr_code(self, data: str, uid: str) -> Tuple[str, str]:
        """
        Generate both PNG and SVG QR codes for the given data.
        
        Args:
            data: The data to encode in the QR code
            uid: Unique identifier for the item (used in filenames)
            
        Returns:
            Tuple containing paths to the generated PNG and SVG files
        """
        # Generate a unique filename using the UID
        png_filename = f"{self.output_dir}/{uid}.png"
        svg_filename = f"{self.output_dir}/{uid}.svg"
        
        # Generate PNG QR code
        png_img = qrcode.make(data)
        png_img.save(png_filename)
        
        # Generate SVG QR code
        factory = qrcode.image.svg.SvgPathImage
        svg_img = qrcode.make(data, image_factory=factory)
        svg_img.save(svg_filename)
        
        return png_filename, svg_filename
    
    @staticmethod
    def generate_uid(component_type: str) -> str:
        """
        Generate a unique identifier for a component.
        
        Format: {PREFIX}-{RANDOM_STRING}
        
        Args:
            component_type: Type of the component (ERC, RP, LIN, SLP)
            
        Returns:
            str: A unique identifier string
        """
        # Generate a random string (first 8 chars of a UUID)
        random_str = str(uuid.uuid4())[:8].upper()
        return f"{component_type.upper()}-{random_str}"
    
    def cleanup_temp_files(self, png_path: str, svg_path: str) -> None:
        """
        Clean up temporary QR code files after they've been uploaded.
        
        Args:
            png_path: Path to the PNG file
            svg_path: Path to the SVG file
        """
        try:
            if os.path.exists(png_path):
                os.remove(png_path)
            if os.path.exists(svg_path):
                os.remove(svg_path)
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Error cleaning up QR code files: {e}")

# Create a global instance of the QR generator
qr_generator = QRGenerator()
