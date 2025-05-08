from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy with no app yet
db = SQLAlchemy()

class VisitorCount(db.Model):
    __tablename__ = 'visitor_counts'
    
    id = db.Column(db.Integer, primary_key=True)
    total_count = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def increment(cls):
        """Increment the visitor count"""
        visitor_count = cls.query.first()
        if visitor_count:
            visitor_count.total_count += 1
            visitor_count.last_updated = datetime.utcnow()
        else:
            visitor_count = cls(total_count=1)
            db.session.add(visitor_count)
        db.session.commit()
        return visitor_count.total_count
    
    @classmethod
    def get_count(cls):
        """Get the current visitor count"""
        visitor_count = cls.query.first()
        if not visitor_count:
            visitor_count = cls(total_count=0)
            db.session.add(visitor_count)
            db.session.commit()
        return visitor_count.total_count