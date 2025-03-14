from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer, Table, Text, create_engine
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship, sessionmaker
from sqlalchemy.orm.base import Mapped

Base = declarative_base()
metadata = Base.metadata

class DatabaseHelper:
    def __init__(self, url: str, echo: bool) -> None:
        self.engine = create_engine(url=url, echo=echo)
        self.session_make = sessionmaker(
            bind=self.engine
        )

    def get_db(self):
        with self.session_make() as session:
            try:
                yield session  # Provide the session to the caller
                session.commit()  # Commit if everything goes well
            except Exception as e:
                session.rollback()  # Rollback if an exception occurs
                raise e


db_helper = DatabaseHelper(url="sqlite:///platforms.db", echo=False)


class Platform(Base):
    __tablename__ = 'platform'

    platform_id = mapped_column(Integer, primary_key=True)
    address = mapped_column(Text)
    longitude = mapped_column(Integer)
    latitude = mapped_column(Text)

    platform_comment: Mapped['PlatformComment'] = relationship('PlatformComment', back_populates='platform')


class PlatformComment(Base):
    __tablename__ = 'platform_comment'

    comment_id = mapped_column(Integer, primary_key=True)
    platform_id = mapped_column(ForeignKey('platform.platform_id'))
    text = mapped_column(Text)
    date = mapped_column(Integer)

    platform: Mapped['Platform'] = relationship('Platform', back_populates='platform_comment')
