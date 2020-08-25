from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:manuel@localhost/telesignos'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

#-------------MODELS---------------------

class Municipio(db.Model):
    __tablename__ = 'municipios'
    __table_args__ = {"schema": "public"}

    id_municipio = db.Column(db.Integer, primary_key=True)
    nombre_municipio = db.Column(db.String(70))
    colonias = db.relationship('Colonia', backref='municipio', lazy=True)
    # hospitales = db.relationship('Hospital', backref='municipio', lazy=True)


    def __init__(self, id_municipio, nombre_municipio):
        self.id_municipio = id_municipio
        self.nombre_municipio = nombre_municipio

    def __repr__(self):
        return '<id_municipio {}>'.format(self.id_municipio)

class Colonia(db.Model):
    __tablename__ = 'colonias'
    __table_args__ = {"schema": "public"}

    id_colonia = db.Column(db.Integer, primary_key=True)
    nombre_colonia = db.Column(db.String(70))
    id_municipio = db.Column(db.Integer, db.ForeignKey('public.municipios.id_municipio'), nullable=False)
    # pacientes = db.relationship('Paciente', backref='colonia', lazy=True)


    def __init__(self, id_colonia, nombre_colonia, id_municipio):
        self.id_colonia = id_colonia
        self.nombre_colonia= nombre_colonia
        self.id_municipio = id_municipio

    def __repr__(self):
        return '<id_colonia {}>'.format(self.id_colonia) +  '<nombre: {}>'.format(self.nombre_colonia) +  '<idmunicipio: {}>'.format(self.municipio.nombre_municipio)

#----------SCHEMA------------------------

class MunicipioSchema(ma.Schema):
    class Meta:
        fields = ("id_municipio","nombre_municipio")
    

class ColoniaSchema(ma.Schema):
    class Meta:
        fields = ("id_colonia","nombre_colonia", "id_municipio")
    

municipio_schema = MunicipioSchema()
municipios_schema = MunicipioSchema(many=True)
colonia_schema = ColoniaSchema()
colonias_schema = ColoniaSchema(many=True)

#------------RESOURCES----------------

#----------municipio---------------
class MunicipiosResource(Resource):
    def get(self):
        municipios = Municipio.query.all()
        return municipios_schema.dump(municipios)
    
    #new
    def post(self):
        new_municipio = Municipio(
            id_municipio=request.json['id_municipio'],
            nombre_municipio=request.json['nombre_municipio']
        )
        db.session.add(new_municipio)
        db.session.commit()
        return municipio_schema.dump(new_municipio)

class MunicipioResource(Resource):
    def get(self, id_municipio):
        municipio = Municipio.query.get_or_404(id_municipio)
        return municipio_schema.dump(municipio)

    def patch(self, id_municipio):
        municipio = Municipio.query.get_or_404(id_municipio)

        if 'id_municipio' in request.json:
            municipio.id_municipio = request.json['id_municipio']
        if 'nombre_municipio' in request.json:
            municipio.nombre_municipio = request.json['nombre_municipio']

        db.session.commit()
        return municipio_schema.dump(municipio)
    
    def delete(self, id_municipio):
        municipio = Municipio.query.get_or_404(id_municipio)
        db.session.delete(municipio)
        db.session.commit()
        return '', 204


#-----------colonias--------------
class ColoniasResource(Resource):
    def get(self):
        colonias = Colonia.query.all()
        return colonias_schema.dump(colonias)
    
    def post(self):
        new_colonia = Colonia(
            id_colonia=request.json['id_colonia'],
            nombre_colonia=request.json['nombre_colonia'],
            id_municipio=request.json['id_municipio']
        )
        db.session.add(new_colonia)
        db.session.commit()
        return colonia_schema.dump(new_colonia)

class ColoniaResource(Resource):
    def get(self, id):
        colonia = Colonia.query.get_or_404(id)
        return colonia_schema.dump(colonia)
    
    def patch(self, id):
        colonia = Colonia.query.get_or_404(id)

        if 'id_colonia' in request.json:
            colonia.id_colonia = request.json['id_colonia']
        if 'nombre_colonia' in request.json:
            colonia.nombre_colonia = request.json['nombre_colonia']
        if 'id_municipio' in request.json:
            colonia.id_municipio = request.json['id_municipio']
        
        db.session.commit()
        return colonia_schema.dump(colonia)
    
    def delete(self, id):
        colonia = Colonia.query.get_or_404(id)
        db.session.delete(colonia)
        db.session.commit()
        return '', 204





api.add_resource(ColoniasResource, '/colonias')
api.add_resource(ColoniaResource, '/colonia/<int:id>')
api.add_resource(MunicipiosResource, '/municipios')
api.add_resource(MunicipioResource, '/municipio/<int:id_municipio>')


if __name__ == '__main__':
    app.run(debug=True)