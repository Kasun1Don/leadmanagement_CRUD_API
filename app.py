from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields

# set alchemy meta data in Base class (define structure of DB tables)
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base) # initialize Alchemy and set instance to Base

app = Flask(__name__) # create app object and initialize Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:spameggs123@localhost:5432/crudleads'
# should create a new db user and pass for new apps
db.init_app(app) # pass database the app

ma  = Marshmallow(app) # initialize marshmallow instance to app

# Add CORS headers manually
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

#define models for Lead and Column tables according to Base Class structure

class Column(db.Model):
    __tablename__ = 'columns'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False) #basically Not Null
    leads: Mapped[list["Lead"]] = db.relationship('Lead', backref='columns', lazy=True) #lazy load

class Lead(db.Model):
    __tablename__ = 'leads'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(200))
    lead_owner: Mapped[str] = mapped_column(String(100))
    column_id: Mapped[int] = mapped_column(Integer, ForeignKey('columns.id'), nullable=False)


#set what fields are to be serialized with marshmallow, there is a more automatic way of doing this.
class LeadSchema(Schema):
    class Meta:
        fields = ('id', 'company_name', 'description', 'lead_owner', 'column_id')

class ColumnSchema(Schema):
    class Meta:
        fields = ('id', 'name', 'leads')
    
    leads = fields.List(fields.Nested(LeadSchema)) #defines nested relationship with ColumnSchema

#instaces for serializing and deserializing single or multiple Lead or Column objects
lead_schema = LeadSchema()
leads_schema = LeadSchema(many=True)
column_schema = ColumnSchema()
columns_schema = ColumnSchema(many=True)

#set API routes

# Create a column
@app.route('/column', methods=['POST'])
def add_column():
    name = request.json['name']
    new_column = Column(name=name)
    db.session.add(new_column)
    db.session.commit()
    return column_schema.dump(new_column), 201 #created status code

# Get all columns
@app.route('/columns', methods=['GET'])
def get_columns():
    columns = Column.query.all()
    return columns_schema.dump(columns)

# Get a specific column
@app.route('/column/<int:id>', methods=['GET'])
def get_column(id):
    column = Column.query.get_or_404(id)
    return column_schema.dump(column)

# Update a column
@app.route('/column/<int:id>', methods=['PUT'])
def update_column(id):
    column = Column.query.get_or_404(id)
    name = request.json['name']
    column.name = name
    db.session.commit()
    return column_schema.dump(column)

# Delete a column
@app.route('/column/<int:id>', methods=['DELETE'])
def delete_column(id):
    column = Column.query.get_or_404(id)
    db.session.delete(column)
    db.session.commit()
    return '', 204  #deleted status code

# Create a lead
@app.route('/lead', methods=['POST'])
def add_lead():
    company_name = request.json['company_name']
    description = request.get_json().get('description', '') # PUT or POST: Flask cannot auto parse JSON so need to be explicit
    lead_owner = request.get_json().get('lead_owner', '')
    column_id = request.json['column_id']
    new_lead = Lead(company_name=company_name, description=description, lead_owner=lead_owner, column_id=column_id)
    db.session.add(new_lead)
    db.session.commit()
    return lead_schema.dump(new_lead), 201

# Get all leads
@app.route('/leads', methods=['GET'])
def get_leads():
    leads = Lead.query.all()
    return leads_schema.dump(leads)

# Get a specific lead
@app.route('/lead/<int:id>', methods=['GET'])
def get_lead(id):
    lead = Lead.query.get_or_404(id)
    return lead_schema.dump(lead)

# Update a lead
@app.route('/lead/<int:id>', methods=['PUT'])
def update_lead(id):
    lead = Lead.query.get_or_404(id)
    lead.company_name = request.json['company_name']
    lead.description = request.get_json().get('description', lead.description)
    lead.lead_owner = request.get_json().get('lead_owner', lead.lead_owner)
    lead.column_id = request.json['column_id']
    db.session.commit()
    return lead_schema.dump(lead)

# Delete a lead
@app.route('/lead/<int:id>', methods=['DELETE'])
def delete_lead(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    return '', 204


#handles any error object
@app.errorhandler(404)
def not_found(err): 
    return {'error': 'Not Found'}, 404


#run the program to create the tables (write to DB) + seed the data (separation of concerns)
@app.cli.command('db_create')
def db_create():
    db.drop_all()  #you can setup migrations to preserve new POSTs instead of dropping
    db.create_all()

    # Add predefined columns data
    # Can list out the columns directly/raw input without using an iterator, this is more scalable
    columns_data = ['Lead Signals', 'Responding', 'Responded', 'Interested', 'Demo']
    columns = []

    for name in columns_data:
        column = Column(name=name)
        columns.append(column)
        db.session.add(column) 

    db.session.flush()  # sends current columns to db to Ensure column IDs are available immediately without committing all

    # Add predefined leads data
    leads = [
        Lead(company_name='Company A', description='Lead for Company A', lead_owner='Owner 1', column_id=columns[0].id),
        Lead(company_name='Company B', description='Lead for Company B', lead_owner='Owner 2', column_id=columns[0].id),
        Lead(company_name='Company C', description='Lead for Company C', lead_owner='Owner 3', column_id=columns[0].id),
        Lead(company_name='Company D', description='Lead for Company D', lead_owner='Owner 4', column_id=columns[0].id),
        Lead(company_name='Company E', description='Lead for Company E', lead_owner='Owner 5', column_id=columns[0].id),
        Lead(company_name='Company F', description='Lead for Company F', lead_owner='Owner 6', column_id=columns[1].id),
        Lead(company_name='Company G', description='Lead for Company G', lead_owner='Owner 7', column_id=columns[1].id),
        Lead(company_name='Company H', description='Lead for Company H', lead_owner='Owner 8', column_id=columns[1].id),
        Lead(company_name='Company I', description='Lead for Company I', lead_owner='Owner 9', column_id=columns[2].id),
        Lead(company_name='Company J', description='Lead for Company J', lead_owner='Owner 10', column_id=columns[3].id)
    ]

    # Add all columns and leads to the session
    db.session.add_all(leads)
    db.session.commit()
    print('Database tables created and populated!')

    # columns = ['Lead Signals', 'Responding', 'Responded', 'Interested', 'Demo']
    # for name in columns:
    #     column = Column(name=name)
    #     db.session.add(column)
        
    # db.session.commit()
    # print('Database tables created!')
if __name__ == '__main__':
    app.run()
