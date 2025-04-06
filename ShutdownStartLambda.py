import boto3

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    rds_client = boto3.client('rds')

    action = event.get('action', 'stop')

    ec2_response = ec2_client.describe_instances(
        Filters=[{'Name': 'tag:Environment', 'Values': ['test']}]
    )

    instance_ids = []
    for reservation in ec2_response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])

    if instance_ids:
        if action == 'stop':
            print(f"Stopping EC2 instances: {instance_ids}")
            ec2_client.stop_instances(InstanceIds=instance_ids)
        elif action == 'start':
            print(f"Starting EC2 instances: {instance_ids}")
            ec2_client.start_instances(InstanceIds=instance_ids)
    else:
        print("No EC2 instances found with the Environment=test tag.")


    db_instances = rds_client.describe_db_instances()

    for db in db_instances['DBInstances']:
        db_identifier = db['DBInstanceIdentifier']
        tags = rds_client.list_tags_for_resource(ResourceName=db['DBInstanceArn']).get('TagList', [])

        for tag in tags:
            if tag['Key'] == 'Environment' and tag['Value'] == 'test':
                if action == 'stop':
                    print(f"Stopping RDS instance: {db_identifier}")
                    rds_client.stop_db_instance(DBInstanceIdentifier=db_identifier)
                elif action == 'start':
                    print(f"Starting RDS instance: {db_identifier}")
                    rds_client.start_db_instance(DBInstanceIdentifier=db_identifier)

    return {
        'statusCode': 200,
        'body': f'{action.capitalize()} operation completed successfully.'
    }
