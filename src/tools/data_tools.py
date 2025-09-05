import json
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from ..config.logging import logger


class DataSummary(BaseModel):
    total_records: int
    columns: List[str]
    data_types: Dict[str, str]
    missing_values: Dict[str, int]
    sample_data: List[Dict[str, Any]]


class DataStats(BaseModel):
    column: str
    count: int
    unique_count: int
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[Union[float, str]] = None
    max: Optional[Union[float, str]] = None
    quartiles: Optional[List[float]] = None


class DataTools:
    """Data processing and analysis tools for agents"""
    
    def __init__(self):
        pass
    
    async def load_json_data(self, data: Union[str, List[Dict], Dict]) -> List[Dict[str, Any]]:
        """Load and normalize JSON data"""
        try:
            if isinstance(data, str):
                # Parse JSON string
                parsed_data = json.loads(data)
            else:
                parsed_data = data
            
            # Normalize to list of dictionaries
            if isinstance(parsed_data, dict):
                # If it's a single object, wrap in a list
                normalized_data = [parsed_data]
            elif isinstance(parsed_data, list):
                # If it's already a list, use as is
                normalized_data = parsed_data
            else:
                logger.error(f"Unsupported data type: {type(parsed_data)}")
                return []
            
            logger.info(f"Loaded {len(normalized_data)} records")
            return normalized_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON data: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return []
    
    async def summarize_data(self, data: List[Dict[str, Any]], sample_size: int = 5) -> DataSummary:
        """Create a summary of the dataset"""
        if not data:
            return DataSummary(
                total_records=0,
                columns=[],
                data_types={},
                missing_values={},
                sample_data=[]
            )
        
        # Get all unique columns
        all_columns = set()
        for record in data:
            all_columns.update(record.keys())
        columns = sorted(list(all_columns))
        
        # Analyze data types and missing values
        data_types = {}
        missing_values = {}
        
        for column in columns:
            column_values = []
            missing_count = 0
            
            for record in data:
                if column in record and record[column] is not None:
                    column_values.append(record[column])
                else:
                    missing_count += 1
            
            # Determine data type
            if column_values:
                first_value = column_values[0]
                if isinstance(first_value, bool):
                    data_types[column] = "boolean"
                elif isinstance(first_value, int):
                    data_types[column] = "integer"
                elif isinstance(first_value, float):
                    data_types[column] = "float"
                elif isinstance(first_value, str):
                    data_types[column] = "string"
                else:
                    data_types[column] = "object"
            else:
                data_types[column] = "unknown"
            
            missing_values[column] = missing_count
        
        # Sample data
        sample_data = data[:sample_size]
        
        summary = DataSummary(
            total_records=len(data),
            columns=columns,
            data_types=data_types,
            missing_values=missing_values,
            sample_data=sample_data
        )
        
        logger.info(f"Generated summary for {len(data)} records with {len(columns)} columns")
        return summary
    
    async def calculate_column_stats(self, data: List[Dict[str, Any]], column: str) -> Optional[DataStats]:
        """Calculate statistics for a specific column"""
        if not data or column not in data[0]:
            logger.error(f"Column '{column}' not found in data")
            return None
        
        # Extract column values (excluding None/null)
        values = []
        for record in data:
            if column in record and record[column] is not None:
                values.append(record[column])
        
        if not values:
            logger.error(f"No valid values found for column '{column}'")
            return None
        
        stats = DataStats(
            column=column,
            count=len(values),
            unique_count=len(set(values))
        )
        
        # Calculate numeric statistics if applicable
        try:
            numeric_values = [float(v) for v in values if isinstance(v, (int, float))]
            
            if numeric_values:
                numeric_values.sort()
                n = len(numeric_values)
                
                stats.mean = sum(numeric_values) / n
                stats.median = numeric_values[n // 2] if n % 2 == 1 else (numeric_values[n // 2 - 1] + numeric_values[n // 2]) / 2
                
                # Standard deviation
                mean_val = stats.mean
                variance = sum((x - mean_val) ** 2 for x in numeric_values) / n
                stats.std = variance ** 0.5
                
                stats.min = min(numeric_values)
                stats.max = max(numeric_values)
                
                # Quartiles
                q1_idx = n // 4
                q3_idx = 3 * n // 4
                stats.quartiles = [
                    numeric_values[q1_idx],
                    stats.median,
                    numeric_values[q3_idx] if q3_idx < n else numeric_values[-1]
                ]
            
        except (ValueError, TypeError):
            # Non-numeric column
            stats.min = str(min(values))
            stats.max = str(max(values))
        
        logger.info(f"Calculated statistics for column '{column}'")
        return stats
    
    async def filter_data(self, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter data based on conditions"""
        filtered_data = []
        
        for record in data:
            match = True
            for column, condition_value in conditions.items():
                if column not in record:
                    match = False
                    break
                
                record_value = record[column]
                
                # Simple equality check (can be extended for complex conditions)
                if record_value != condition_value:
                    match = False
                    break
            
            if match:
                filtered_data.append(record)
        
        logger.info(f"Filtered data: {len(data)} -> {len(filtered_data)} records")
        return filtered_data
    
    async def group_data(self, data: List[Dict[str, Any]], group_by: str) -> Dict[str, List[Dict[str, Any]]]:
        """Group data by a specific column"""
        if not data or group_by not in data[0]:
            logger.error(f"Group by column '{group_by}' not found")
            return {}
        
        groups = {}
        for record in data:
            group_key = str(record.get(group_by, "Unknown"))
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(record)
        
        logger.info(f"Grouped data by '{group_by}' into {len(groups)} groups")
        return groups
    
    async def aggregate_data(self, data: List[Dict[str, Any]], group_by: str, agg_column: str, operation: str = "sum") -> Dict[str, float]:
        """Aggregate data by groups"""
        groups = await self.group_data(data, group_by)
        results = {}
        
        for group_key, group_data in groups.items():
            values = []
            for record in group_data:
                if agg_column in record and isinstance(record[agg_column], (int, float)):
                    values.append(float(record[agg_column]))
            
            if values:
                if operation == "sum":
                    results[group_key] = sum(values)
                elif operation == "mean" or operation == "avg":
                    results[group_key] = sum(values) / len(values)
                elif operation == "count":
                    results[group_key] = len(values)
                elif operation == "min":
                    results[group_key] = min(values)
                elif operation == "max":
                    results[group_key] = max(values)
                else:
                    results[group_key] = sum(values)  # default to sum
        
        logger.info(f"Aggregated data by '{group_by}' using '{operation}' on '{agg_column}'")
        return results


# Global tool instance
data_tools = DataTools()