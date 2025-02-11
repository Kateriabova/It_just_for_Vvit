import random

import db.data_base_creator as data_base_creator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os


class DataBaseManager():
    name = os.path.join('db', 'imagan.db')
    engine = create_engine(f"sqlite:///{name}")
    session = Session(bind=engine)

    @staticmethod
    def add_user(name):
        user_1 = data_base_creator.User(name=name)
        DataBaseManager.session.add(user_1)
        DataBaseManager.session.commit()
        return user_1.id

    @staticmethod
    def room_info():
        a = DataBaseManager.session.query(dat.Room).all()
        jsonchik = {}
        for i in a:
            count =
            count = count.filter(data_base_creator.SessionUser.active == 1).count()
            # надо будет переписать когда relationship будут
            print(i.colode_rel.name, i.owner.name)
            dic = {'colode': i.colode_rel.name, 'owner': i.owner.name, 'count': i.count, 'active': i.active,
                   'quantity': count}
            jsonchik[i.id] = dic
        return jsonchik

    @staticmethod
    def players_by_room_id(room_id):
        players_id = DataBaseManager.session.query(data_base_creator.SessionUser).filter(
            data_base_creator.SessionUser.room_id == room_id)
        players_id = players_id.filter(data_base_creator.SessionUser.active == 1)
        jsonchik = {}
        for player in players_id:
            jsonchik[player.id] = {'name': player.user_rel.name, 'score': player.score}
        return jsonchik

    @staticmethod
    def colode_names():
        colodes = DataBaseManager.session.query(data_base_creator.Colode).all()
        jsonchik = {}
        for i in colodes:
            jsonchik[i.id] = {'name': i.name}
        print(jsonchik)
        return jsonchik

    @staticmethod
    def create_room_with_owner(owner_id):
        new_group = data_base_creator.Room(colode_id=1, owner_id=owner_id, active=1, count=0)
        DataBaseManager.session.add(new_group)
        DataBaseManager.session.commit()
        room_id = new_group.id
        session_id = DataBaseManager.add_user_to_room(room_id, owner_id)
        DataBaseManager.session.commit()
        return room_id, session_id

    @staticmethod
    def add_user_to_room(room_id, user_id):
        print(f"user: {user_id}", f"room: {room_id}")
        user = DataBaseManager.session.query(data_base_creator.User).get(user_id)
        room = DataBaseManager.session.query(data_base_creator.Room).get(room_id)
        count = DataBaseManager.session.query(data_base_creator.SessionUser).filter(
            data_base_creator.SessionUser.room_id == room_id)
        count = count.filter(data_base_creator.SessionUser.active == 1).count()
        if count < 6:
            session = data_base_creator.SessionUser(score=0, active=1)
            session.room_rel = room
            user.rooms.append(session)
            DataBaseManager.session.commit()
            return session.id
        else:
            print("6 users in this room(((")
            return False

    @staticmethod
    def change_colode_in_room_by_room_id(room_id, colode_id):
        room = DataBaseManager.session.query(data_base_creator.Room).get(room_id)
        colode = DataBaseManager.session.query(data_base_creator.Colode).get(colode_id)
        room.game_colode = colode
        DataBaseManager.session.commit()

    @staticmethod
    def get_game_status(room_id, user_id):
        room = DataBaseManager.session.query(data_base_creator.Room).get(room_id)
        if room.active != 2:
            return False
        session = DataBaseManager.session.query(data_base_creator.SessionUser).filter(
            data_base_creator.SessionUser.room_id == room_id).filter(data_base_creator.SessionUser.user_id == user_id)
        cards = list(filter(lambda x: x.active == 1, session[0].sessioncard))
        a = []
        for i in cards:
            a.append(i.id)
        return a

    @staticmethod
    def get_user_name_by_id(user_id):
        user = DataBaseManager.session.query(data_base_creator.User).get(user_id)
        return user.name

    @staticmethod
    def get_img_path_by_card_id(card_id):
        card = DataBaseManager.session.query(data_base_creator.SessionCard).get(card_id)
        return card.card_rel.file

    @staticmethod
    def start_game(room_id):
        room = DataBaseManager.session.query(data_base_creator.Room).get(room_id)
        if room.active == 0:
            return False
        room.active = 2
        DataBaseManager.session.commit()
        colode_id = room.colode_id
        colode = DataBaseManager.session.query(data_base_creator.CardsInColode).filter(
            data_base_creator.CardsInColode.colode_id == colode_id)
        new_colode = [i for i in colode]
        random.shuffle(new_colode)
        number_card = room.count
        print(number_card, 505)
        for i in range(len(new_colode)):
            print(room_id, new_colode[number_card], number_card)
            card = data_base_creator.CardRoom(room_id=room_id, card_id=new_colode[number_card].id,
                                              number_in_colode=number_card)
            number_card += 1
            DataBaseManager.session.add(card)
        DataBaseManager.session.commit()
        players = DataBaseManager.session.query(data_base_creator.SessionUser).filter(
            data_base_creator.SessionUser.room_id == room_id)
        players = [i for i in players]
        count = 0
        for i in range(len(players)):
            s_c_1 = data_base_creator.SessionCard(card_id=colode[i + count].id, number=i + count, room_id=room_id, active=1)
            count += 1
            s_c_2 = data_base_creator.SessionCard(card_id=colode[i + count].id, number=i + count, room_id=room_id, active=1)
            count += 1
            s_c_3 = data_base_creator.SessionCard(card_id=colode[i + count].id, number=i + count, room_id=room_id, active=1)
            count += 1
            s_c_4 = data_base_creator.SessionCard(card_id=colode[i + count].id, number=i + count, room_id=room_id, active=1)
            DataBaseManager.session.add_all([s_c_1, s_c_2, s_c_3, s_c_4])
        DataBaseManager.session.commit()
        qu = DataBaseManager.session.query(data_base_creator.SessionCard).filter(
            data_base_creator.SessionCard.room_id == room_id)
        count = 0
        for i in range(len(players)):
            c_n = data_base_creator.CardsNow(session_id=players[i].id, session_card=qu[i + count].id)
            count += 1
            DataBaseManager.session.add(c_n)
            c_n = data_base_creator.CardsNow(session_id=players[i].id, session_card=qu[i + count].id)
            count += 1
            DataBaseManager.session.add(c_n)
            c_n = data_base_creator.CardsNow(session_id=players[i].id, session_card=qu[i + count].id)
            count += 1
            DataBaseManager.session.add(c_n)
            c_n = data_base_creator.CardsNow(session_id=players[i].id, session_card=qu[i + count].id)
            DataBaseManager.session.add(c_n)

        DataBaseManager.session.commit()

    @staticmethod
    def give_card_to_user(user_id, room_id):
        room = DataBaseManager.session.query(data_base_creator.Room).get(room_id)
        number_card = room.count + 1
        card_room = DataBaseManager.session.query(data_base_creator.CardRoom).filter(
            data_base_creator.CardRoom.room_id == room_id and
            data_base_creator.CardRoom.number_in_colode == number_card)[0]
        path = DataBaseManager.session.query(data_base_creator.CardsInColode).filter(
            data_base_creator.CardsInColode.id == card_room.card_id)[0].file
        room.count = number_card
        card = data_base_creator.SessionCard(card_id = card_room.card_id, number = number_card, active=1, room_id=room_id)
        DataBaseManager.session.add(card)
        DataBaseManager.session.commit()
        session_card = DataBaseManager.session.query(data_base_creator.SessionCard).filter(
            data_base_creator.SessionCard.room_id == room_id and
            data_base_creator.SessionCard.card_id == card_room.card_id)[0]
        session_user = DataBaseManager.session.query(data_base_creator.SessionUser).filter(
            data_base_creator.SessionUser.room_id == room_id and
            data_base_creator.SessionUser.user_id == user_id)[0]
        c_n = data_base_creator.CardsNow(session_id=session_user.id, session_card=session_card.id)
        DataBaseManager.session.add(c_n)
        DataBaseManager.session.commit()

        return (card_room.card_id, path)

    '''@staticmethod
    def get_played_cards(room_id):
        room = DataBaseManager.session.query(data_base_creator.Room).get(room_id)
        number_card = room.count + 1
        card_room = DataBaseManager.session.query(data_base_creator.CardRoom).filter(
            data_base_creator.CardRoom.room_id == room_id and
            data_base_creator.CardRoom.number_in_colode == number_card)
        path = DataBaseManager.session.query(data_base_creator.CardsInColode).filter(
            data_base_creator.CardsInColode.id == card_room.card_id).file
        room.count = number_card
        DataBaseManager.session.commit()
        return (card_room.card_id, path)'''

    @staticmethod
    def get_round(room_id):
        room = DataBaseManager.session.query(data_base_creator.Room).get(room_id)
        round = list(filter(lambda x: x.active == 1, room.rounds))[0]
        return round.id

    @staticmethod
    def get_gm(round_id):
        round = DataBaseManager.session.query(data_base_creator.Round).get(round_id)
        return round.session_ved_id

    @staticmethod
    def get_round_status(round_id):
        round = DataBaseManager.session.query(data_base_creator.Round).get(round_id)
        return round.stage

    @staticmethod
    def get_association_by_round_id(round_id):
        round = DataBaseManager.session.query(data_base_creator.Round).get(round_id)
        return round.association

    @staticmethod
    def get_played_cards(round_id):
        rounds = DataBaseManager.session.query(data_base_creator.RoundCards).filter(
            data_base_creator.RoundCards.round_id == round_id)
        if rounds:
            print('werty')
        print(rounds.__class__.__name__, 444)
        rounds.__iter__()
        a = [i.card for i in rounds]
        room_id = DataBaseManager.session.query(data_base_creator.Round).get(round_id).room_id
        count = DataBaseManager.session.query(data_base_creator.SessionUser).filter(
            data_base_creator.SessionUser.room_id == room_id)
        count = count.filter(data_base_creator.SessionUser.active == 1).count()
        if len(a) == count:
            return (a, 'ok')
        return (a, False)

    @staticmethod
    def get_ready_count_and_add(room_id, add=True):
        room = DataBaseManager.session.query(data_base_creator.Room).get(room_id)
        thing = list(filter(lambda x: x.active == 1, room.rounds))[0]
        if add:
            thing.ready_count += 1
        qu = thing.ready_count
        DataBaseManager.session.commit()
        return qu

    @staticmethod
    def get_q_of_players(room_id):
        count = DataBaseManager.session.query(data_base_creator.SessionUser).filter(
            data_base_creator.SessionUser.room_id == room_id)
        count = count.filter(data_base_creator.SessionUser.active == 1).count()
        return count

    @staticmethod
    def add_association(association, card_id, round_id):
        round = DataBaseManager.session.query(data_base_creator.Round).get(round_id)
        round.acssociaton = association
        round.session_ved_card = card_id
        DataBaseManager.session.commit()

    @staticmethod
    def play_card_by_round_id(card_id, session_id, round_id):
        r_c = data_base_creator.RoundCards(round_id=round_id, player=session_id, card=card_id)
        DataBaseManager.session.add(r_c)
        DataBaseManager.session.commit()

        qu = DataBaseManager.session.query(data_base_creator.RoundCards).filter(
            data_base_creator.RoundCards.round_id == round_id)
        count = qu.count()
        room = DataBaseManager.session.query(data_base_creator.SessionUser).get(session_id).room_id
        count_2 = DataBaseManager.session.query(data_base_creator.SessionUser).filter(
            data_base_creator.SessionUser.room_id == room).count()
        if count == count_2:
            ro = DataBaseManager.session.query(data_base_creator.Round).get(round_id)
            ro.stage = 'vouting'
        DataBaseManager.session.commit()

    @staticmethod
    def add_round(room_id):
        room = DataBaseManager.session.query(data_base_creator.Room).get(room_id)
        rounds = room.rounds
        rounds = len([i for i in rounds])
        users = room.users
        users = [i for i in users]
        ved = users[rounds % len(users)].id
        session_id = DataBaseManager.session.query(data_base_creator.SessionUser
                                                   ).filter(data_base_creator.SessionUser.room_id == room_id
                                                            and data_base_creator.SessionUser.user_id == ved)[0].id
        round = data_base_creator.Round(stage='association', active=1, room_id=room_id, session_ved_id= session_id)
        DataBaseManager.session.add(round)
        DataBaseManager.session.commit()

    @staticmethod
    def get_users_cards(session_id):
        session = DataBaseManager.session.query(data_base_creator.SessionUser).get(session_id)
        cards = session.sessioncard
        cards = [i.sessioncard_rel for i in cards]
        card = []
        for i in cards:
            card.append(i.card_id)
        return card

    @staticmethod
    def get_user_name_by_session(session_id):
        session = DataBaseManager.session.query(data_base_creator.SessionUser).get(session_id)
        return session.user_rel.name

    @staticmethod
    def add_voute(card_id, round_id, session_id):
        round = DataBaseManager.session.query(data_base_creator.Round).get(round_id)
        roundcard = DataBaseManager.session.query(data_base_creator.RoundCards
                                                   ).filter(data_base_creator.RoundCards.round_id == round_id
                                                            and data_base_creator.RoundCards.card == card_id)[0]
        rounduser = DataBaseManager.session.query(data_base_creator.RoundCards
                                                   ).filter(data_base_creator.RoundCards.round_id == round_id
                                                            and data_base_creator.RoundCards.player == session_id)[0]
        roundcard.numb_of_votes = roundcard.numb_of_votes + 1
        rounduser.vote_card_id = card_id
        if card_id == round. session_ved_card:
            rounduser.score_for_this_round += 3
            roundcard.score_for_this_round += 1
        DataBaseManager.session.commit()

'''тогда в add_vote
если голос за правильную карту то этот юзер и ведущий получают баллы
если за чужую то + балл владельцу

1 Если карточку ведущего угадали все игроки, то он идет на 3 хода назад, а остальные стоят на месте.
 2 Если карточку ведущего никто не угадал, то ведущий идет на 2 хода назад. Плюс очки получают игроки, чьи карточки угадали.
 3 В любом другом случае по 3 очка получают все игроки, правильно угадавшие карточку. Ведущий получает 3 очка плюс по очку за каждого угадавшего его игрока. Все игроки получают по одному очку за каждого игрока, который угадал их картинку.
'''