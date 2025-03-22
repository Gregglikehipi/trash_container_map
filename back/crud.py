from sqlModels import *


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