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

def create_comment(session, platform_id: int, text: str, date: int = None):
    platform = session.query(Platform).filter_by(platform_id=platform_id).first()
    if not platform:
        raise ValueError(f"Платформа с ID {platform_id} не найдена")

    new_comment = PlatformComment(
        platform_id=platform_id,
        text=text,
        date=int(time.time())
    )
    session.add(new_comment)
    return new_comment

def read_comments(session, platform_id: int):
    return session.query(PlatformComment).filter_by(platform_id=platform_id).all()

def read_comment(session, comment_id: int):
    return session.query(PlatformComment).filter_by(comment_id=comment_id).first()

def update_comment(session, comment_id: int, new_text: str):
    comment = session.query(PlatformComment).filter_by(comment_id=comment_id).first()
    if comment:
        comment.text = new_text
        comment.date = int(time.time())
    else:
        raise ValueError(f"Комментарий с ID {comment_id} не найден")
    return comment

def delete_comment(session, comment_id: int):
    comment = session.query(PlatformComment).filter_by(comment_id=comment_id).first()
    if comment:
        session.delete(comment)
    else:
        raise ValueError(f"Комментарий с ID {comment_id} не найден")
    return True