import tempfile, os, shutil
from utils.logger import setup_logger

logger = setup_logger()

def clean(dry_run=False):
    temp = tempfile.gettempdir()
    deleted = 0
    for f in os.listdir(temp):
        try:
            path = os.path.join(temp, f)
            if os.path.isfile(path):
                if not dry_run:
                    os.remove(path)
                deleted += 1
            elif os.path.isdir(path):
                if not dry_run:
                    shutil.rmtree(path)
                deleted += 1
        except Exception as e:
            logger.error(f"Clean error {path}: {str(e)}")
    logger.info(f"Cleaned {deleted} temp items (dry_run={dry_run})")
