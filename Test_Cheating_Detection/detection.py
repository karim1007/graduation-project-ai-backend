from frame_analysis import process_directory
import os

# New function to process a specific candidate's content
def process_candidate_exam(candidate_name):
    # Create content path based on candidate name
    content_path = os.path.join(r"C:\Users\PC\Desktop\grad\Test-Cheating-Detection\content", candidate_name)
    
    # Process the directory
    result = process_directory(content_path)
    
    # Analyze the results
    analysis = analyze_results(result)
    
    # Extract just the filenames for phone usage frames
    phone_frames = [os.path.basename(frame) for frame in analysis["phone_usage_frames"]]
    
    # Extract just the filenames for frames with multiple people
    multiple_people_frames = [os.path.basename(frame) for frame in analysis["multiple_people_frames"]]
    
    # Format the output in the exact format requested
    formatted_result = {
        "Candidate": candidate_name,
        "Phone usage detected": len(phone_frames),
        "Frames with phone detection": phone_frames if phone_frames else [],
        "People detected (more than 1)": len(multiple_people_frames),
        "Frames with multiple people detection": multiple_people_frames if multiple_people_frames else [],
        "People count changes detected": len(analysis["people_count_changes"]),
        "Total frames processed": len(result)
    }
    
    return formatted_result

# Process results to detect phone usage and people count changes
def analyze_results(results):
    phone_usage_frames = []
    multiple_people_frames = []  # Changed to track frames with multiple people
    people_count_changes = []
    previous_count = None
    unique_people_counts = set()
    
    for i, frame in enumerate(results):
        # Check for phone usage
        if frame['communication_device_present']:
            phone_usage_frames.append(frame['image_path'])
        
        # Track frames with multiple people detected (more than 1)
        if frame['people_count'] > 1:
            multiple_people_frames.append(frame['image_path'])
        
        # Track unique people counts
        unique_people_counts.add(frame['people_count'])
        
        # Check for people count changes
        current_count = frame['people_count']
        if previous_count is not None and current_count != previous_count:
            people_count_changes.append({
                'frame': frame['image_path'],
                'previous_count': previous_count,
                'current_count': current_count
            })
        previous_count = current_count
    
    # Summary
    print(f"Results analysis:")
    print(f"Total frames processed: {len(results)}")
    
    # Phone usage summary
    print(f"\nPhone detection summary:")
    if phone_usage_frames:
        print(f"Phone detected in {len(phone_usage_frames)} frames:")
        for frame in phone_usage_frames:
            print(f"  - {frame}")
    else:
        print("No phone usage detected in any frames.")
    
    # People count changes summary
    print(f"\nPeople count changes summary:")
    if people_count_changes:
        print(f"People count changed {len(people_count_changes)} times:")
        for change in people_count_changes:
            print(f"  - In {change['frame']}: {change['previous_count']} → {change['current_count']}")
    else:
        print("No changes in people count detected.")
    
    print(f"\nUnique people counts observed: {sorted(list(unique_people_counts))}")
    
    return {
        "phone_usage_frames": phone_usage_frames,
        "multiple_people_frames": multiple_people_frames,  # Updated name
        "people_count_changes": people_count_changes,
        "unique_people_counts": sorted(list(unique_people_counts))
    }

# Example usage
if __name__ == "__main__":
    # Process a specific candidate
    candidate_result = process_candidate_exam("karim")
    
    # Option 1: Print as formatted text
    print(f"Candidate: {candidate_result['Candidate']}")
    print(f"Phone usage detected: {candidate_result['Phone usage detected']} frames")
    if candidate_result['Phone usage detected'] > 0:
        print("Frames with phone detection:")
        for frame in candidate_result['Frames with phone detection']:
            print(f"  - {frame}")
    
    print(f"Multiple people detected: {candidate_result['People detected (more than 1)']} frames")
    if candidate_result['People detected (more than 1)'] > 0:
        print("Frames with multiple people detection:")
        for frame in candidate_result['Frames with multiple people detection']:
            print(f"  - {frame}")
    
    print(f"People count changes detected: {candidate_result['People count changes detected']} times")
    print(f"Total frames processed: {candidate_result['Total frames processed']}")
    
    # Option 2: Return as JSON
    import json
    print("\n==== JSON Output ====")
    print(json.dumps(candidate_result, indent=2))