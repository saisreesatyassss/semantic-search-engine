"""
Quick deployment test script
Run this before deploying to Streamlit Cloud
"""
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing package imports...")
    
    try:
        import streamlit
        print("✓ streamlit")
    except ImportError as e:
        print(f"✗ streamlit: {e}")
        return False
    
    try:
        import sentence_transformers
        print("✓ sentence-transformers")
    except ImportError as e:
        print(f"✗ sentence-transformers: {e}")
        return False
    
    try:
        import faiss
        print("✓ faiss-cpu")
    except ImportError as e:
        print(f"✗ faiss-cpu: {e}")
        return False
    
    try:
        import pandas
        print("✓ pandas")
        import numpy
        print("✓ numpy")
        import sklearn
        print("✓ scikit-learn")
        import yaml
        print("✓ pyyaml")
    except ImportError as e:
        print(f"✗ Core packages: {e}")
        return False
    
    print("\n✅ All required packages installed!\n")
    return True


def test_file_structure():
    """Verify required files exist."""
    print("Checking file structure...")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "config.yaml",
        ".streamlit/config.toml",
        "web_app/app.py",
        "search_engine/semantic_search.py",
        "vector_database/faiss.index",
        "data/processed/metadata.pkl",
        "data/processed/embeddings.npy"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} NOT FOUND")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {len(missing_files)}")
        for f in missing_files:
            print(f"  - {f}")
        return False
    else:
        print("\n✅ All required files present!\n")
        return True


def test_file_sizes():
    """Check if data files are within acceptable size limits."""
    print("Checking file sizes...")
    
    size_limits = {
        "vector_database/faiss.index": 100,  # MB
        "data/processed/embeddings.npy": 100,
        "data/processed/metadata.pkl": 10
    }
    
    issues = []
    for file_path, max_size_mb in size_limits.items():
        path = Path(file_path)
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            status = "✓" if size_mb < max_size_mb else "⚠"
            print(f"{status} {file_path}: {size_mb:.2f} MB (limit: {max_size_mb} MB)")
            
            if size_mb > max_size_mb:
                issues.append(f"{file_path} is too large ({size_mb:.2f} MB)")
    
    if issues:
        print("\n⚠️  File size warnings:")
        for issue in issues:
            print(f"  - {issue}")
        print()
    else:
        print("\n✅ File sizes are within limits!\n")
    
    return len(issues) == 0


def test_search_engine():
    """Test if search engine can be initialized."""
    print("Testing search engine initialization...")
    
    try:
        from search_engine.semantic_search import SemanticSearchEngine
        
        print("  Loading search engine...")
        engine = SemanticSearchEngine()
        
        print("  Initializing components...")
        engine.initialize()
        
        stats = engine.get_statistics()
        print(f"✓ Search engine initialized")
        print(f"  - Documents: {stats.get('n_documents', 0):,}")
        print(f"  - Model: {stats.get('model_name', 'Unknown')}")
        print(f"  - Embedding dim: {stats.get('embedding_dimension', 0)}")
        
        # Test a simple search
        print("\n  Testing search query...")
        results = engine.search("test query", top_k=3)
        print(f"✓ Search returned {len(results)} results")
        
        if results:
            print(f"  - Top result score: {results[0].get('similarity_score', 0):.4f}")
        
        print("\n✅ Search engine working correctly!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Search engine test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all deployment tests."""
    print("="*60)
    print("STREAMLIT CLOUD DEPLOYMENT PRE-CHECK")
    print("="*60)
    print()
    
    tests = [
        ("Package Imports", test_imports),
        ("File Structure", test_file_structure),
        ("File Sizes", test_file_sizes),
        ("Search Engine", test_search_engine)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}\n")
            results.append((test_name, False))
    
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready for deployment!")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Ready for Streamlit Cloud'")
        print("3. git push origin main")
        print("4. Deploy on share.streamlit.io")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
