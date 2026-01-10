"""Test script to verify the setup is correct."""
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all required packages are installed."""
    logger.info("Testing package imports...")

    required_packages = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('langchain', 'LangChain'),
        ('plotly', 'Plotly'),
        ('reportlab', 'ReportLab'),
        ('dotenv', 'python-dotenv'),
    ]

    failed = []
    for package, name in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {name} installed")
        except ImportError:
            logger.error(f"✗ {name} NOT installed")
            failed.append(name)

    return len(failed) == 0


def test_env_file():
    """Test that .env file exists and has required variables."""
    logger.info("\nTesting environment configuration...")

    env_file = Path('.env')
    if not env_file.exists():
        logger.error("✗ .env file not found")
        logger.info("  Run: cp .env.example .env")
        return False

    logger.info("✓ .env file exists")

    # Check for API key
    with open(env_file) as f:
        content = f.read()

    if 'OPENROUTER_API_KEY=' in content:
        logger.info("✓ OPENROUTER_API_KEY found in .env")

        # Check if it's still the placeholder
        if 'your_openrouter_api_key_here' in content or 'your_actual' in content:
            logger.warning("⚠ OPENROUTER_API_KEY appears to be a placeholder")
            logger.info("  Update .env with your actual API key from https://openrouter.ai/")
            return False
        else:
            logger.info("✓ OPENROUTER_API_KEY appears to be set")
    else:
        logger.error("✗ OPENROUTER_API_KEY not found in .env")
        return False

    return True


def test_data_directory():
    """Test that data directory exists and has files."""
    logger.info("\nTesting data directory...")

    data_dir = Path('data/excel_files')

    if not data_dir.exists():
        logger.error("✗ data/excel_files directory not found")
        return False

    logger.info("✓ data/excel_files directory exists")

    # Check for data files
    csv_files = list(data_dir.glob('*.csv'))
    xlsx_files = list(data_dir.glob('*.xlsx'))
    xls_files = list(data_dir.glob('*.xls'))

    total_files = len(csv_files) + len(xlsx_files) + len(xls_files)

    if total_files == 0:
        logger.error("✗ No data files found in data/excel_files/")
        logger.info("  Add CSV or Excel files to data/excel_files/")
        return False

    logger.info(f"✓ Found {total_files} data files:")
    for f in csv_files[:5]:
        logger.info(f"  - {f.name}")
    for f in xlsx_files[:5]:
        logger.info(f"  - {f.name}")
    for f in xls_files[:5]:
        logger.info(f"  - {f.name}")

    if total_files > 5:
        logger.info(f"  ... and {total_files - 5} more")

    return True


def test_modules():
    """Test that custom modules can be imported."""
    logger.info("\nTesting custom modules...")

    modules = [
        'config',
        'data_loader',
        'database_handler',
        'llm_handler',
        'chart_generator',
        'report_generator',
        'sample_questions'
    ]

    failed = []
    for module in modules:
        try:
            __import__(module)
            logger.info(f"✓ {module}.py can be imported")
        except Exception as e:
            logger.error(f"✗ {module}.py import failed: {str(e)}")
            failed.append(module)

    return len(failed) == 0


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("NLP to SQL Application - Setup Test")
    logger.info("=" * 60)

    tests = [
        ("Package Imports", test_imports),
        ("Environment File", test_env_file),
        ("Data Directory", test_data_directory),
        ("Custom Modules", test_modules)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"\n{test_name} failed with error: {str(e)}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
        if not result:
            all_passed = False

    logger.info("=" * 60)

    if all_passed:
        logger.info("\n🎉 All tests passed! You're ready to run the application.")
        logger.info("\nStart the app with: streamlit run app.py")
        return 0
    else:
        logger.error("\n❌ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
