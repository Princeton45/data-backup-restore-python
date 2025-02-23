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