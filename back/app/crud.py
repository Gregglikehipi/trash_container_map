from app.sqlModels import *
from datetime import datetime
from collections import defaultdict


def create_platform(session, address, longitude, latitude):
    new_platform = PlatformDB(address=address, longitude=longitude, latitude=latitude)
    session.add(new_platform)


def read_platforms(session):
    platforms = session.query(PlatformDB).all()
    return platforms


def update_platform(session, platform_id, address=None, longitude=None, latitude=None):
    platform = session.query(PlatformDB).filter_by(platform_id=platform_id).first()

    if platform:
        if address:
            platform.address = address
        if longitude:
            platform.longitude = longitude
        if latitude:
            platform.latitude = latitude

    else:
        print(f"Пользователь с ID {platform_id} не найден.")


def delete_platform(session, platform_id):
    platform = session.query(PlatformDB).filter_by(platform_id=platform_id).first()

    if platform:
        session.delete(platform)

    else:
        print(f"Пользователь с ID {platform_id} не найден.")

def create_comment(db: Session, platform_id: str, text: str):
    db_comment = PlatformCommentDB(
        platform_id=platform_id,
        text=text,
        date=int(datetime.now().timestamp())
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments(db: Session, platform_id: str):
    return db.query(PlatformCommentDB).filter(
        PlatformCommentDB.platform_id == platform_id
    ).all()

def filter_platforms_by_status(db: Session, status: str = None):
    query = db.query(PlatformDB)
    if status:
        query = query.filter(PlatformDB.status == status)
    return query.all()

def get_platforms_stats(db: Session):
    platforms = db.query(PlatformDB).all()
    stats = defaultdict(int)
    for platform in platforms:
        stats[platform.status] += 1
    return {
        "total": len(platforms),
        "red": stats.get("red", 0),
        "yellow": stats.get("yellow", 0),
        "green": stats.get("green", 0)
    }