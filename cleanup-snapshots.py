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