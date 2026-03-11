"""
Week 4 - Synthetic Data Generation Script
Generates 1000+ service request records with realistic workflow patterns for ML training
"""

import sys
import os
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from enum import Enum

# Define enums locally to avoid database dependencies
class RequestType(Enum):
    CERTIFICATE = "certificate"
    HOSTEL = "hostel"
    IT_SUPPORT = "it_support"
    LIBRARY = "library"
    EXAM = "exam"
    TRANSCRIPT = "transcript"

class WorkflowStage(Enum):
    CREATED = "created"
    ASSIGNED = "assigned"
    VERIFIED = "verified"
    APPROVED = "approved"
    PROCESSED = "processed"
    COMPLETED = "completed"

# Configuration
NUM_REQUESTS = 1200  # Generate 1200 requests for robust training
OUTPUT_FILE = "data/raw/synthetic_requests.csv"

# SLA (Service Level Agreement) in hours for each request type
SLA_HOURS = {
    RequestType.CERTIFICATE: 72,   # 3 days
    RequestType.HOSTEL: 48,        # 2 days
    RequestType.IT_SUPPORT: 24,    # 1 day
    RequestType.LIBRARY: 48,       # 2 days
    RequestType.EXAM: 96,          # 4 days
    RequestType.TRANSCRIPT: 120,   # 5 days
}

# Stage duration distributions (mean, std_dev) in hours
STAGE_DURATIONS = {
    WorkflowStage.CREATED: (2, 1),      # Wait time before assignment
    WorkflowStage.ASSIGNED: (4, 2),     # Admin review time
    WorkflowStage.VERIFIED: (6, 3),     # Verification time
    WorkflowStage.APPROVED: (8, 4),     # Approval time
    WorkflowStage.PROCESSED: (12, 6),   # Processing time
    WorkflowStage.COMPLETED: (0, 0),    # Final stage
}

# Request type distribution (realistic weights)
REQUEST_TYPE_WEIGHTS = {
    RequestType.CERTIFICATE: 0.30,  # Most common
    RequestType.TRANSCRIPT: 0.25,
    RequestType.HOSTEL: 0.20,
    RequestType.LIBRARY: 0.12,
    RequestType.IT_SUPPORT: 0.08,
    RequestType.EXAM: 0.05,
}

# Priority distribution
PRIORITY_WEIGHTS = {
    1: 0.40,  # Low
    2: 0.45,  # Medium
    3: 0.15,  # High
}


def generate_temporal_features() -> Tuple[int, int, datetime]:
    """Generate realistic temporal features (hour, day of week, timestamp)"""
    # Requests more common during business hours and weekdays
    hour_weights = {
        **{h: 0.01 for h in range(0, 8)},    # Night (low)
        **{h: 0.08 for h in range(8, 12)},   # Morning (high)
        **{h: 0.06 for h in range(12, 14)},  # Lunch (medium)
        **{h: 0.07 for h in range(14, 18)},  # Afternoon (high)
        **{h: 0.02 for h in range(18, 24)},  # Evening (low)
    }
    
    # Days: Weekdays more likely than weekends
    day_weights = {
        0: 0.18,  # Monday
        1: 0.18,  # Tuesday
        2: 0.18,  # Wednesday
        3: 0.18,  # Thursday
        4: 0.18,  # Friday
        5: 0.05,  # Saturday (low)
        6: 0.05,  # Sunday (low)
    }
    
    hour = random.choices(list(hour_weights.keys()), weights=list(hour_weights.values()))[0]
    day_of_week = random.choices(list(day_weights.keys()), weights=list(day_weights.values()))[0]
    
    # Generate timestamp within last 6 months
    days_ago = random.randint(0, 180)
    base_date = datetime.now() - timedelta(days=days_ago)
    timestamp = base_date.replace(hour=hour, minute=random.randint(0, 59), second=0, microsecond=0)
    
    # Adjust to correct day of week
    current_dow = timestamp.weekday()
    day_diff = day_of_week - current_dow
    timestamp = timestamp + timedelta(days=day_diff)
    
    return hour, day_of_week, timestamp


def generate_stage_duration(stage: WorkflowStage, is_delayed: bool = False) -> float:
    """Generate realistic stage duration with delay factors"""
    mean, std_dev = STAGE_DURATIONS[stage]
    
    # Add delay factor for delayed requests
    if is_delayed and stage != WorkflowStage.CREATED:
        mean *= random.uniform(1.5, 2.5)  # 50-150% longer
        std_dev *= 1.5
    
    # Generate duration (ensure non-negative)
    duration = max(0.1, random.gauss(mean, std_dev))
    return round(duration, 2)


def calculate_handler_workload(timestamp: datetime, is_peak: bool = False) -> int:
    """Calculate handler workload based on time and load"""
    base_workload = random.randint(1, 5)
    
    # Peak hours (10-12, 14-16) have higher workload
    if is_peak or timestamp.hour in [10, 11, 14, 15]:
        base_workload += random.randint(2, 5)
    
    # Weekday vs weekend
    if timestamp.weekday() >= 5:  # Weekend
        base_workload = max(1, base_workload - 2)
    
    return base_workload


def generate_request_record(request_id: int) -> Dict:
    """Generate a single synthetic service request record"""
    
    # Select request type
    request_type = random.choices(
        list(REQUEST_TYPE_WEIGHTS.keys()),
        weights=list(REQUEST_TYPE_WEIGHTS.values())
    )[0]
    
    # Select priority
    priority = random.choices(
        list(PRIORITY_WEIGHTS.keys()),
        weights=list(PRIORITY_WEIGHTS.values())
    )[0]
    
    # Generate temporal features
    hour, day_of_week, created_at = generate_temporal_features()
    
    # Determine if request will be delayed (40% probability)
    # High priority requests less likely to be delayed
    delay_probability = 0.35 if priority == 3 else (0.40 if priority == 2 else 0.45)
    is_delayed = random.random() < delay_probability
    
    # Simulate workflow progression through stages
    current_time = created_at
    total_duration = 0
    stage_durations = {}
    
    stages = [
        WorkflowStage.CREATED,
        WorkflowStage.ASSIGNED,
        WorkflowStage.VERIFIED,
        WorkflowStage.APPROVED,
        WorkflowStage.PROCESSED,
        WorkflowStage.COMPLETED
    ]
    
    for stage in stages[:-1]:  # Exclude COMPLETED (has 0 duration)
        duration = generate_stage_duration(stage, is_delayed)
        stage_durations[stage.value] = duration
        total_duration += duration
        current_time += timedelta(hours=duration)
    
    # Calculate if actually delayed based on SLA
    sla_hours = SLA_HOURS[request_type]
    actual_is_delayed = total_duration > sla_hours
    
    # Get handler workload (average across stages)
    handler_workload = calculate_handler_workload(created_at, is_delayed)
    
    # Add some variability to match intended delay rate
    if is_delayed and not actual_is_delayed:
        # Force delay by adding extra time
        extra_hours = random.uniform(5, 20)
        total_duration += extra_hours
        stage_durations[WorkflowStage.PROCESSED.value] += extra_hours
        actual_is_delayed = True
    elif not is_delayed and actual_is_delayed:
        # Reduce delay slightly but may still be delayed
        reduction = random.uniform(0.7, 0.9)
        total_duration *= reduction
    
    # Final delay determination
    is_delayed_final = total_duration > sla_hours
    
    # Completion status (95% of requests complete eventually)
    is_completed = random.random() < 0.95
    final_stage = WorkflowStage.COMPLETED.value if is_completed else random.choice([
        WorkflowStage.ASSIGNED.value,
        WorkflowStage.VERIFIED.value,
        WorkflowStage.APPROVED.value,
        WorkflowStage.PROCESSED.value
    ])
    
    completed_at = current_time if is_completed else None
    
    # Build record
    record = {
        'request_id': f"REQ-SYN-{request_id:04d}",
        'request_type': request_type.value,
        'priority': priority,
        'created_hour': hour,
        'created_day_of_week': day_of_week,
        'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'completed_at': completed_at.strftime('%Y-%m-%d %H:%M:%S') if completed_at else None,
        'total_duration_hours': round(total_duration, 2),
        'sla_hours': sla_hours,
        'stage_created_duration': stage_durations.get(WorkflowStage.CREATED.value, 0),
        'stage_assigned_duration': stage_durations.get(WorkflowStage.ASSIGNED.value, 0),
        'stage_verified_duration': stage_durations.get(WorkflowStage.VERIFIED.value, 0),
        'stage_approved_duration': stage_durations.get(WorkflowStage.APPROVED.value, 0),
        'stage_processed_duration': stage_durations.get(WorkflowStage.PROCESSED.value, 0),
        'handler_workload': handler_workload,
        'final_stage': final_stage,
        'is_completed': 1 if is_completed else 0,
        'is_delayed': 1 if is_delayed_final else 0,
    }
    
    return record


def generate_synthetic_dataset(num_requests: int = NUM_REQUESTS) -> List[Dict]:
    """Generate complete synthetic dataset"""
    print(f"\n{'='*60}")
    print("  SYNTHETIC DATA GENERATION - Week 4")
    print('='*60)
    print(f"\nGenerating {num_requests} synthetic service requests...")
    print("This may take a minute...\n")
    
    records = []
    for i in range(1, num_requests + 1):
        record = generate_request_record(i)
        records.append(record)
        
        if i % 100 == 0:
            print(f"  ✅ Generated {i}/{num_requests} requests...")
    
    print(f"\n✅ Successfully generated {len(records)} records!")
    return records


def save_to_csv(records: List[Dict], output_file: str = OUTPUT_FILE):
    """Save records to CSV file"""
    print(f"\n📝 Saving data to {output_file}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if not records:
        print("❌ No records to save!")
        return
    
    # Write to CSV
    fieldnames = list(records[0].keys())
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✅ Data saved successfully!")
    print(f"   File: {output_file}")
    print(f"   Size: {os.path.getsize(output_file) / 1024:.2f} KB")


def print_dataset_statistics(records: List[Dict]):
    """Print statistics about generated dataset"""
    print(f"\n{'='*60}")
    print("  DATASET STATISTICS")
    print('='*60)
    
    total = len(records)
    delayed = sum(1 for r in records if r['is_delayed'] == 1)
    on_time = total - delayed
    completed = sum(1 for r in records if r['is_completed'] == 1)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Records: {total}")
    print(f"   Completed: {completed} ({completed/total*100:.1f}%)")
    print(f"   In Progress: {total - completed} ({(total-completed)/total*100:.1f}%)")
    
    print(f"\n⏱️  Delay Distribution:")
    print(f"   On-time: {on_time} ({on_time/total*100:.1f}%)")
    print(f"   Delayed: {delayed} ({delayed/total*100:.1f}%)")
    
    # Request type distribution
    print(f"\n📋 Request Type Distribution:")
    type_counts = {}
    for r in records:
        req_type = r['request_type']
        type_counts[req_type] = type_counts.get(req_type, 0) + 1
    
    for req_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {req_type}: {count} ({count/total*100:.1f}%)")
    
    # Priority distribution
    print(f"\n⚡ Priority Distribution:")
    priority_counts = {1: 0, 2: 0, 3: 0}
    for r in records:
        priority_counts[r['priority']] += 1
    
    for priority, count in priority_counts.items():
        priority_name = {1: "Low", 2: "Medium", 3: "High"}[priority]
        print(f"   {priority_name} (P{priority}): {count} ({count/total*100:.1f}%)")
    
    # Duration statistics
    durations = [r['total_duration_hours'] for r in records if r['is_completed'] == 1]
    if durations:
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        print(f"\n⏳ Completion Time Statistics:")
        print(f"   Average: {avg_duration:.2f} hours")
        print(f"   Min: {min_duration:.2f} hours")
        print(f"   Max: {max_duration:.2f} hours")
    
    # Temporal distribution
    print(f"\n📅 Temporal Distribution:")
    hour_counts = {}
    day_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    for r in records:
        hour_counts[r['created_hour']] = hour_counts.get(r['created_hour'], 0) + 1
        day_counts[r['created_day_of_week']] += 1
    
    print(f"   Peak Hour: {max(hour_counts, key=hour_counts.get)}:00 ({max(hour_counts.values())} requests)")
    
    days = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    peak_day = max(day_counts, key=day_counts.get)
    print(f"   Peak Day: {days[peak_day]} ({day_counts[peak_day]} requests)")
    
    print(f"\n{'='*60}")


def main():
    """Main execution function"""
    print("\n🤖 Week 4: Synthetic Data Generation for ML Training")
    print("This script generates 1000+ service request records with realistic patterns\n")
    
    try:
        # Generate data
        records = generate_synthetic_dataset(NUM_REQUESTS)
        
        # Save to CSV
        save_to_csv(records, OUTPUT_FILE)
        
        # Print statistics
        print_dataset_statistics(records)
        
        # Success message
        print("\n✅ SYNTHETIC DATA GENERATION COMPLETE!")
        print(f"\n📁 Dataset Location: {OUTPUT_FILE}")
        print(f"📊 Ready for ML Training (Week 5)")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review dataset in {OUTPUT_FILE}")
        print(f"   2. Validate data distribution")
        print(f"   3. Proceed to Week 5: ML Model Training")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
