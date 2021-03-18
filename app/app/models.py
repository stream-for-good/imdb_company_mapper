from app.main import db
import datetime
from sqlalchemy.sql import func

from app.main import db
import datetime
from sqlalchemy.sql import func

association_table = db.Table('ASSOCIATION_CC_TT', db.Model.metadata,
                             db.Column('tt_code', db.String(32), db.ForeignKey('CONTENT.id')),
                             db.Column('cc_code', db.String(32), db.ForeignKey('COMPANY.id'))
                             )


class Content(db.Model):
    __tablename__ = "CONTENT"
    id = db.Column(db.String(32), primary_key=True)
    companies = db.relationship(
        "Company",
        secondary=association_table,
        back_populates="contents")


class Company(db.Model):
    __tablename__ = "COMPANY"
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    link = db.Column(db.String(256), index=True, unique=True)
    contents = db.relationship(
        "Content",
        secondary=association_table,
        back_populates="companies")
