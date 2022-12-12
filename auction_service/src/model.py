from datetime import datetime
from ..main import db


class Auction(db.Model):
    '''Auction class for the auction services
    '''
    __tablename__ = 'auctions'
    id = db.Column(db.Integer(), primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    item_name = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.String(255), nullable=False)
    end_time = db.Column(db.String(255), nullable=False) # 7 - 9  # BID - 8 10 -> WINNER
    max_bid_user = db.Column(db.Integer(), nullable=True)
    max_bid_amount = db.Column(db.Integer(), nullable=True, default=0)

    def __repr__(self):
        return f"<{self.id}, {self.item_name}, {self.start_time}, {self.end_time}, {self.max_bid_user}, {self.max_bid_amount}>"


class User(db.Model):
    '''User class for the user management
    '''
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    user_name = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(255), nullable= False)
    role = db.Column(db.String(255), nullable= False)

    def __repr__(self):
        return f"{self.id}"