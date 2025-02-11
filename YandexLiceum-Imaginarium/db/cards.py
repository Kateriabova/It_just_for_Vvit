import db.data_base_creator as data_base_creator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os


engine = create_engine("sqlite:///imagan.db")
session = Session(bind=engine)
for i in range(4):
    for j in range(12):
        if j < 10:
            j = '0' + str(j)
        path = f'dixit_0{i}_{j}.jpg'
        card = data_base_creator.CardsInColode(colode_id=1, file=path)
        session.add(card)
session.commit()

c = data_base_creator.Colode(name='best')
session.add(c)
session.commit()


