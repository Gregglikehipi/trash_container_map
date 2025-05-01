from app.sqlModels import *


def create_platform(session, address, longitude, latitude):
    new_platform = Platform(address=address, longitude=longitude, latitude=latitude)
    session.add(new_platform)


def read_platforms(session):
    platforms = session.query(Platform).all()
    return platforms


def update_platform(session, platform_id, address=None, longitude=None, latitude=None):
    platform = session.query(Platform).filter_by(platform_id=platform_id).first()

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
    platform = session.query(Platform).filter_by(platform_id=platform_id).first()

    if platform:
        session.delete(platform)

    else:
        print(f"Пользователь с ID {platform_id} не найден.")

def create_comment(db: Session, platform_id: int, text: str):
    db_comment = PlatformCommentDB(
        platform_id=platform_id,
        text=text,
        date=int(datetime.now().timestamp())
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments(db: Session, platform_id: int):
    return db.query(PlatformCommentDB).filter(
        PlatformCommentDB.platform_id == platform_id
    ).all()