from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from db_Setup import *

engine = create_engine('sqlite:///games.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete GamesCompanyName if exisitng.
session.query(GameType).delete()
# Delete GameName if exisitng.
session.query(GameName).delete()
# Delete GmailUser if exisitng.
session.query(GmailUser).delete()

# Create sample users data
SampleUser = GmailUser(name="Satuluri vijayalakshmi",
                       email="s.vijaya20000@gmail.com",
                       )
session.add(SampleUser)
session.commit()
print ("Successfully Add First User")
# Create sample game names
feild1 = GameType(name="Platform Games",
                  user_id=1)
session.add(feild1)
session.commit()

feild2 = GameType(name="ShooterGames",
                  user_id=1)
session.add(feild2)
session.commit()

# Populare a Games with models for testing
# Using different users for Games names year also
item1 = GameName(name="SuperMario",
                 year="1987",
                 developer="Nintendo Creative Department",
                 publisher="Nintendo",
                 mode="Singla and multi player",
                 gameprogrammer="Toshiko Nakago,Kazuaki Tezuka ",
                 gametypeid=1,
                 gmailuser_id=1)
session.add(item1)
session.commit()
item2 = GameName(name="Wolfeinstein",
                 year="1992",
                 developer="id software",
                 publisher="Apogee software",
                 mode="single-player",
                 gameprogrammer="John Camrack,John Romero",
                 gametypeid=2,
                 gmailuser_id=1)
session.add(item2)
session.commit()
print("Your game database has been inserted!")
