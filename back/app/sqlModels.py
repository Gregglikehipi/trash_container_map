from sqlalchemy import create_engine, Column, ForeignKey, Integer, Text, Float, String
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session, Mapped, mapped_column

Base = declarative_base()

class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False) -> None:
        self.engine = create_engine(url=url, echo=echo)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_db(self) -> Session:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

db_helper = DatabaseHelper(url="sqlite:///app/platforms.db", echo=False)

class PlatformDB(Base):
    __tablename__ = 'platform'

    id: Mapped[str] = mapped_column(String, primary_key=True, name="platform_id")
    address: Mapped[str] = mapped_column(Text)
    longitude: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(Text, default="green")

    comments: Mapped[list["PlatformCommentDB"]] = relationship(
        "PlatformCommentDB", 
        back_populates="platform"
    )

class PlatformCommentDB(Base):
    __tablename__ = 'platform_comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, name="comment_id")
    platform_id: Mapped[int] = mapped_column(ForeignKey('platform.platform_id'))
    text: Mapped[str] = mapped_column(Text)
    date: Mapped[int] = mapped_column(Integer) 

    platform: Mapped["PlatformDB"] = relationship(
        "PlatformDB", 
        back_populates="comments"
    )