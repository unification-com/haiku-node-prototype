import logging
import os

from pathlib import Path

from sqlalchemy import create_engine

from haiku_node.db.adhoc import Base

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

appnames = ['app1', 'app2', 'app3']


def test_root() -> Path:
    return Path(os.path.dirname(os.path.abspath(__file__)))


def app_sqlite_target(app_name: str) -> Path:
    db_path = Path(test_root() / Path(
        f'data/adhoc/{app_name}.adhoc.db'))
    return db_path.resolve()


def create_dbs():
    for app in appnames:
        p = app_sqlite_target(app)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        log.info(f'Creating databases: {p.name}')
        engine = create_engine(f'sqlite:///{p}')
        Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_dbs()
