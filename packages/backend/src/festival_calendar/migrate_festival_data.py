"""
Data migration script to populate DynamoDB FestivalCalendar table

This script loads festival seed data into the DynamoDB FestivalCalendar table.
It handles data transformation, validation, and batch writes for efficiency.
"""

import json
import os
import sys
from typing import Dict, List, Any
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

from .festival_seed_data import FESTIVAL_SEED_DATA, apply_regional_variation


def convert_floats_to_decimal(obj: Any) -> Any:
    """
    Convert float values to Decimal for DynamoDB compatibility.
    
    DynamoDB requires Decimal type for numeric values instead of float.
    
    Args:
        obj: Object to convert (dict, list, or primitive)
        
    Returns:
        Object with floats converted to Decimal
    """
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


def prepare_festival_items() -> List[Dict[str, Any]]:
    """
    Prepare festival items for DynamoDB insertion.
    
    This function:
    1. Converts festival seed data to DynamoDB format
    2. Creates separate items for each region (for GSI queries)
    3. Converts floats to Decimal
    4. Validates data integrity
    
    Returns:
        List of festival items ready for DynamoDB
    """
    items = []
    
    for festival in FESTIVAL_SEED_DATA:
        # Create a base item for the festival
        base_item = {
            'festivalId': festival['festivalId'],
            'name': festival['name'],
            'date': festival['date'],
            'regions': festival['region'],  # Store all regions
            'category': festival['category'],
            'demandMultipliers': festival['demandMultipliers'],
            'duration': festival['duration'],
            'preparationDays': festival['preparationDays'],
            'importance': festival['importance'],
            'historicalImpact': festival['historicalImpact'],
            'metadata': festival['metadata'],
        }
        
        # Convert floats to Decimal
        base_item = convert_floats_to_decimal(base_item)
        items.append(base_item)
        
        # Create regional variation items for GSI queries
        # Each region gets a separate item with regional adjustments
        for region in festival['region']:
            regional_festival = apply_regional_variation(festival, region)
            regional_item = {
                'festivalId': f"{festival['festivalId']}-{region}",
                'name': festival['name'],
                'date': festival['date'],
                'region': region,  # Single region for GSI
                'regions': festival['region'],  # All regions for reference
                'category': festival['category'],
                'demandMultipliers': regional_festival['demandMultipliers'],
                'duration': festival['duration'],
                'preparationDays': festival['preparationDays'],
                'importance': festival['importance'],
                'historicalImpact': festival['historicalImpact'],
                'metadata': festival['metadata'],
                'isRegionalVariation': True,
                'baseFestivalId': festival['festivalId'],
            }
            
            # Convert floats to Decimal
            regional_item = convert_floats_to_decimal(regional_item)
            items.append(regional_item)
    
    return items


def batch_write_items(
    dynamodb_client: Any,
    table_name: str,
    items: List[Dict[str, Any]],
    batch_size: int = 25
) -> Dict[str, Any]:
    """
    Write items to DynamoDB in batches.
    
    DynamoDB BatchWriteItem has a limit of 25 items per request.
    This function handles batching and retries for unprocessed items.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        table_name: Name of the DynamoDB table
        items: List of items to write
        batch_size: Number of items per batch (max 25)
        
    Returns:
        Dictionary with write statistics
    """
    stats = {
        'total_items': len(items),
        'written_items': 0,
        'failed_items': 0,
        'batches': 0,
    }
    
    # Process items in batches
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        stats['batches'] += 1
        
        # Prepare batch write request
        request_items = {
            table_name: [
                {'PutRequest': {'Item': item}}
                for item in batch
            ]
        }
        
        # Write batch with retry logic for unprocessed items
        unprocessed_items = request_items
        retry_count = 0
        max_retries = 3
        
        while unprocessed_items and retry_count < max_retries:
            try:
                response = dynamodb_client.batch_write_item(
                    RequestItems=unprocessed_items
                )
                
                # Check for unprocessed items
                unprocessed_items = response.get('UnprocessedItems', {})
                
                if unprocessed_items:
                    retry_count += 1
                    print(f"Retrying {len(unprocessed_items.get(table_name, []))} unprocessed items (attempt {retry_count})")
                else:
                    stats['written_items'] += len(batch)
                    print(f"Successfully wrote batch {stats['batches']} ({len(batch)} items)")
                    
            except ClientError as e:
                print(f"Error writing batch {stats['batches']}: {e}")
                stats['failed_items'] += len(batch)
                break
        
        if unprocessed_items and retry_count >= max_retries:
            failed_count = len(unprocessed_items.get(table_name, []))
            stats['failed_items'] += failed_count
            print(f"Failed to write {failed_count} items after {max_retries} retries")
    
    return stats


def verify_data_integrity(
    dynamodb_client: Any,
    table_name: str,
    expected_count: int
) -> bool:
    """
    Verify that data was written correctly to DynamoDB.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        table_name: Name of the DynamoDB table
        expected_count: Expected number of items
        
    Returns:
        True if verification passed, False otherwise
    """
    try:
        # Scan table to count items
        response = dynamodb_client.scan(
            TableName=table_name,
            Select='COUNT'
        )
        
        actual_count = response['Count']
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = dynamodb_client.scan(
                TableName=table_name,
                Select='COUNT',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            actual_count += response['Count']
        
        print(f"\nData integrity check:")
        print(f"  Expected items: {expected_count}")
        print(f"  Actual items: {actual_count}")
        
        if actual_count == expected_count:
            print("  ✓ Data integrity verified")
            return True
        else:
            print("  ✗ Data integrity check failed")
            return False
            
    except ClientError as e:
        print(f"Error verifying data integrity: {e}")
        return False


def migrate_festival_data(
    table_name: str = None,
    region: str = 'us-east-1',
    dry_run: bool = False
) -> bool:
    """
    Main migration function to populate FestivalCalendar table.
    
    Args:
        table_name: DynamoDB table name (defaults to env var)
        region: AWS region
        dry_run: If True, only prepare data without writing
        
    Returns:
        True if migration succeeded, False otherwise
    """
    # Get table name from environment or parameter
    if table_name is None:
        table_name = os.environ.get('FESTIVAL_CALENDAR_TABLE', 'VyaparSaathi-FestivalCalendar')
    
    print(f"Festival Calendar Data Migration")
    print(f"================================")
    print(f"Table: {table_name}")
    print(f"Region: {region}")
    print(f"Dry run: {dry_run}")
    print()
    
    # Prepare festival items
    print("Preparing festival data...")
    items = prepare_festival_items()
    print(f"Prepared {len(items)} items")
    print(f"  - Base festivals: {len(FESTIVAL_SEED_DATA)}")
    print(f"  - Regional variations: {len(items) - len(FESTIVAL_SEED_DATA)}")
    print()
    
    if dry_run:
        print("Dry run mode - skipping write to DynamoDB")
        print("\nSample item:")
        print(json.dumps(items[0], indent=2, default=str))
        return True
    
    # Initialize DynamoDB client
    print("Connecting to DynamoDB...")
    dynamodb_client = boto3.client('dynamodb', region_name=region)
    
    # Convert items to DynamoDB format
    print("Converting items to DynamoDB format...")
    dynamodb_items = []
    for item in items:
        # Use boto3's TypeSerializer to convert Python dict to DynamoDB format
        from boto3.dynamodb.types import TypeSerializer
        serializer = TypeSerializer()
        dynamodb_item = {k: serializer.serialize(v) for k, v in item.items()}
        dynamodb_items.append(dynamodb_item)
    
    # Write items to DynamoDB
    print(f"\nWriting {len(dynamodb_items)} items to DynamoDB...")
    stats = batch_write_items(dynamodb_client, table_name, dynamodb_items)
    
    # Print statistics
    print(f"\nMigration Statistics:")
    print(f"  Total items: {stats['total_items']}")
    print(f"  Written items: {stats['written_items']}")
    print(f"  Failed items: {stats['failed_items']}")
    print(f"  Batches processed: {stats['batches']}")
    
    # Verify data integrity
    if stats['failed_items'] == 0:
        print("\nVerifying data integrity...")
        integrity_ok = verify_data_integrity(
            dynamodb_client,
            table_name,
            len(dynamodb_items)
        )
        
        if integrity_ok:
            print("\n✓ Migration completed successfully!")
            return True
        else:
            print("\n✗ Migration completed with integrity issues")
            return False
    else:
        print("\n✗ Migration completed with errors")
        return False


if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate festival data to DynamoDB')
    parser.add_argument('--table', type=str, help='DynamoDB table name')
    parser.add_argument('--region', type=str, default='us-east-1', help='AWS region')
    parser.add_argument('--dry-run', action='store_true', help='Prepare data without writing')
    
    args = parser.parse_args()
    
    # Run migration
    success = migrate_festival_data(
        table_name=args.table,
        region=args.region,
        dry_run=args.dry_run
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
