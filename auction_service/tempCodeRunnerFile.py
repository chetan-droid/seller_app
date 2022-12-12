db = SQLAlchemy(app)


class Auction(db.Model):
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
