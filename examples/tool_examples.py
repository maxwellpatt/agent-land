#!/usr/bin/env python3
"""
Tool usage examples for agent-land.

This script demonstrates how to use the various tools available in the framework
and how to integrate them with agents effectively.
"""

import asyncio
import json
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.web_search import web_search_tool
from src.tools.file_operations import file_operations_tool
from src.tools.data_tools import data_tools
from src.config.logging import logger


async def web_search_examples():
    """Demonstrate web search tool capabilities"""
    print("\n🔍 Web Search Tool Examples")
    print("=" * 50)
    
    # Basic search
    print("\n1. Basic Web Search:")
    search_results = await web_search_tool.search("Pydantic AI framework", max_results=3)
    
    for i, result in enumerate(search_results, 1):
        print(f"  {i}. {result.title}")
        print(f"     URL: {result.url}")
        print(f"     Snippet: {result.snippet[:100]}...")
        print()
    
    # Academic search
    print("2. Academic Search:")
    academic_results = await web_search_tool.search_academic("machine learning applications", max_results=2)
    
    for i, result in enumerate(academic_results, 1):
        print(f"  {i}. {result.title}")
        print(f"     URL: {result.url}")
        print(f"     Snippet: {result.snippet[:100]}...")
        print()
    
    # Fetch page content (mock)
    print("3. Fetch Page Content:")
    if search_results:
        content = await web_search_tool.fetch_page_content(search_results[0].url)
        if content:
            print(f"  Content preview: {content[:150]}...")
        else:
            print("  Could not fetch content")


async def file_operations_examples():
    """Demonstrate file operations tool capabilities"""
    print("\n📁 File Operations Tool Examples")
    print("=" * 50)
    
    # Create a temporary directory for examples
    temp_dir = Path("temp_examples")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # 1. Write and read text file
        print("1. Text File Operations:")
        test_file = temp_dir / "test.txt"
        content = "Hello from agent-land!\nThis is a test file for demonstrating file operations."
        
        success = await file_operations_tool.write_text_file(str(test_file), content)
        print(f"  Write success: {success}")
        
        if success:
            read_content = await file_operations_tool.read_text_file(str(test_file))
            print(f"  Read content: {read_content}")
            
            # Get file info
            file_info = file_operations_tool.get_file_info(str(test_file))
            print(f"  File info: {file_info.name}, {file_info.size} bytes, exists: {file_info.exists}")
        
        # 2. JSON file operations
        print("\n2. JSON File Operations:")
        json_file = temp_dir / "test.json"
        test_data = {
            "project": "agent-land",
            "version": "0.1.0",
            "features": ["pydantic-ai", "type-safety", "modularity"],
            "stats": {"agents": 3, "tools": 3, "examples": 3}
        }
        
        json_success = await file_operations_tool.write_json_file(str(json_file), test_data)
        print(f"  JSON write success: {json_success}")
        
        if json_success:
            json_data = await file_operations_tool.read_json_file(str(json_file))
            print(f"  JSON data: {json.dumps(json_data, indent=2)}")
        
        # 3. Directory listing
        print("\n3. Directory Listing:")
        files = await file_operations_tool.list_directory(str(temp_dir))
        print(f"  Found {len(files)} files:")
        for file_info in files:
            print(f"    - {file_info.name} ({file_info.size} bytes)")
        
    except Exception as e:
        print(f"❌ File operations error: {e}")
    
    finally:
        # Clean up
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception:
            pass


async def data_tools_examples():
    """Demonstrate data tools capabilities"""
    print("\n📊 Data Tools Examples")
    print("=" * 50)
    
    # Sample data for demonstration
    sample_data = [
        {"id": 1, "name": "Alice", "department": "Engineering", "salary": 95000, "years": 3},
        {"id": 2, "name": "Bob", "department": "Marketing", "salary": 78000, "years": 2},
        {"id": 3, "name": "Charlie", "department": "Engineering", "salary": 105000, "years": 5},
        {"id": 4, "name": "Diana", "department": "Sales", "salary": 82000, "years": 4},
        {"id": 5, "name": "Eve", "department": "Engineering", "salary": 88000, "years": 1},
        {"id": 6, "name": "Frank", "department": "Marketing", "salary": 92000, "years": 6}
    ]
    
    try:
        # 1. Load and summarize data
        print("1. Data Loading and Summary:")
        loaded_data = await data_tools.load_json_data(sample_data)
        print(f"  Loaded {len(loaded_data)} records")
        
        summary = await data_tools.summarize_data(loaded_data)
        print(f"  Summary: {summary.total_records} records, {len(summary.columns)} columns")
        print(f"  Columns: {', '.join(summary.columns)}")
        print(f"  Data types: {summary.data_types}")
        print(f"  Sample data: {summary.sample_data[0]}")
        
        # 2. Calculate column statistics
        print("\n2. Column Statistics:")
        salary_stats = await data_tools.calculate_column_stats(loaded_data, "salary")
        if salary_stats:
            print(f"  Salary statistics:")
            print(f"    Count: {salary_stats.count}")
            print(f"    Mean: ${salary_stats.mean:.2f}")
            print(f"    Median: ${salary_stats.median:.2f}")
            print(f"    Std Dev: ${salary_stats.std:.2f}")
            print(f"    Range: ${salary_stats.min:.2f} - ${salary_stats.max:.2f}")
        
        years_stats = await data_tools.calculate_column_stats(loaded_data, "years")
        if years_stats:
            print(f"  Years experience statistics:")
            print(f"    Count: {years_stats.count}")
            print(f"    Mean: {years_stats.mean:.1f} years")
            print(f"    Range: {years_stats.min} - {years_stats.max} years")
        
        # 3. Filter data
        print("\n3. Data Filtering:")
        engineering_filter = {"department": "Engineering"}
        engineering_data = await data_tools.filter_data(loaded_data, engineering_filter)
        print(f"  Engineering department: {len(engineering_data)} employees")
        for emp in engineering_data:
            print(f"    - {emp['name']}: ${emp['salary']}")
        
        # 4. Group data
        print("\n4. Data Grouping:")
        groups = await data_tools.group_data(loaded_data, "department")
        print(f"  Grouped by department: {len(groups)} groups")
        for dept, employees in groups.items():
            print(f"    {dept}: {len(employees)} employees")
        
        # 5. Aggregate data
        print("\n5. Data Aggregation:")
        avg_salary_by_dept = await data_tools.aggregate_data(loaded_data, "department", "salary", "mean")
        print(f"  Average salary by department:")
        for dept, avg_salary in avg_salary_by_dept.items():
            print(f"    {dept}: ${avg_salary:.2f}")
        
        total_years_by_dept = await data_tools.aggregate_data(loaded_data, "department", "years", "sum")
        print(f"  Total years experience by department:")
        for dept, total_years in total_years_by_dept.items():
            print(f"    {dept}: {total_years} years")
        
    except Exception as e:
        print(f"❌ Data tools error: {e}")


async def integrated_tool_workflow():
    """Demonstrate using multiple tools together in a workflow"""
    print("\n🔧 Integrated Tool Workflow")
    print("=" * 50)
    
    try:
        # Step 1: Create sample data
        workflow_data = {
            "analysis": {
                "topic": "Employee Performance Analysis",
                "date": "2024-01-15",
                "findings": [
                    "Engineering department has highest average salary",
                    "Sales team shows strong performance metrics",
                    "Marketing ROI exceeded expectations"
                ]
            },
            "recommendations": [
                "Increase engineering team budget",
                "Expand sales territories",
                "Invest more in digital marketing"
            ]
        }
        
        # Step 2: Save analysis to file
        temp_dir = Path("temp_workflow")
        temp_dir.mkdir(exist_ok=True)
        
        analysis_file = temp_dir / "analysis_results.json"
        write_success = await file_operations_tool.write_json_file(str(analysis_file), workflow_data)
        print(f"✅ Saved analysis to file: {write_success}")
        
        # Step 3: Load and process the data
        if write_success:
            loaded_data = await file_operations_tool.read_json_file(str(analysis_file))
            print(f"✅ Loaded analysis data: {loaded_data['analysis']['topic']}")
            
            # Step 4: Generate a summary report
            summary_content = f"""
# Analysis Report: {loaded_data['analysis']['topic']}

**Date:** {loaded_data['analysis']['date']}

## Key Findings:
"""
            for finding in loaded_data['analysis']['findings']:
                summary_content += f"- {finding}\n"
            
            summary_content += "\n## Recommendations:\n"
            for rec in loaded_data['recommendations']:
                summary_content += f"- {rec}\n"
            
            # Step 5: Save summary report
            report_file = temp_dir / "summary_report.md"
            report_success = await file_operations_tool.write_text_file(str(report_file), summary_content)
            print(f"✅ Generated summary report: {report_success}")
            
            # Step 6: List all generated files
            files = await file_operations_tool.list_directory(str(temp_dir))
            print(f"✅ Workflow generated {len(files)} files:")
            for file_info in files:
                print(f"  - {file_info.name} ({file_info.size} bytes)")
        
        print("\n🎉 Integrated workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Integrated workflow error: {e}")
    
    finally:
        # Clean up
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception:
            pass


async def main():
    """Run all tool examples"""
    print("🚀 Agent-Land Tool Examples")
    print("=" * 50)
    
    try:
        await web_search_examples()
        await file_operations_examples()
        await data_tools_examples()
        await integrated_tool_workflow()
        
        print("\n✅ All tool examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running tool examples: {e}")
        print(f"\n❌ Error running tool examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())