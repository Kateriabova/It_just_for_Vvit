from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, SmallInteger

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine("sqlite:///imagan.db")

Base = declarative_base()

class User(Base):  # 1
    __tablename__ = 'workers'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False)
    division = Column(String(100), nullable=False)
    post = Column(String(100), nullable=False)
    salary =
    allowance =
    active = Column(Integer(), unique=False)
    is_owner = relationship('Room', back_populates="owner")
    rooms = relationship("SessionUser", back_populates="user_rel")


class Room(Base):  # 2
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    colode_id = Column(Integer, ForeignKey('colodes.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))
    count = Column(Integer, default=0)
    active = Column(Integer, nullable=False)
    users = relationship('SessionUser', back_populates="room_rel")
    rounds = relationship('Round', back_populates='rooms')
    owner = relationship('User', back_populates="is_owner")
    colode_rel = relationship('Colode', back_populates="colode_in_rooms")
    cards = relationship("CardRoom", back_populates="room")

class SessionUser(Base):  # 5
    __tablename__ = 'sessions'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id'))
    room_id = Column(Integer(), ForeignKey('rooms.id'))
    score = Column(Integer(), nullable=False)
    active = Column(Integer(), unique=False)
    user_rel = relationship("User", back_populates="rooms")
    room_rel = relationship("Room", back_populates="users")
    sessioncard = relationship('CardsNow', back_populates='sessionuser_rel')


class SessionCard(Base):
    __tablename__ = 'sessioncards'
    id = Column(Integer(), primary_key=True)
    card_id = Column(Integer(), ForeignKey('cards_in_colode.id'))
    number = Column(Integer(), nullable=False)
    active = Column(Integer(), unique=False)
    room_id = Column(Integer(), ForeignKey('rooms.id'))
    users = relationship("CardsNow", back_populates='sessioncard_rel')
    round_rel = relationship("RoundCards", back_populates="user_card_rel")
    card_rel = relationship("CardsInColode", back_populates="sessions_rel")


class Colode(Base):  # 3
    __tablename__ = 'colodes'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    colode_in_rooms = relationship('Room', back_populates="colode_rel")
    colode_of_card = relationship("CardsInColode", back_populates="colode_rel")


class CardsInColode(Base):  # 4
    __tablename__ = 'cards_in_colode'
    id = Column(Integer(), primary_key=True)
    colode_id = Column(Integer(), ForeignKey('colodes.id'))
    file = Column(String(200), nullable=False)
    sessions_rel = relationship("SessionCard", back_populates="card_rel")
    colode_rel = relationship("Colode", back_populates="colode_of_card")


class CardsNow(Base):
    __tablename__ = 'cards_now'
    id = Column(Integer(), primary_key=True)
    session_id = Column(Integer(), ForeignKey('sessions.id'))
    session_card = Column(Integer(), ForeignKey('sessioncards.id'))
    active = Column(Integer(), default=1)
    sessioncard_rel = relationship("SessionCard", back_populates='users')
    sessionuser_rel = relationship("SessionUser", back_populates='sessioncard')


class SessionUser(Base):  # 5
    __tablename__ = 'sessions'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id'))
    room_id = Column(Integer(), ForeignKey('rooms.id'))
    score = Column(Integer(), nullable=False)
    active = Column(Integer(), unique=False)
    user_rel = relationship("User", back_populates="rooms")
    room_rel = relationship("Room", back_populates="users")
    sessioncard = relationship('CardsNow', back_populates='sessionuser_rel')


class CardRoom(Base):
    __tablename__ = 'cards_in_room'
    id = Column(Integer(), primary_key=True)
    room_id = Column(Integer(), ForeignKey('rooms.id'))
    card_id = Column(Integer(), ForeignKey('cards_in_colode.id'))
    number_in_colode = Column(Integer(), nullable=False)
    room = relationship("Room", back_populates="cards")


class Round(Base):
    __tablename__ = 'round'
    id = Column(Integer(), primary_key=True)
    stage = Column(String(100), nullable=False)
    room_id = Column(Integer(), ForeignKey('rooms.id'))
    session_ved_id = Column(Integer(), ForeignKey('sessions.id'))
    session_ved_card = Column(Integer(), ForeignKey('sessioncards.id'), default=0)
    active = Column(Integer(), nullable=False)
    association = Column(String(100), default='something')
    ready_count = Column(Integer(), default=0)
    round_card = relationship("RoundCards", back_populates="round_rel")
    rooms = relationship('Room', back_populates='rounds')


class RoundCards(Base):
    __tablename__ = 'round_cards'
    id = Column(Integer(), primary_key=True)
    numb_of_votes = Column(Integer(), default=0)
    round_id = Column(Integer(), ForeignKey('round.id'))
    player = Column(Integer(), ForeignKey('sessions.id'))
    card = Column(Integer(), ForeignKey('sessioncards.id'))
    vote_card_id = Column(Integer(), default=0)
    score_for_this_round = Column(Integer(), default=0)
    user_card_rel = relationship("SessionCard", back_populates="round_rel")
    round_rel = relationship("Round", back_populates="round_card")


if __name__ == '__main__':
    Base.metadata.create_all(engine)
