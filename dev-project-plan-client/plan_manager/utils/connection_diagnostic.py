# Connection Diagnostic Utility

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_diagnostic():
    """Run comprehensive connection diagnostic"""
    print("=== Plan Manager Connection Diagnostic ===\n")
    
    # 1. Check database connection
    print("1. Testing database connection...")
    try:
        from database.connection import test_connection
        success, message = test_connection()
        if success:
            print(f"   ✅ Database: {message}")
        else:
            print(f"   ❌ Database: {message}")
    except Exception as e:
        print(f"   ❌ Database: Import error - {e}")
    
    # 2. Check configuration
    print("\n2. Checking configuration...")
    try:
        from config import ConfigManager
        config = ConfigManager()
        db_config = config.get_database_config()
        print(f"   📊 DB Host: {db_config['db_host']}:{db_config['db_port']}")
        print(f"   📊 DB Name: {db_config['db_name']}")
        print(f"   📊 DB User: {db_config['db_user']}")
    except Exception as e:
        print(f"   ❌ Config: Error reading configuration - {e}")
    
    # 3. Check gRPC dependencies
    print("\n3. Checking gRPC dependencies...")
    try:
        import grpc
        print(f"   ✅ gRPC: {grpc.__version__}")
    except ImportError:
        print("   ❌ gRPC: Not installed (pip install grpcio)")
    
    try:
        import grpc_tools
        print(f"   ✅ gRPC Tools: Available")
    except ImportError:
        print("   ❌ gRPC Tools: Not installed (pip install grpcio-tools)")
    
    # 4. Check protobuf files
    print("\n4. Checking protobuf files...")
    try:
        from grpc_client import helper_pb2, helper_pb2_grpc
        print("   ✅ Protobuf: Generated files found")
    except ImportError as e:
        print(f"   ❌ Protobuf: {e}")
        print("      Run: python -m utils.grpc_test to test server connection")
    
    # 5. Test default gRPC server
    print("\n5. Testing default gRPC server...")
    try:
        from utils.grpc_test import test_grpc_server
        if test_grpc_server("192.168.120.238:50051"):
            print("   ✅ Default server: Reachable")
        else:
            print("   ❌ Default server: Not reachable")
    except Exception as e:
        print(f"   ❌ Default server: Test failed - {e}")
    
    print("\n=== Diagnostic Complete ===")
    print("\nIf you see any ❌ above, please address those issues before using the application.")

if __name__ == "__main__":
    run_diagnostic()