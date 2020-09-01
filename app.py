from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
import enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:manuel@localhost/telesignos'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

#-------------MODELS---------------------
class Permission: 
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class UrgenciaEnum(enum.Enum):
    EMBARAZO='embarazo'
    ACCIDENTE='accidente'
    RESPIRATORIO='respiratorio'
    OTRO='otro'

class Gravedad(enum.Enum):
    BAJA='baja'
    MEDIA='media'
    ALTA='alta'
    MUY_ALTA='muy alta'

class tipoUsuario(enum.Enum):
    PARAMEDICO='paramédico'
    MEDICO_REG='medico regulador'
    REGISTRANTE='registrante'
    ADMIN='admin'

class Municipio(db.Model):
    __tablename__ = 'municipios'
    __table_args__ = {"schema": "public"}

    id_municipio = db.Column(db.Integer, primary_key=True)
    nombre_municipio = db.Column(db.String(70))
    colonias = db.relationship('Colonia', backref='municipio', lazy=True)
    hospitales = db.relationship('Hospital', backref='municipio', lazy=True)


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
    pacientes = db.relationship('Paciente', backref='colonia', lazy=True)


    def __init__(self, id_colonia, nombre_colonia, id_municipio):
        self.id_colonia = id_colonia
        self.nombre_colonia= nombre_colonia
        self.id_municipio = id_municipio

    def __repr__(self):
        return '<id_colonia {}>'.format(self.id_colonia) +  '<nombre: {}>'.format(self.nombre_colonia) +  '<idmunicipio: {}>'.format(self.municipio.nombre_municipio)

class Hospital(db.Model):
    __tablename__ = 'hospitales'
    __table_args__ = {"schema": "public"}

    id_hospital = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_municipio = db.Column(db.Integer, db.ForeignKey('public.municipios.id_municipio'), nullable=False)
    nombre_hospital = db.Column(db.String(70))
    direccion = db.Column(db.String(70))
    telefono = db.Column(db.String(10))
    email = db.Column(db.String(70))
    movimientos = db.relationship('Movimiento', backref='hospital', lazy=True)

    def __init__(self, id_municipio, nombre_hospital, direccion, telefono, email):
        self.id_municipio = id_municipio
        self.nombre_hospital = nombre_hospital
        self.direccion = direccion
        self.telefono = telefono
        self.email = email

    def __repr__(self):
        return '<id_hospital {}>'.format(self.id_hospital)

class Servicio(db.Model):
    __tablename__ = 'servicios'
    __table_args__ = {"schema": "public"}

    id_servicio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    servicio_nombre = db.Column(db.String(10))
    contacto = db.Column(db.String(70))
    telefono = db.Column(db.String(10))
    email = db.Column(db.String(70))
    ambulancias = db.relationship('Ambulancia', backref='servicio', lazy=True)

    def __init__(self, servicio_nombre, contacto, telefono, email):
        self.servicio_nombre = servicio_nombre
        self.contacto = contacto
        self.telefono = telefono
        self.email = email

    def __repr__(self):
        return '<id {}>'.format(self.id_servicio)

class Ambulancia(db.Model):
    __tablename__ = 'ambulancias'
    __table_args__ = {"schema": "public"}

    id_ambulancia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num_unidad = db.Column(db.String(10))
    id_servicio = db.Column(db.Integer, db.ForeignKey('public.servicios.id_servicio'), nullable=False)
    movimientos = db.relationship('Movimiento', backref='ambulancia', lazy=True)


    def __init__(self, num_unidad, id_servicio):
        self.num_unidad= num_unidad
        self.id_servicio = id_servicio

    def __repr__(self):
        return '<id_ambulancia {}>'.format(self.id_ambulancia)

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    __table_args__ = {"schema": "public"}

    id_paciente = db.Column(db.Integer, primary_key = True, autoincrement=True)
    servicio_medico = db.Column(db.String(70))
    nombre_paciente = db.Column(db.String(70))
    apellidos = db.Column(db.String(100))
    genero = db.Column(db.String(1))
    fecha_nac = db.Column(db.DateTime)
    id_colonia = db.Column(db.Integer, db.ForeignKey('public.colonias.id_colonia'), nullable=False)
    movimientos = db.relationship('Movimiento', backref='paciente', lazy=True)
  
    def __init__(self, servicio_medico, nombre_paciente, apellidos, genero, fecha_nac, id_colonia):
        self.servicio_medico = servicio_medico
        self.nombre_paciente = nombre_paciente
        self.apellidos = apellidos
        self.genero = genero
        self.fecha_nac = fecha_nac
        self.id_colonia = id_colonia

    def __repr__(self):
        return '<id_paciente {}>'.format(self.id_paciente)

class Tipo_Urgencia(db.Model):
    __tablename__= 'tipo_urgencia'
    __table_args__ = {'schema': 'public'}

    id_tipo_urgencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    urgencia = db.Column(db.String(20))
    descripcion = db.Column(db.String(70))
    movimientos = db.relationship('Movimiento', backref='tipo_urgencia', lazy=True)

    def __init__(self, urgencia, descripcion):
        self.urgencia = urgencia
        self.descripcion = descripcion

    def __repr__(self):
        return '<id_tipo_urgencia {}>'.format(self.id_tipo_urgencia) + '<urgencia {}>'.format(self.urgencia)


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {"schema": "public"}

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(70), unique=True, index=True)
    id_tipo_usuario = db.Column(db.Integer, db.ForeignKey('public.tipo_usuario.id_tipo_usuario'), nullable=False)
    movimientos = db.relationship('Movimiento', backref='usuario', lazy=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return (self.id_usuario)


    def __init__(self, **kwargs): 
        super(Usuario, self).__init__(**kwargs) 
        if self.role is None:
            if self.nombre_usuario == 'manuel' or 'cirett': 
                self.role = Tipo_Usuario.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Tipo_Usuario.query.filter_by(registro=True).first()

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions 
        
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<nombre {}>'.format(self.nombre_usuario) + '<tipo: {}>'.format(self.role.tipo_usuario)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    __table_args__ = {"schema": "public"}

    id_movimiento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('public.pacientes.id_paciente'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('public.usuarios.id_usuario'))
    id_hospital = db.Column(db.Integer, db.ForeignKey('public.hospitales.id_hospital'))
    id_ambulancia = db.Column(db.Integer, db.ForeignKey('public.ambulancias.id_ambulancia'))
    id_tipo_urgencia = db.Column(db.Integer, db.ForeignKey('public.tipo_urgencia.id_tipo_urgencia'))
    fecha_inicio = db.Column(db.DateTime)
    fecha_final = db.Column(db.DateTime)
    presion_arterial = db.Column(db.String(10))
    frec_cardiaca = db.Column(db.String(10))
    frec_respiratoria = db.Column(db.String(10))
    temperatura = db.Column(db.String(2))
    escala_glassgow = db.Column(db.String(10))
    gravedad = db.Column(db.Enum(Gravedad))
    registros = db.relationship('Bitacora', backref='movimientos', lazy=True)
    

    def __init__(self, id_ambulancia, id_colonia, id_urgencia):
        self.id_ambulancia = id_ambulancia
        self.id_colonia = id_colonia
        self.id_urgencia = id_urgencia

    def __repr__(self):
        return '<id_movimiento {}>'.format(self.id_movimiento)


class Bitacora(db.Model):
    __tablename__ = 'bitacora'
    __table_args__ = {"schema": "public"}

    id_bitacora = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime)
    id_movimiento = db.Column(db.Integer, db.ForeignKey('public.movimientos.id_movimiento'))
    tipo_movimiento = db.Column(db.Integer)


    def __init__(self, id_bitacora, fecha, id_movimiento, tipo_movimiento):
        self.fecha = fecha
        self.id_movimiento = id_movimiento
        self.tipo_movimiento = tipo_movimiento
    
    def __repr__(self):
        return '<id_bitacora {}>'.format(self.id_bitacora)


#----------SCHEMA------------------------

class MunicipioSchema(ma.Schema):
    class Meta:
        fields = ("id_municipio","nombre_municipio")
    

class ColoniaSchema(ma.Schema):
    class Meta:
        fields = ("id_colonia","nombre_colonia", "id_municipio")
    
class HospitalSchema(ma.Schema):
    class Meta:
        fields = ("id_hospital", "id_municipio", "nombre_hospital", 
    "direccion", "telefono", "email")

class ServicioSchema(ma.Schema):
    class Meta:
        fields = ("id_servicio,", "servicio_nombre", "contacto", "telefono", "email")

class AmbulanciaSchema(ma.Schema):
    class Meta:
        fields = ("id_ambulancia", "num_unidad", "id_servicio")

class PacienteSchema(ma.Schema):
    class Meta:
        fields = ("id_paciente", "servicio_medico", "nombre_paciente", "apellidos", "genero", "fecha_nac", "id_colonia")

class Tipo_UrgenciaSchema(ma.Schema):
    class Meta:
        fields = ("id_tipo_urgencia," "urgencia", "descripcion")

class MovimientoSchema(ma.Schema):
    class Meta:
        fields = ("id_movimiento", "id_paciente", "id_usuario", "id_hospital", "id_ambulancia", "id_tipo_urgencia"
    "fecha_inicio", "fecha_final", "presion_arterial", "frec_cardiaca", "frec_respiratoria", "temperatura", "escala_glassgow"
    "gravedad")


municipio_schema = MunicipioSchema()
municipios_schema = MunicipioSchema(many=True)
colonia_schema = ColoniaSchema()
colonias_schema = ColoniaSchema(many=True)
hospital_schema = HospitalSchema()
hospitales_schema = HospitalSchema(many=True)
paciente_schema = PacienteSchema()
pacientes_schema = PacienteSchema(many=True)
servicio_schema = ServicioSchema()
servicios_schema = ServicioSchema(many=True)
ambulancia_schema = AmbulanciaSchema()
ambulancias_schema = AmbulanciaSchema(many=True)
tipo_urgencia_schema = Tipo_UrgenciaSchema()
tipos_urgencia_schema = Tipo_UrgenciaSchema(many=True)
movimiento_schema = MovimientoSchema()
movimientos_schema = MovimientoSchema(many=True)

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

#-----------hospitales-----------------
class HospitalesResource(Resource):
    def get(self):
        hospitales = Hospital.query.all()
        return hospitales_schema.dump(hospitales)
    
    def post(self):
        new_hospital = Hospital(
            id_municipio=request.json['id_municipio'],
            nombre_hospital=request.json['nombre_hospital'],
            direccion=request.json['direccion'],
            telefono=request.json['telefono'],
            email=request.json['email']
        )
        db.session.add(new_hospital)
        db.session.commit()
        return colonia_schema.dump(new_hospital)

class HospitalResource(Resource):
    def get(self, id):
        hospital = Hospital.query.get_or_404(id)
        return hospital_schema.dump(hospital)

    def patch(self, id):
        hospital = Hospital.query.get_or_404(id)
        if 'id_hospital' in request.json:
            hospital.id_hospital = request.json['id_hospital']
        if 'id_municipio' in request.json:
            hospital.id_municipio = request.json['id_municipio']
        if 'nombre_hospital' in request.json:
            hospital.nombre_hospital = request.json['nombre_hospital']
        if 'direccion' in request.json:
            hospital.direccion = request.json['direccion']
        if 'telefono' in request.json:
            hospital.telefono = request.json['telefono']
        if 'email' in request.json:
            hospital.email = request.json['email']
        db.session.commit()
        return hospital_schema.dump(hospital)

    def delete(self, id):
        hospital = Hospital.query.get_or_404(id)
        db.session.delete(hospital)
        db.session.commit()
        return '', 204

#------------ambulancias-----------------
class AmbulanciasResource(Resource):
    def get(self):
        ambulancias = Ambulancia.query.all()
        return ambulancias_schema.dump(ambulancias)
    
    def post(self):
        new_ambulancia = Ambulancia(
            num_unidad=request.json['num_unidad'],
            id_servicio=request.json['num_unidad']
        )
        db.session.add(new_ambulancia)
        db.session.commit()
        return ambulancia_schema.dump(new_ambulancia)

class AmbulanciaResource(Resource):
    def get(self, id):
        ambulancia = Ambulancia.query.get_or_404(id)
        return amulancia_schema.dump(ambulancia)

    def patch(self, id):
        ambulancia = Ambulancia.query.get_or_404(id)
        if 'num_unidad' in request.json:
            ambulancia.num_unidad = request.json['num_unidad']
        if 'id_servicio' in request.json:
            ambulancia.id_servicio = request.json['id_servicio']
        db.session.commit()
        return ambulancia.schema.dump(ambulancia)

    def delete(self, id):
        ambulancia = Ambulancia.query.get_or_404(id)
        db.session.delete(ambulancia)
        db.session.commit()
        return '', 204

#------------servicios--------------------
class ServiciosResource(Resource):
    def get(self):
        servicios = Servicio.query.all()
        return servicios_schema.dump(servicios)
    
    def post(self):
        new_servicio = Servicio(
            servicio_nombre=request.json['servicio_nombre'],
            contacto = request.json['contacto'],
            telefono = request.json['telefono'],
            email = request.json['email']
        )
        db.session.add(new_servicio)
        db.session.commit()
        return servicio_schema.dump(new_servicio)

class ServicioResource(Resource):
    def get(self, id):
        servicio = Servicio.query.get_or_404(id)
        return servicio_schema.dump(servicio)
    
    def patch(self, id):
        servicio = Servicio.query.get_or_404(id)
        if 'servicio_nombre' in request.json:
            servicio.servicio_nombre = request.json['servicio_nombre']
        if 'contacto' in request.json:
            servicio.contacto = request.json['contacto']
        if 'telefono' in request.json:
            servicio.telefono = request.json['telefono']
        if 'email' in request.json:
            servicio.email = request.json['email']
        db.session.commit()
        return servicio_schema.dump(servicio)
    
    def delete(self, id):
        servicio = Servicio.query.get_or_404(id)
        db.session.delete(servicio)
        db.session.commit()
        return '', 204
       
#------------pacientes--------------------
class PacientesResource(Resource):
    def get(self):
        pacientes = Paciente.query.all()
        return pacientes_schema.dump(pacientes)
    
    def post(self):
        paciente = Paciente(
            servicio_medico = request.json['servicio_medico'],
            nombre_paciente = request.json['nombre_paciente'],
            apellidos = request.json['apellidos'],
            genero = request.json['genero'],
            fecha_nac = request.json['fecha_nac'],
            id_colonia = request.json['id_colonia']
        )
        db.session.add(paciente)
        db.session.commit()
        return paciente_schema.dump(paciente)
    
class PacienteResource(Resource):
    def get(self, id):
        paciente = Paciente.query.get_or_404(id)
        return paciente_schema.dump(paciente)

    def patch(self, id):
        paciente = Paciente.query.get_or_404(id)
        if 'servicio_medico' in request.json:
            paciente.servicio_medico = request.json['servicio_medico']
        if 'nombre_paciente' in request.json:
            paciente.nombre_paciente = request.json['nombre_paciente']
        if 'apellidos' in request.json:
            paciente.apellidos = request.json['apellidos']
        if 'genero' in request.json:
            paciente.genero = request.json['genero']
        if 'fecha_nac' in request.json:
            paciente.fecha_nac = request.json['fecha_nac']
        if 'id_colonia' in request.json:
            paciente.fecha_nac = request.json['id_colonia']
        db.session.commit()
        return paciente_schema.dump(paciente)
    
    def delete(self, id):
        paciente = Paciente.query.get_or_404(id)
        db.session.delete(paciente)
        db.session.commit()
        return '', 204

#-----------movimientos--------------------

class MovimientosResource(Resource):
    def get(self):
        movimientos = Movimiento.query.all()
        return movimientos_schema.dump(movimientos)
    
    def post(self):
        movimiento = Movimiento(
            id_ambulancia=request.json['id_ambulancia'],
            id_colonia=request.json['id_colonia'],
            id_urgencia=request.json['id_urgencia']
        )
        db.session.add(movimiento)
        db.session.commit()
        return movimiento_schema.dump(movimiento)

class MovimientoResource(Resource):
    def get(self, id):
        movimiento = Movimiento.query.get_or_404(id)
        return movimiento_schema.dump(movimiento)
    
    def patch(self, id):
        movimiento = Movimiento.query.get_or_404(id)
        if 'id_paciente' in request.json:
            movimiento.id_paciente = request.json['id_paciente']
        if 'id_usuario' in request.json:
            movimiento.id_usuario = request.json['id_usuario']
        if 'id_hospital' in request.json:
            movimiento.id_hospital = request.json['id_hospital']
        if 'id_ambulancia' in request.json:
            movimiento.id_ambulancia = request.json['id_ambulancia']
        if 'id_tipo_urgencia' in request.json:
            movimiento.id_tipo_urgencia = request.json['id_tipo_urgencia']
        if 'fecha_inicio' in request.json:
            movimiento.fecha_inicio = request.json['fecha_inicio']
        if 'fecha_final' in request.json:
            movimiento.fecha_final = request.json['fecha_final']
        if 'presion_arterial' in request.json:
            movimiento.presion_arterial = request.json['presion_arterial']
        if 'frec_cardiaca' in request.json:
            movimiento.frec_cardiaca = request.json['frec_cardiaca']
        if 'frec_respiratoria' in request.json:
            movimiento.frec_respiratoria = request.json['frec_respiratoria']
        if 'temperatura' in request.json:
            movimiento.temperatura = request.json['temperatura']
        if 'escala_glassgow' in request.json:
            movimiento.escala_glassgow = request.json['escala_glassgow']
        if 'gravedad' in request.json:
            movimiento.gravedad = request.json['gravedad']
        db.session.commit()
        return movimiento_schema.dump(movimiento)

    def delete(self, id):
        movimiento = Movimiento.query.get_or_404(id)
        db.session.delete(movimiento)
        db.session.commit()
        return '', 204

#-----------tipo_urgencia-------------------

class Tipos_UrgenciaResource(Resource):
    def get(self):
        tipos_urgencia = Tipo_Urgencia.query.all()
        return tipos_urgencia_schema.dump(tipos_urgencia)
    
    def post(self):
        tipo_urgencia = Tipo_Urgencia(
            urgencia = request.json['tipo_urgencia'],
            descripcion = request.json['urgencia']
        )
        db.session.add(tipo_urgencia)
        db.session.commit()
        return tipo_urgencia_schema.dump(tipo_urgencia)

class Tipo_UrgenciaResource(Resource):
    def get(self, id):
        tipo_urgencia = Tipo_Urgencia.query.get_or_404(id)
        return tipo_urgencia_schema.dump(tipo_urgencia)
    
    def patch(self,id):
        tipo_urgencia = Tipo_Urgencia.query.get_or_404(id)
        if 'urgencia' in request.json:
            tipo_urgencia.urgencia = request.json['urgencia']
        if 'descripcion' in request.json:
            tipo_urgencia.descripcion = request.json['descripcion']
        db.session.commit()
        return tipo_urgencia_schema.dump(tipo_urgencia)
    
    def delete(self, id):
        tipo_urgencia = Tipo_Urgencia.query.get_or_404(id)
        db.session.delete(tipo_urgencia)
        db.session.commit()
        return '', 204

api.add_resource(Tipos_UrgenciaResource, '/tipos_urgencia')
api.add_resource(Tipo_UrgenciaResource, '/tipo_urgencia/<int:id>')
api.add_resource(MovimientoResource, '/movimiento/<int:id>')
api.add_resource(MovimientosResource, '/movimientos')
api.add_resource(PacientesResource, '/pacientes')
api.add_resource(PacienteResource, '/paciente/<int:id>')
api.add_resource(ServicioResource, '/servicio/<int:id>')
api.add_resource(ServiciosResource, '/servicios')
api.add_resource(AmbulanciasResource, '/ambulancias')
api.add_resource(AmbulanciaResource, '/ambulancia/<int:id>')
api.add_resource(HospitalesResource, '/hospitales')
api.add_resource(HospitalResource, '/hospital/<int:id>')
api.add_resource(ColoniasResource, '/colonias')
api.add_resource(ColoniaResource, '/colonia/<int:id>')
api.add_resource(MunicipiosResource, '/municipios')
api.add_resource(MunicipioResource, '/municipio/<int:id_municipio>')


if __name__ == '__main__':
    app.run(debug=True)