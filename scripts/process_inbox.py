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

def cleanup_processed_file(file_path, config):
    """Remove processed file from filesystem and git tracking."""
    logger = logging.getLogger(__name__)

    try:
        # Remove file from filesystem
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Removed processed file: {file_path}")

        # Remove from git tracking (history scrubbing is done in batch later)
        if not config.get('scrub_git_history', False):
            subprocess.run(['git', 'rm', '--cached', '--ignore-unmatch', file_path],
                         capture_output=True)

    except Exception as e:
        logger.error(f"Error during cleanup of {file_path}: {str(e)}")

def scrub_files_from_history(files, config):
    """Batch scrub multiple files from git history."""
    logger = logging.getLogger(__name__)

    if not files:
        return

    if not config.get('scrub_git_history', False):
        return

    logger.info(f"Scrubbing {len(files)} file(s) from git history...")

    # Build filter-repo command with all paths
    cmd = ['git', 'filter-repo', '--force', '--invert-paths']
    for file_path in files:
        cmd.extend(['--path', file_path])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        logger.info(f"Successfully scrubbed {len(files)} file(s) from git history")
    else:
        # Fallback: try BFG for each file
        logger.warning(f"git filter-repo failed, trying BFG: {result.stderr}")
        for file_path in files:
            bfg_result = subprocess.run(
                ['bfg', '--delete-files', os.path.basename(file_path)],
                capture_output=True,
                text=True
            )
            if bfg_result.returncode != 0:
                logger.error(f"Failed to scrub {file_path}: {bfg_result.stderr}")

        # BFG requires gc after all deletions
        subprocess.run(['git', 'reflog', 'expire', '--expire=now', '--all'],
                     capture_output=True)
        subprocess.run(['git', 'gc', '--prune=now', '--aggressive'],
                     capture_output=True)
        logger.info("Completed BFG cleanup")

def process_html_file(html_path, config):
    """Process a single .html file (raw HTML body, no email headers)."""
    logger = logging.getLogger(__name__)
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    import_script = os.path.join(scripts_dir, 'import_newsletter.py')

    logger.info(f"Processing: {html_path}")

    try:
        cmd = [
            sys.executable,
            import_script,
            '--input', html_path,
            '--raw-html',
            '--htmlsrc'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            logger.info(f"SUCCESS: {html_path}")
            if result.stdout:
                logger.info(result.stdout.strip())
            return True
        else:
            logger.error(f"FAILED: {html_path}")
            if result.stderr:
                logger.error(result.stderr)
            return False

    except Exception as e:
        logger.error(f"ERROR processing {html_path}: {str(e)}")
        return False

def process_inbox(config):
    """Process all .eml and .html files in inbox and import directories."""
    logger = logging.getLogger(__name__)

    inbox_dir = config.get('inbox_directory', 'inbox')
    import_dir = config.get('import_directory', 'import')

    processed = 0
    failed = 0
    processed_files = []  # Track files for batch history scrubbing

    # Process .eml files from inbox
    if os.path.exists(inbox_dir):
        eml_files = list(Path(inbox_dir).glob('*.eml'))
        if eml_files:
            logger.info(f"Found {len(eml_files)} .eml file(s) in {inbox_dir}")
            for eml_path in eml_files:
                eml_path_str = str(eml_path)
                if process_eml_file(eml_path_str, config):
                    processed += 1
                    processed_files.append(eml_path_str)
                    cleanup_processed_file(eml_path_str, config)
                else:
                    failed += 1

    # Process .html files from import
    if os.path.exists(import_dir):
        html_files = list(Path(import_dir).glob('*.html'))
        if html_files:
            logger.info(f"Found {len(html_files)} .html file(s) in {import_dir}")
            for html_path in html_files:
                html_path_str = str(html_path)
                if process_html_file(html_path_str, config):
                    processed += 1
                    processed_files.append(html_path_str)
                    cleanup_processed_file(html_path_str, config)
                else:
                    failed += 1

    # Batch scrub all processed files from history (if enabled)
    if processed_files:
        scrub_files_from_history(processed_files, config)

    if processed == 0 and failed == 0:
        logger.info("No files found to process")

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
