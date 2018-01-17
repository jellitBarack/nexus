from datetime import date
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Date
from alembic import op
from models import Employee


employee = Employee(email='dvd@redhat.com',
                    username='dvalleed',
                    first_name='David',
                    last_name='Vallee Delisle',
                    password='q1w2e3')
db.session.add(employee)
db.session.commit()
