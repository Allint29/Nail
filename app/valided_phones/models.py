from datetime import datetime
from app import db
from sqlalchemy.orm import relationship

class RussianMobilOperator(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   Operator = db.Column(db.String(250))
   Count = db.Column(db.String(250))
   Count_parse = db.Column(db.BigInteger)
   Note = db.Column(db.Text)

   code_zone = db.relationship('CodeZone', backref='russian_mobil_operator', lazy='dynamic')

   def ParseCount(self):
       if self.Count == None or self.Count == "":
           return self.Count_parse == 0
       pass
      
   
class CodeZone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Code = db.Column(db.Integer)
    ZoneText = db.Column(db.String(250))
    Count = db.Column(db.String(250))
    Count_parse = db.Column(db.BigInteger)

    RussianMobilOperator_id = db.Column(db.Integer, db.ForeignKey('russian_mobil_operator.id'))
    