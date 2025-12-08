#!/usr/bin/env python3
"""
LLM-Based Report Generation for Railway Inspection
Reads YOLO detection results and generates structured maintenance reports
"""

import json
import os
from datetime import datetime
from typing import List, Dict

# Configuration
INPUT_JSON = 'yolo_output.json'
OUTPUT_REPORT = 'inspection_report.txt'
OUTPUT_HTML = 'inspection_report.html'

# Severity/Priority mapping
SEVERITY_MAP = {
    'crack': 'HIGH',
    'missing_clip': 'HIGH',
    'deformation': 'HIGH',
    'loose_bolt': 'MEDIUM',
    'loose_fastener': 'MEDIUM',
    'corrosion': 'MEDIUM',
    'wear': 'LOW'
}

def load_detection_data(json_path: str) -> Dict:
    """Load YOLO detection results from JSON"""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Detection file not found: {json_path}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    return data

def filter_high_confidence(detections: List[Dict], threshold: float = 0.60) -> List[Dict]:
    """Filter detections by confidence threshold for reporting"""
    filtered = [d for d in detections if d['confidence'] >= threshold]
    print(f"\nFiltering detections: {len(detections)} total → {len(filtered)} high-confidence (≥{threshold})")
    return filtered

def group_by_image(detections: List[Dict]) -> Dict[str, List[Dict]]:
    """Group detections by image filename"""
    grouped = {}
    for det in detections:
        img = det['image']
        if img not in grouped:
            grouped[img] = []
        grouped[img].append(det)
    return grouped

def assign_priority(defect_class: str) -> str:
    """Assign priority based on defect type"""
    return SEVERITY_MAP.get(defect_class, 'LOW')

def generate_text_report(data: Dict) -> str:
    """Generate human-readable text report"""
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append("RAILWAY COMPONENT INSPECTION REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Inspection Date: {data['inspection_date']}")
    report_lines.append(f"Total Images Analyzed: {data['total_images']}")
    report_lines.append(f"Total Detections: {data['total_detections']}")
    report_lines.append(f"Model Used: {data['model']}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Filter high-confidence detections
    detections = filter_high_confidence(data['detections'], threshold=0.60)
    
    if not detections:
        report_lines.append("✓ NO DEFECTS DETECTED - All components passed inspection")
        report_lines.append("")
        return "\n".join(report_lines)
    
    # Executive Summary
    report_lines.append("EXECUTIVE SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"High-Confidence Defects Detected: {len(detections)}")
    
    # Count by priority
    priority_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    for det in detections:
        priority = assign_priority(det['class'])
        priority_counts[priority] += 1
    
    report_lines.append(f"  - High Priority Issues: {priority_counts['HIGH']}")
    report_lines.append(f"  - Medium Priority Issues: {priority_counts['MEDIUM']}")
    report_lines.append(f"  - Low Priority Issues: {priority_counts['LOW']}")
    report_lines.append("")
    
    # Defects by Image
    report_lines.append("DETAILED FINDINGS")
    report_lines.append("-" * 80)
    
    grouped = group_by_image(detections)
    
    for img_name, img_detections in sorted(grouped.items()):
        report_lines.append(f"\nImage: {img_name}")
        report_lines.append(f"  Defects Found: {len(img_detections)}")
        report_lines.append("")
        
        # Sort by priority
        sorted_dets = sorted(img_detections, 
                            key=lambda x: (0 if assign_priority(x['class']) == 'HIGH' 
                                         else 1 if assign_priority(x['class']) == 'MEDIUM' 
                                         else 2))
        
        for i, det in enumerate(sorted_dets, 1):
            priority = assign_priority(det['class'])
            report_lines.append(f"  [{i}] {det['class'].upper()} (Priority: {priority})")
            report_lines.append(f"      Confidence: {det['confidence']:.1%}")
            report_lines.append(f"      Description: {det['description']}")
            report_lines.append(f"      Location: bbox({det['bbox']['x1']:.0f}, {det['bbox']['y1']:.0f}, "
                              f"{det['bbox']['x2']:.0f}, {det['bbox']['y2']:.0f})")
            report_lines.append("")
    
    # Maintenance Recommendations
    report_lines.append("-" * 80)
    report_lines.append("MAINTENANCE RECOMMENDATIONS")
    report_lines.append("-" * 80)
    
    if priority_counts['HIGH'] > 0:
        report_lines.append(f"\n⚠️  URGENT: {priority_counts['HIGH']} high-priority issue(s) require immediate attention!")
        report_lines.append("   - Schedule emergency maintenance within 24 hours")
        report_lines.append("   - Consider track closure if safety is compromised")
    
    if priority_counts['MEDIUM'] > 0:
        report_lines.append(f"\n⚠️  {priority_counts['MEDIUM']} medium-priority issue(s) detected")
        report_lines.append("   - Schedule maintenance within 7 days")
        report_lines.append("   - Monitor condition closely")
    
    if priority_counts['LOW'] > 0:
        report_lines.append(f"\nℹ️  {priority_counts['LOW']} low-priority issue(s) noted")
        report_lines.append("   - Include in routine maintenance schedule")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)

def generate_html_report(data: Dict) -> str:
    """Generate HTML report for better visualization"""
    detections = filter_high_confidence(data['detections'], threshold=0.60)
    
    priority_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    for det in detections:
        priority = assign_priority(det['class'])
        priority_counts[priority] += 1
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Railway Inspection Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .priority-high {{ color: #e74c3c; font-weight: bold; }}
        .priority-medium {{ color: #f39c12; font-weight: bold; }}
        .priority-low {{ color: #3498db; font-weight: bold; }}
        .defect {{ background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }}
        .defect.high {{ border-left-color: #e74c3c; }}
        .defect.medium {{ border-left-color: #f39c12; }}
        .image-section {{ margin: 20px 0; }}
        .recommendations {{ background: #fff3cd; padding: 20px; border-radius: 5px; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚂 Railway Component Inspection Report</h1>
        <p>Generated: {data['inspection_date']}</p>
    </div>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p><strong>Total Images:</strong> {data['total_images']}</p>
        <p><strong>High-Confidence Detections:</strong> {len(detections)}</p>
        <p class="priority-high">High Priority: {priority_counts['HIGH']}</p>
        <p class="priority-medium">Medium Priority: {priority_counts['MEDIUM']}</p>
        <p class="priority-low">Low Priority: {priority_counts['LOW']}</p>
    </div>
    
    <h2>Detailed Findings</h2>
"""
    
    if detections:
        grouped = group_by_image(detections)
        for img_name, img_detections in sorted(grouped.items()):
            html += f'<div class="image-section"><h3>📷 {img_name}</h3>'
            for det in img_detections:
                priority = assign_priority(det['class']).lower()
                html += f'''
                <div class="defect {priority}">
                    <strong>{det['class'].upper()}</strong> 
                    <span class="priority-{priority}">[{priority.upper()} PRIORITY]</span>
                    <br>Confidence: {det['confidence']:.1%}
                    <br>{det['description']}
                </div>
                '''
            html += '</div>'
    else:
        html += '<div class="summary">✓ No defects detected - All components passed inspection</div>'
    
    if priority_counts['HIGH'] > 0 or priority_counts['MEDIUM'] > 0:
        html += f'''
        <div class="recommendations">
            <h2>⚠️ Maintenance Recommendations</h2>
            {'<p class="priority-high">URGENT: Schedule emergency maintenance within 24 hours for high-priority issues!</p>' if priority_counts['HIGH'] > 0 else ''}
            {'<p class="priority-medium">Schedule maintenance within 7 days for medium-priority issues.</p>' if priority_counts['MEDIUM'] > 0 else ''}
        </div>
        '''
    
    html += "</body></html>"
    return html

def main():
    """Main execution function"""
    print("=" * 80)
    print("Railway Inspection Report Generator")
    print("=" * 80)
    
    # Load detection data
    try:
        data = load_detection_data(INPUT_JSON)
        print(f"\n✓ Loaded detection data from {INPUT_JSON}")
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"Please run 'python run_yolo.py' first to generate detection results.")
        return
    
    # Generate text report
    print(f"\nGenerating text report...")
    text_report = generate_text_report(data)
    
    with open(OUTPUT_REPORT, 'w') as f:
        f.write(text_report)
    print(f"✓ Text report saved to: {OUTPUT_REPORT}")
    
    # Generate HTML report
    print(f"Generating HTML report...")
    html_report = generate_html_report(data)
    
    with open(OUTPUT_HTML, 'w') as f:
        f.write(html_report)
    print(f"✓ HTML report saved to: {OUTPUT_HTML}")
    
    print("\n" + "=" * 80)
    print("Report generation complete!")
    print("=" * 80)
    
    # Print text report to console
    print("\n" + text_report)

if __name__ == "__main__":
    main()
