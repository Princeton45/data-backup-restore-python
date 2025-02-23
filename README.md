# Data Backup & Restore for AWS EC2 Volumes

Hi! In this project, I created a few python scripts to automate the backup, cleanup, and restoration of AWS EC2 volumes. I leveraged Python and the Boto3 library to interact with AWS services.

## What I Did

1.  **EC2 Volume Backup:** I wrote a Python script that automatically creates snapshots of EC2 volumes.

First, I created 2 servers, one with a `Dev` tag and the other with a `Prod` tag.

![ec2-tags](https://github.com/Princeton45/data-backup-restore-python/blob/main/images/ec2-tag.png)

Then, I created the python script that once a day creates a snapshot of the EC2 Volumes and stores it in the EC2 Snapshots section in AWS.

`volume-backups.py`
```python
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
schedule.every().day.do(create_volume_snapshots)

# Keep checking for scheduled tasks and run them when they're due.
while True:
    schedule.run_pending() 
```

Below are the 2 snapshots created from the script for the 2 EC2 volumes.

![snapshots](https://github.com/Princeton45/data-backup-restore-python/blob/main/images/snapshots.png)

2.  **Old Snapshot Cleanup:** I developed another Python script that identifies and removes old EC2 volume snapshots to manage storage. This is because if the python scheduler runs everday, we will 
end up with a lot of snapshots so there needs to be a way to cleanup old snapshots.

We only need the most recent snapshots.

This script cleans up old snapshots of volumes with the name tag of `Prod` while leaving only 2 of the most recent snapshots.

`cleanup-snapshots.py`
```python
import boto3
from operator import itemgetter

# Creates an EC2 client for interacting with AWS EC2 in the "us-east-1" region.
ec2_client = boto3.client('ec2', region_name="us-east-1")

# Retrieve volumes that have the tag "Name" with a value of "prod".
volumes = ec2_client.describe_volumes(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': ['prod']
        }
    ]
)

# Iterate over each volume returned by the describe_volumes call.
for volume in volumes['Volumes']:
    # Retrieve snapshots owned by your account for the current volume.
    snapshots = ec2_client.describe_snapshots(
        OwnerIds=['self'],
        Filters=[
            {
                'Name': 'volume-id',
                'Values': [volume['VolumeId']]
            }
        ]
    )
    
    # Sort the snapshots by the StartTime in descending order (newest first).
    sorted_by_date = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)
    
    # Delete all snapshots except for the two most recent ones.
    # This iterates over the snapshots starting from the third one (index 2 onward).
    for snap in sorted_by_date[2:]:
        response = ec2_client.delete_snapshot(
            SnapshotId=snap['SnapshotId']
        )
        # Print the response from the delete operation.
        print(response)
```

As you can see below, the script is skipping the first 2 most recent snapshots, while displaying the rest

![snapshots-1](https://github.com/Princeton45/data-backup-restore-python/blob/main/images/snapshot-1.png)

![snapshots-2](https://github.com/Princeton45/data-backup-restore-python/blob/main/images/snapshot-2.png)

Now running the script, all snapshots other than the most recent 2 got deleted:

![snapdel1](https://github.com/Princeton45/data-backup-restore-python/blob/main/images/snapdel1.png)

![snapdel2](https://github.com/Princeton45/data-backup-restore-python/blob/main/images/snapdel2.png)



3.  **EC2 Volume Restoration:** I created a Python script to restore EC2 volumes from the created snapshot backups.

```python
# Import boto3 for AWS resource interactions and itemgetter for sorting snapshots
import boto3
from operator import itemgetter

# Initialize the boto3 client and resource for EC2 in the 'us-east-1' region.
ec2_client = boto3.client('ec2', region_name="us-east-1")
ec2_resource = boto3.resource('ec2', region_name="us-east-1")

# Define the instance ID for which we wish to manage volumes.
instance_id = "i-06cfc27313775bbb6"

# Retrieve all volumes attached to the given instance.
# The filter 'attachment.instance-id' returns volumes connected to the specified instance.
volumes = ec2_client.describe_volumes(
    Filters=[
        {
            'Name': 'attachment.instance-id',
            'Values': [instance_id]
        }
    ]
)

# We assume that the instance has only one attached volume.
# Therefore, we grab the first (and only) volume from the returned list.
instance_volume = volumes['Volumes'][0]
print(instance_volume) 

# Get the list of snapshots for the specified volume owned by the account ('self').
snapshots = ec2_client.describe_snapshots(
    OwnerIds=['self'],
    Filters=[
        {
            'Name': 'volume-id',
            'Values': [instance_volume['VolumeId']]
        }
    ]
)

# Sort the snapshot list in descending order based on the 'StartTime' field.
latest_snapshot = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)[0]
print(latest_snapshot['StartTime']) 

# Create a new volume from the latest snapshot.
new_volume = ec2_client.create_volume(
    SnapshotId=latest_snapshot['SnapshotId'],
    AvailabilityZone="us-east-1b",  # Ensure this matches your instance's zone if reattaching
    TagSpecifications=[
        {
            'ResourceType': 'volume',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'prod'
                }
            ]
        }
    ]
)

# This loop continuously checks whether the volume has become available.
while True:
    # Retrieve the current state of the new volume.
    vol = ec2_resource.Volume(new_volume['VolumeId'])
    print(vol.state) 
    
    # Once the volume is in the 'available' state, attach it to the instance.
    if vol.state == 'available':
        ec2_resource.Instance(instance_id).attach_volume(
            VolumeId=new_volume['VolumeId'],
            Device='/dev/xvdb'  
        )
        break  # Exit the loop after the volume has been successfully attached.
```