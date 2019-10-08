from datetime import datetime
from app import db
from sqlalchemy.orm import relationship

class RussianMobilOperator(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   Operator = db.Column(db.String, nullable=False)
   Count = db.Column(db.String, nullable=False)
   Count_parse = db.Column(db.Integer, nullable=True)
   Note = db.Column(db.Text, nullable=True)

   code_zone = db.relationship('CodeZone', backref='russian_mobil_operator', lazy='dynamic')

   def ParseCount(self):
       if self.Count == None or self.Count == "":
           return self.Count_parse == 0
       pass
      
   
class CodeZone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Code = db.Column(db.Integer, nullable=False)
    ZoneText = db.Column(db.String, nullable=True)
    Count = db.Column(db.String, nullable=False)
    Count_parse = db.Column(db.Integer, nullable=True)

    RussianMobilOperator_id = db.Column(db.Integer, db.ForeignKey('russian_mobil_operator.id'))
    