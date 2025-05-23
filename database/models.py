
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String)
    year_founded = Column(Integer)
    is_active = Column(Boolean)
    years_active = Column(Integer)
    year_disbanded = Column(Integer)
    cagematch_id = Column(Integer, unique=True)

    # Relationships
    wrestlers = relationship("Wrestler", back_populates="promotion")
    gimmicks = relationship("Gimmick", back_populates="debut_promotion")

    def __repr__(self):
        return f"<Promotion(name='{self.name}', country='{self.country}')>"


class Wrestler(Base):
    __tablename__ = "wrestlers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"))
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    debut = Column(Date)
    age = Column(Integer)
    is_active = Column(Boolean)
    years_active = Column(Integer)
    retirement_date = Column(Date)
    cagematch_id = Column(Integer, unique=True)
    title_reigns = Column(Integer)
    titles_won = Column(Integer)
    is_champion = Column(Boolean)

    # Relationships
    promotion = relationship("Promotion", back_populates="wrestlers")
    gimmicks = relationship("Gimmick", back_populates="wrestler")

    def __repr__(self):
        return (
            f"<Wrestler(name='{self.name}', "
            f"promotion_id={self.promotion_id}, "
            f"cagematch_id={self.cagematch_id}, "
            f"age={self.age}, "
            f"is_active={self.is_active}, "
            f"years_active={self.years_active}, "
            f"retirement_date={self.retirement_date}, "
            f"height_cm={self.height_cm}, weight_kg={self.weight_kg}, "
            f"debut={self.debut}, titles_won={self.titles_won}, "
            f"title_reigns={self.title_reigns}, is_champion={self.is_champion})>"
        )


class Gimmick(Base):
    __tablename__ = "gimmicks"

    id = Column(Integer, primary_key=True)
    wrestler_id = Column(Integer, ForeignKey("wrestlers.id"))
    gimmick_name = Column(String)
    debut_promotion_id = Column(Integer, ForeignKey("promotions.id"))
    is_default = Column(Boolean)
    date_created = Column(DateTime)
    last_seen = Column(DateTime)

    # Relationships
    wrestler = relationship("Wrestler", back_populates="gimmicks")
    debut_promotion = relationship("Promotion", back_populates="gimmicks")

    def __repr__(self):
        return f"<Gimmick(name='{self.gimmick_name}', wrestler_id={self.wrestler_id})>"