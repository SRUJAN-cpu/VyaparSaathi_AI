"""
ML-based forecasting using Amazon Forecast

This module implements structured data forecasting mode using Amazon Forecast
for ML-based demand predictions.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal
import time

import boto3
from botocore.exceptions import ClientError

# Initialize AWS clients
forecast_client = boto3.client('forecast')
forecastquery_client = boto3.client('forecastquery')
s3_client = boto3.client('s3')

# Environment variables
FORECAST_ROLE_ARN = os.environ.get('FORECAST_ROLE_ARN', '')
PROCESSED_DATA_BUCKET = os.environ.get('PROCESSED_DATA_BUCKET', 'vyaparsaathi-processed-data')


def prepare_forecast_data(
    user_id: str,
    skus: Optional[List[str]] = None,
    categories: Optional[List[str]] = None
) -> str:
    """
    Prepare data in Amazon Forecast format and upload to S3.
    
    Amazon Forecast expects CSV with columns:
    - timestamp (YYYY-MM-DD HH:MM:SS)
    - item_id (SKU)
    - target_value (demand quantity)
    
    Args:
        user_id: User identifier
        skus: Optional list of SKUs to include
        categories: Optional list of categories to include
        
    Returns:
        S3 URI of prepared data file
    """
    # TODO: Retrieve historical sales data from S3/DynamoDB
    # For now, return a placeholder
    
    data_key = f"forecast-data/{user_id}/sales_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    s3_uri = f"s3://{PROCESSED_DATA_BUCKET}/{data_key}"
    
    # In a real implementation, we would:
    # 1. Fetch historical sales data
    # 2. Transform to Forecast format
    # 3. Upload to S3
    
    return s3_uri


def create_dataset_group(dataset_group_name: str) -> str:
    """
    Create Amazon Forecast dataset group.
    
    Args:
        dataset_group_name: Name for the dataset group
        
    Returns:
        Dataset group ARN
    """
    try:
        response = forecast_client.create_dataset_group(
            DatasetGroupName=dataset_group_name,
            Domain='RETAIL',
            Tags=[
                {'Key': 'Application', 'Value': 'VyaparSaathi'},
                {'Key': 'Component', 'Value': 'ForecastEngine'}
            ]
        )
        return response['DatasetGroupArn']
    except forecast_client.exceptions.ResourceAlreadyExistsException:
        # Dataset group already exists, describe it
        response = forecast_client.describe_dataset_group(
            DatasetGroupArn=f"arn:aws:forecast:*:*:dataset-group/{dataset_group_name}"
        )
        return response['DatasetGroupArn']
    except ClientError as e:
        print(f"Error creating dataset group: {e}")
        raise


def create_dataset(dataset_name: str, dataset_group_arn: str) -> str:
    """
    Create Amazon Forecast dataset.
    
    Args:
        dataset_name: Name for the dataset
        dataset_group_arn: ARN of the dataset group
        
    Returns:
        Dataset ARN
    """
    schema = {
        'Attributes': [
            {'AttributeName': 'timestamp', 'AttributeType': 'timestamp'},
            {'AttributeName': 'item_id', 'AttributeType': 'string'},
            {'AttributeName': 'target_value', 'AttributeType': 'float'}
        ]
    }
    
    try:
        response = forecast_client.create_dataset(
            DatasetName=dataset_name,
            Domain='RETAIL',
            DatasetType='TARGET_TIME_SERIES',
            DataFrequency='D',  # Daily frequency
            Schema=schema,
            Tags=[
                {'Key': 'Application', 'Value': 'VyaparSaathi'},
                {'Key': 'Component', 'Value': 'ForecastEngine'}
            ]
        )
        return response['DatasetArn']
    except forecast_client.exceptions.ResourceAlreadyExistsException:
        # Dataset already exists
        response = forecast_client.describe_dataset(
            DatasetArn=f"arn:aws:forecast:*:*:dataset/{dataset_name}"
        )
        return response['DatasetArn']
    except ClientError as e:
        print(f"Error creating dataset: {e}")
        raise


def import_data(
    dataset_arn: str,
    data_s3_uri: str,
    import_job_name: str
) -> str:
    """
    Import data into Amazon Forecast dataset.
    
    Args:
        dataset_arn: ARN of the dataset
        data_s3_uri: S3 URI of the data file
        import_job_name: Name for the import job
        
    Returns:
        Import job ARN
    """
    try:
        response = forecast_client.create_dataset_import_job(
            DatasetImportJobName=import_job_name,
            DatasetArn=dataset_arn,
            DataSource={
                'S3Config': {
                    'Path': data_s3_uri,
                    'RoleArn': FORECAST_ROLE_ARN
                }
            },
            TimestampFormat='yyyy-MM-dd HH:mm:ss',
            Tags=[
                {'Key': 'Application', 'Value': 'VyaparSaathi'},
                {'Key': 'Component', 'Value': 'ForecastEngine'}
            ]
        )
        return response['DatasetImportJobArn']
    except ClientError as e:
        print(f"Error importing data: {e}")
        raise


def wait_for_import_job(import_job_arn: str, timeout_seconds: int = 600) -> bool:
    """
    Wait for data import job to complete.
    
    Args:
        import_job_arn: ARN of the import job
        timeout_seconds: Maximum time to wait
        
    Returns:
        True if successful, False otherwise
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        response = forecast_client.describe_dataset_import_job(
            DatasetImportJobArn=import_job_arn
        )
        status = response['Status']
        
        if status == 'ACTIVE':
            return True
        elif status in ['CREATE_FAILED', 'DELETE_FAILED']:
            print(f"Import job failed: {response.get('Message', 'Unknown error')}")
            return False
        
        time.sleep(10)
    
    print("Import job timed out")
    return False


def create_predictor(
    predictor_name: str,
    dataset_group_arn: str,
    forecast_horizon: int
) -> str:
    """
    Create and train Amazon Forecast predictor.
    
    Args:
        predictor_name: Name for the predictor
        dataset_group_arn: ARN of the dataset group
        forecast_horizon: Number of days to forecast
        
    Returns:
        Predictor ARN
    """
    try:
        response = forecast_client.create_auto_predictor(
            PredictorName=predictor_name,
            ForecastHorizon=forecast_horizon,
            ForecastFrequency='D',
            DataConfig={
                'DatasetGroupArn': dataset_group_arn
            },
            Tags=[
                {'Key': 'Application', 'Value': 'VyaparSaathi'},
                {'Key': 'Component', 'Value': 'ForecastEngine'}
            ]
        )
        return response['PredictorArn']
    except ClientError as e:
        print(f"Error creating predictor: {e}")
        raise


def wait_for_predictor(predictor_arn: str, timeout_seconds: int = 3600) -> bool:
    """
    Wait for predictor training to complete.
    
    Args:
        predictor_arn: ARN of the predictor
        timeout_seconds: Maximum time to wait
        
    Returns:
        True if successful, False otherwise
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        response = forecast_client.describe_auto_predictor(
            PredictorArn=predictor_arn
        )
        status = response['Status']
        
        if status == 'ACTIVE':
            return True
        elif status in ['CREATE_FAILED', 'DELETE_FAILED']:
            print(f"Predictor training failed: {response.get('Message', 'Unknown error')}")
            return False
        
        time.sleep(30)
    
    print("Predictor training timed out")
    return False


def create_forecast(
    forecast_name: str,
    predictor_arn: str
) -> str:
    """
    Create forecast from trained predictor.
    
    Args:
        forecast_name: Name for the forecast
        predictor_arn: ARN of the trained predictor
        
    Returns:
        Forecast ARN
    """
    try:
        response = forecast_client.create_forecast(
            ForecastName=forecast_name,
            PredictorArn=predictor_arn,
            Tags=[
                {'Key': 'Application', 'Value': 'VyaparSaathi'},
                {'Key': 'Component', 'Value': 'ForecastEngine'}
            ]
        )
        return response['ForecastArn']
    except ClientError as e:
        print(f"Error creating forecast: {e}")
        raise


def wait_for_forecast(forecast_arn: str, timeout_seconds: int = 600) -> bool:
    """
    Wait for forecast generation to complete.
    
    Args:
        forecast_arn: ARN of the forecast
        timeout_seconds: Maximum time to wait
        
    Returns:
        True if successful, False otherwise
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        response = forecast_client.describe_forecast(
            ForecastArn=forecast_arn
        )
        status = response['Status']
        
        if status == 'ACTIVE':
            return True
        elif status in ['CREATE_FAILED', 'DELETE_FAILED']:
            print(f"Forecast generation failed: {response.get('Message', 'Unknown error')}")
            return False
        
        time.sleep(10)
    
    print("Forecast generation timed out")
    return False


def query_forecast(
    forecast_arn: str,
    item_id: str,
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """
    Query forecast for a specific item.
    
    Args:
        forecast_arn: ARN of the forecast
        item_id: Item ID (SKU)
        start_date: Start date in ISO format
        end_date: End date in ISO format
        
    Returns:
        List of forecast predictions
    """
    try:
        response = forecastquery_client.query_forecast(
            ForecastArn=forecast_arn,
            Filters={
                'item_id': item_id
            },
            StartDate=start_date,
            EndDate=end_date
        )
        
        return response.get('Forecast', {}).get('Predictions', {})
    except ClientError as e:
        print(f"Error querying forecast: {e}")
        return []


def transform_forecast_to_daily_predictions(
    forecast_data: Dict[str, Any],
    festivals: List[Dict[str, Any]],
    sku: str,
    category: str
) -> List[Dict[str, Any]]:
    """
    Transform Amazon Forecast output to DailyPrediction format.
    
    Args:
        forecast_data: Raw forecast data from Amazon Forecast
        festivals: List of relevant festivals
        sku: Product SKU
        category: Product category
        
    Returns:
        List of DailyPrediction dictionaries
    """
    daily_predictions = []
    
    # Amazon Forecast returns predictions with p10, p50, p90 quantiles
    p10_values = forecast_data.get('p10', [])
    p50_values = forecast_data.get('p50', [])
    p90_values = forecast_data.get('p90', [])
    
    # Create festival lookup by date
    festival_by_date = {}
    for festival in festivals:
        festival_date = festival['date']
        if festival_date not in festival_by_date:
            festival_by_date[festival_date] = []
        festival_by_date[festival_date].append(festival)
    
    # Transform each prediction
    for i, p50_pred in enumerate(p50_values):
        timestamp = p50_pred.get('Timestamp', '')
        date = timestamp.split('T')[0] if 'T' in timestamp else timestamp
        
        # Get quantile values
        demand_forecast = p50_pred.get('Value', 0)
        lower_bound = p10_values[i].get('Value', demand_forecast * 0.8) if i < len(p10_values) else demand_forecast * 0.8
        upper_bound = p90_values[i].get('Value', demand_forecast * 1.2) if i < len(p90_values) else demand_forecast * 1.2
        
        # Calculate festival multiplier
        festival_multiplier = 1.0
        contributing_festivals = []
        
        if date in festival_by_date:
            for festival in festival_by_date[date]:
                multiplier = festival.get('demandMultipliers', {}).get(category, 1.0)
                if multiplier > festival_multiplier:
                    festival_multiplier = multiplier
                contributing_festivals.append(festival['name'])
        
        # Calculate confidence based on prediction interval width
        interval_width = upper_bound - lower_bound
        relative_width = interval_width / demand_forecast if demand_forecast > 0 else 1.0
        confidence = max(0.5, min(0.95, 1.0 - (relative_width / 2)))
        
        daily_predictions.append({
            'date': date,
            'demandForecast': round(demand_forecast, 2),
            'lowerBound': round(lower_bound, 2),
            'upperBound': round(upper_bound, 2),
            'festivalMultiplier': round(festival_multiplier, 2),
            'confidence': round(confidence, 2),
            'festivals': contributing_festivals
        })
    
    return daily_predictions


def generate_ml_forecast(forecast_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate ML-based forecast using Amazon Forecast.
    
    This is the main entry point for ML forecasting mode.
    
    Args:
        forecast_context: Context dictionary with all forecast parameters
        
    Returns:
        Forecast results dictionary
    """
    user_id = forecast_context['userId']
    forecast_horizon = forecast_context['forecastHorizon']
    festivals = forecast_context['festivals']
    skus = forecast_context.get('skus', [])
    categories = forecast_context.get('categories', [])
    
    # For MVP, we'll use a simplified approach
    # In production, this would involve full Amazon Forecast workflow
    
    # Generate unique names
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    dataset_group_name = f"vyaparsaathi-{user_id}-{timestamp}"
    
    try:
        # Note: Full Amazon Forecast workflow takes significant time (hours)
        # For MVP/demo, we'll return a placeholder structure
        # In production, this would be an async process with status tracking
        
        print(f"ML forecasting requested for user {user_id}")
        print(f"Note: Full Amazon Forecast workflow not implemented in MVP")
        print(f"Falling back to pattern-based forecasting")
        
        # Fall back to pattern-based forecasting
        from .pattern_forecaster import generate_pattern_forecast
        return generate_pattern_forecast(forecast_context)
        
    except Exception as e:
        print(f"Error in ML forecasting: {e}")
        # Fall back to pattern-based forecasting
        from .pattern_forecaster import generate_pattern_forecast
        return generate_pattern_forecast(forecast_context)
