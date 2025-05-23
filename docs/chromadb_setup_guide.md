# ChromaDB Setup and Troubleshooting Guide

This documentation explains how to properly set up ChromaDB for local vector storage in the insurance chatbot RAG system, along with common issues and their solutions.

## Issue: ChromaDB "HTTP-only Client Mode" Error

When initializing ChromaDB's `PersistentClient`, you might encounter the following error:

```
RuntimeError: Chroma is running in http-only client mode, and can only be run with 'chromadb.api.fastapi.FastAPI' as the chroma_api_impl.
```

## Root Cause

This error typically occurs for one of these reasons:

1. **Package Conflict**: Having both `chromadb` and `chromadb-client` packages installed simultaneously. The client package forces ChromaDB to run in HTTP-only mode, preventing local persistence.

2. **Environment Variables**: Environment variables like `CHROMA_SERVER_HOST` being set, forcing ChromaDB into client mode.

3. **Incompatible Versions**: Using incompatible versions of ChromaDB with its dependencies (NumPy, langchain, etc.).

## Solution

The solution we implemented involved:

1. **Remove Conflicting Packages**:
   ```bash
   pip uninstall -y chromadb chromadb-client
   ```

2. **Install a Specific Compatible Version**:
   ```bash
   pip install chromadb==0.4.22
   ```

3. **Use Simple Initialization**:
   ```python
   import chromadb
   chroma_client = chromadb.PersistentClient(path=persist_directory)
   ```

## Compatibility Notes

- ChromaDB 0.4.x works well with local persistence and LangChain
- Avoid installing both `chromadb` and `chromadb-client` packages
- With newer versions of LangChain, it's recommended to use the `langchain_chroma` package

## Dependencies

Our working configuration uses these packages:

- `chromadb==0.4.22`
- `numpy==1.26.4`
- `langchain==0.3.25`
- `langchain-community==0.3.24`
- `langchain-openai==0.3.17`

## Testing

To verify your ChromaDB setup is working correctly, run the provided test scripts:

```bash
python test_chromadb_init.py  # Test basic ChromaDB functionality
python test_rag_system.py     # Test the full RAG system
```

## Warnings and Deprecation Notices

You may see deprecation warnings about:

1. The `Chroma` class from LangChain:
   ```
   LangChainDeprecationWarning: The class `Chroma` was deprecated in LangChain 0.2.9 and will be removed in 1.0.
   ```
   
   Future solution: Replace with `from langchain_chroma import Chroma`

2. The `Chain.__call__` method:
   ```
   LangChainDeprecationWarning: The method `Chain.__call__` was deprecated in langchain 0.1.0 and will be removed in 1.0.
   ```
   
   Future solution: Use `.invoke()` instead of the call syntax

These warnings can be ignored for now, but should be addressed in future updates.

## Troubleshooting

If you encounter issues:

1. Verify no ChromaDB-related environment variables are set
2. Check for package conflicts with `pip list | grep chroma`
3. Make sure your NumPy version is compatible with your dependencies
4. Use the `PersistentClient` with minimal parameters (just the path)

## Additional Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [LangChain Chroma Integration](https://python.langchain.com/docs/integrations/vectorstores/chroma)