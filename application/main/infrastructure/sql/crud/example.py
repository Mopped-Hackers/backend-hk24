from urllib import response
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func, select

from .. import models
from sqlalchemy import or_, and_, union_all
from typing import List, Dict


def example(db: Session):
    grapes = db.query(models.example).all()
    return grapes
