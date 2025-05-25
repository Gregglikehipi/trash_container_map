from app.sqlModels import *
from datetime import datetime
from collections import defaultdict
from typing import List, Dict


def create_platform(session, address, longitude, latitude):
    new_platform = PlatformDB(address=address, longitude=longitude, latitude=latitude)
    session.add(new_platform)


def read_platforms(session):
    platforms = session.query(PlatformDB).all()
    return platforms



def update_platform(session, platform_id, status, change):
    platform = session.query(PlatformDB).filter_by(id=platform_id).first()

    if platform:

        platform.status = status
        platform.change = change

        session.commit()

    else:
        print(f"ID {platform_id} не найден.")


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

def set_platform_rating(
    db: Session,
    platform_id: int,
    user_token: str,
    rating: int
) -> PlatformRatingDB:
    # Ищем существующую оценку
    existing_rating = db.query(PlatformRatingDB).filter_by(
        platform_id=platform_id,
        user_token=user_token
    ).first()

    if existing_rating:
        # Обновляем существующую оценку
        existing_rating.rating = rating
        existing_rating.timestamp = int(datetime.now().timestamp())
    else:
        # Создаём новую
        existing_rating = PlatformRatingDB(
            platform_id=platform_id,
            user_token=user_token,
            rating=rating,
            timestamp=int(datetime.now().timestamp())
        )
        db.add(existing_rating)
    
    db.commit()
    db.refresh(existing_rating)
    return existing_rating

def get_user_rating(db: Session, platform_id: int, user_token: str):
    return db.query(PlatformRatingDB).filter_by(
        platform_id=platform_id,
        user_token=user_token
    ).first()

def get_average_rating(db: Session, platform_id: int):
    ratings = db.query(PlatformRatingDB).filter_by(platform_id=platform_id).all()
    if not ratings:
        return None
    return sum(r.rating for r in ratings) / len(ratings)

def get_rating_distribution(ratings: List[PlatformRatingDB]) -> Dict[int, int]:
    distribution = defaultdict(int)
    for r in ratings:
        distribution[r.rating] += 1
    return dict(distribution)