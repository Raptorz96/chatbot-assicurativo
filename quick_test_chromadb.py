#!/usr/bin/env python
"""
Quick ChromaDB Test Script

Use this script to quickly verify your ChromaDB setup is working correctly.
Run it with: python quick_test_chromadb.py

If it runs without errors, your ChromaDB setup is working.
"""
import os
import sys
import chromadb

def test_chromadb():
    print(f"Testing ChromaDB version: {chromadb.__version__}")
    print("Attempting to create a PersistentClient...")
    
    # Create a test directory
    test_dir = "./test_chroma_quick"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Create a client
        client = chromadb.PersistentClient(path=test_dir)
        print("✅ Successfully created PersistentClient")
        
        # Try to create a collection
        collection_name = "test_collection"
        
        # Check if collection exists and create it if not
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
        
        if collection_name in collection_names:
            collection = client.get_collection(name=collection_name)
            print(f"✅ Successfully retrieved existing collection '{collection_name}'")
        else:
            collection = client.create_collection(name=collection_name)
            print(f"✅ Successfully created new collection '{collection_name}'")
        
        # Add a test document
        collection.add(
            documents=["This is a test document"],
            metadatas=[{"source": "test"}],
            ids=["test1"]
        )
        print("✅ Successfully added a document to the collection")
        
        # Query the collection
        results = collection.query(
            query_texts=["test"],
            n_results=1
        )
        print("✅ Successfully queried the collection")
        print(f"Results: {results}")
        
        print("All ChromaDB tests passed successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        print(f"ChromaDB test failed. See error message above.")
        return False

if __name__ == "__main__":
    success = test_chromadb()
    sys.exit(0 if success else 1)