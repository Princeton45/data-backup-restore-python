import boto3  
import schedule  # Library for scheduling periodic tasks

# Create an EC2 client for the 'us-east-1' region.
ec2_client = boto3.client('ec2', region_name="us-east-1")

def create_volume_snapshots():
    # Retrieve all available EBS volumes.
    volumes = ec2_client.describe_volumes(
        
    # Matches all the volumes that have the tag of "prod" to then create a snapshot for them
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': ['prod']
            }
        ]
    )
    
    # Iterate through each volume in the retrieved list.
    for volume in volumes['Volumes']:
        # Create a snapshot for the current volume using its VolumeId.
        new_snapshot = ec2_client.create_snapshot(
            VolumeId=volume['VolumeId']
        )
        # Print the snapshot's details after successful creation.
        print(new_snapshot)

# Schedule the create_volume_snapshots function to run every day.
schedule.every(1).day.do(create_volume_snapshots)

# Keep checking for scheduled tasks and run them when they're due.
while True:
    schedule.run_pending() 