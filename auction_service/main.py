import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# from src.service import get_active_auctions_service
# from src.model import Auction, User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # local DB instance

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

    def __repr__(self):
        return f"<{self.id}, {self.item_name}, {self.start_time}, {self.end_time}, {self.max_bid_user}, {self.max_bid_amount}>"



class User(db.Model):
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


with app.app_context():
    # TO CREATE TABLES IN DATABASE
    db.create_all()
    
    # Auction Management
    @app.route("/active_auctions")
    def get_active_auctions():
        auctions = Auction.query.all()
        try:
            result = []
            for auction in auctions:
                if auction.end_time < str(datetime.utcnow()):
                    continue
                auction_data = auction.__dict__
                auction_data.pop('_sa_instance_state') 
                result.append(auction_data)
                # return get_active_auctions_service()
            return result
        except Exception as err:
            return {"error": str(err)}

    '''We can access all the auctions which is created by the admin'''
    @app.route("/all_auctions")
    def get_all_auctions():
        try:
            token_email = request.headers.get('token')
            current_user = User.query.filter_by(user_email=token_email).first()

            if current_user and current_user.role != 'admin':
                return {"error": "Only Admin can access this API"}

            auctions = Auction.query.all()

            result = []
            for auction in auctions:
                auction_data = auction.__dict__
                auction_data.pop('_sa_instance_state') 
                result.append(auction_data)

            return {"data": result, "status_code":201}
        except Exception as err:
            return {"error": str(err)}


    '''We can check the auction status here which is 
    Access the auction status followed by auction id.
    '''
    @app.route("/auction_status_by_id/", methods=['GET'])
    def auction_status():
        try:
            auction_id = request.args.get('auction_id')
            current_auction = Auction.query.get_or_404(auction_id)

            print(current_auction.end_time)
            print(str(datetime.utcnow()))
            if current_auction.end_time < str(datetime.utcnow()):
                return {"status": f"Auction is CLOSED, winner is {current_auction.max_bid_user}"}
            else:
                return {"status": f"Auction is OPEN, current maximum bid is {current_auction.max_bid_amount}"}
        except Exception as err:
            return {"error" : str(err)}


    # CREATE AUCTION HERE

    @app.route("/auction", methods=["POST"])
    def create_auction():
        # input data
        data = request.get_json()

        # Auction Object - initiate
        new_auction = Auction()
        # Auction Object - parameter value
        new_auction.item_name = data.get("item_name")
        new_auction.start_time = data.get("start_time")
        new_auction.end_time = data.get("end_time")

        # save auction to DB
        db.session.add(new_auction)
        db.session.commit()

        print(new_auction)
        new_auction_data = new_auction.__dict__
        new_auction_data.pop('_sa_instance_state')

        return {"data": new_auction_data}


    @app.route("/auction_update", methods=["PATCH"])
    def update_auction():
        """User bid amount & user_id & auction_id"""
        data = request.get_json()

        attrs = ('year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond')
        
        auction_id = data.get('auction_id')
        user_id = data.get('user_id')
        bid_amount = data.get('bid_amount')

        current_auction = Auction.query.get_or_404(auction_id)
        current_time = datetime.utcnow
        start_time = datetime.strptime(current_auction.start_time, "%Y-%m-%d %H:%M:%S.%f")
        end_time = datetime.strptime(current_auction.end_time, "%Y-%m-%d %H:%M:%S.%f")
       
        if (current_time) >= (start_time) and (current_time) <= (end_time):

            # check bid amount with max auction amount:
            if bid_amount > int(current_auction.max_bid_amount):
                current_auction.max_bid_amount = bid_amount
                current_auction.max_bid_user = user_id

                # save in DB
                db.session.add(current_auction)
                db.session.commit()

                return {"message": f"Congrats, your bid amount {current_auction.max_bid_amount} is maximum for this Auction"}
            else:
                return {"message": f"Your bid amount is low. Current max bid amount is {current_auction.max_bid_amount} and bid by user_id: {current_auction.max_bid_user}"}

        elif current_time < current_auction.start_time:
            return {"error": "Auction has not started yet."}
        else:
            return {"error": f"Bid time is closed for auction id {auction_id}"}

    """Delete the auction using auction id"""
    @app.route("/auction/<auction_id>", methods=["DELETE"])
    def delete_auction(auction_id):
        try:
            auction = Auction.query.get_or_404(auction_id)
            
            db.session.delete(auction)
            db.session.commit()

            auction_data = auction.__dict__
            return {"message":"Successfully delete auction", "data": 'auction_data'}
        except Exception as err:
            return {"error" : str(err)}

    # User Management
    @app.route("/user", methods=['POST'])
    def create_user():
        try:
            data = request.get_json()

            user = User()
            user.role = data.get('role')
            user.user_email = data.get('user_email')
            user.user_name = data.get('user_name')

            db.session.add(user)
            db.session.commit()

            return {"message": "Successfully create user"}
        except Exception as err:
            return {"error": str(err)}

    @app.route("/all_user")
    def get_all_users():
        try:
            users = User.query.all()
            result = []
            for user in users:
                user_data = user.__dict__
                user_data.pop('_sa_instance_state') 
                result.append(user_data)

            return {"data": result}
        except Exception as err:
            return {"error": str(err)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

