#!/usr/bin/env python3
"""
Process .eml files from inbox directory.
- Imports and converts to markdown
- Optionally removes processed files and scrubs git history
- Logs success/failure
"""

import argparse
import logging
import os
import subprocess
import sys
import yaml
from pathlib import Path
from datetime import datetime

# Setup logging
def setup_logging(config):
    """Configure logging based on config settings."""
    log_config = config.get('logging', {})

    if not log_config.get('enabled', True):
        logging.disable(logging.CRITICAL)
        return

    log_file = log_config.get('file', 'logs/newsletter_processing.log')
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    level = getattr(logging, log_config.get('level', 'INFO').upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_config(config_path='config/newsletter_config.yml'):
    """Load configuration from YAML file, with environment variable overrides."""
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}

    # Apply environment variable overrides
    if os.environ.get('NEWSLETTER_INBOX_DIRECTORY'):
        config['inbox_directory'] = os.environ['NEWSLETTER_INBOX_DIRECTORY']

    if os.environ.get('NEWSLETTER_OUTPUT_DIRECTORY'):
        config['output_directory'] = os.environ['NEWSLETTER_OUTPUT_DIRECTORY']

    if os.environ.get('NEWSLETTER_SCRUB_GIT_HISTORY'):
        config['scrub_git_history'] = os.environ['NEWSLETTER_SCRUB_GIT_HISTORY'].lower() == 'true'

    # Logging overrides
    if 'logging' not in config:
        config['logging'] = {}

    if os.environ.get('NEWSLETTER_LOG_ENABLED'):
        config['logging']['enabled'] = os.environ['NEWSLETTER_LOG_ENABLED'].lower() == 'true'

    if os.environ.get('NEWSLETTER_LOG_FILE'):
        config['logging']['file'] = os.environ['NEWSLETTER_LOG_FILE']

    if os.environ.get('NEWSLETTER_LOG_LEVEL'):
        config['logging']['level'] = os.environ['NEWSLETTER_LOG_LEVEL']

    return config

def process_eml_file(eml_path, config):
    """Process a single .eml file."""
    logger = logging.getLogger(__name__)
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    import_script = os.path.join(scripts_dir, 'import_newsletter.py')

    logger.info(f"Processing: {eml_path}")

    try:
        # Build command
        cmd = [
            sys.executable,
            import_script,
            '--input', eml_path,
            '--htmlsrc'  # Use HTML cleaning
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            logger.info(f"SUCCESS: {eml_path}")
            if result.stdout:
                logger.info(result.stdout.strip())
            return True
        else:
            logger.error(f"FAILED: {eml_path}")
            if result.stderr:
                logger.error(result.stderr)
            return False

    except Exception as e:
        logger.error(f"ERROR processing {eml_path}: {str(e)}")
        return False

def cleanup_processed_file(eml_path, config):
    """Remove processed file and optionally scrub from git history."""
    logger = logging.getLogger(__name__)

    try:
        # Remove file from filesystem
        if os.path.exists(eml_path):
            os.remove(eml_path)
            logger.info(f"Removed processed file: {eml_path}")

        # Optionally scrub from git history
        if config.get('scrub_git_history', False):
            logger.info(f"Scrubbing {eml_path} from git history...")

            # Use git filter-repo to remove file from all history
            # This rewrites git history - must be done carefully
            result = subprocess.run(
                ['git', 'filter-repo', '--force', '--invert-paths', '--path', eml_path],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"Successfully scrubbed {eml_path} from git history")
            else:
                # Fallback: try BFG if filter-repo not available
                logger.warning(f"git filter-repo failed, trying BFG: {result.stderr}")
                bfg_result = subprocess.run(
                    ['bfg', '--delete-files', os.path.basename(eml_path)],
                    capture_output=True,
                    text=True
                )
                if bfg_result.returncode == 0:
                    # BFG requires gc after
                    subprocess.run(['git', 'reflog', 'expire', '--expire=now', '--all'],
                                 capture_output=True)
                    subprocess.run(['git', 'gc', '--prune=now', '--aggressive'],
                                 capture_output=True)
                    logger.info(f"Successfully scrubbed {eml_path} using BFG")
                else:
                    logger.error(f"Failed to scrub history: {bfg_result.stderr}")
        else:
            # Just remove from git tracking without history scrub
            subprocess.run(['git', 'rm', '--cached', '--ignore-unmatch', eml_path],
                         capture_output=True)

    except Exception as e:
        logger.error(f"Error during cleanup of {eml_path}: {str(e)}")

def process_inbox(config):
    """Process all .eml files in the inbox directory."""
    logger = logging.getLogger(__name__)

    inbox_dir = config.get('inbox_directory', 'inbox')

    if not os.path.exists(inbox_dir):
        logger.warning(f"Inbox directory does not exist: {inbox_dir}")
        return {'processed': 0, 'failed': 0}

    eml_files = list(Path(inbox_dir).glob('*.eml'))

    if not eml_files:
        logger.info(f"No .eml files found in {inbox_dir}")
        return {'processed': 0, 'failed': 0}

    logger.info(f"Found {len(eml_files)} .eml file(s) to process")

    processed = 0
    failed = 0

    for eml_path in eml_files:
        eml_path_str = str(eml_path)

        if process_eml_file(eml_path_str, config):
            processed += 1
            cleanup_processed_file(eml_path_str, config)
        else:
            failed += 1

    logger.info(f"Processing complete. Success: {processed}, Failed: {failed}")
    return {'processed': processed, 'failed': failed}

def main():
    parser = argparse.ArgumentParser(description='Process newsletter emails from inbox')
    parser.add_argument('--config', default='config/newsletter_config.yml',
                       help='Path to configuration file')
    parser.add_argument('--inbox', help='Override inbox directory from config')
    args = parser.parse_args()

    config = load_config(args.config)

    if args.inbox:
        config['inbox_directory'] = args.inbox

    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info(f"Starting newsletter processing at {datetime.now().isoformat()}")

    results = process_inbox(config)

    # Exit with error code if any failed
    if results['failed'] > 0:
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
