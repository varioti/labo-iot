from app import db
from datetime import datetime

db.drop_all()
db.create_all()


class AdvicesConsumption(db.Model):
    """

    """
    __tablename__ = "adviceConsumption"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_d = db.Column(db.String(150), nullable=False)
    advice = db.Column(db.Text, nullable=False)
    device = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return "TYPE:  %s, \n ADVICE: %s \n DEVICE: %s\n\n" % (self.type, self.advice, self.device)

    def add_new_advice(type_d, advice, device):
        """
        Add a new advice on energy consumption

        :parameter
        type: type of the advice (reduce consumption, new purchase of appliances, tip) (string)
        advice: the advice (string)
        device: kitchen device (fridge, bulb, oven, microwave, ...)

        :return:
         A advice
        """

        new_advice = AdvicesConsumption(type_d=type_d, advice=advice, device=device)
        db.session.add(new_advice)
        db.session.commit()

    def get_type_d(self):
        """
        :return the type of the device (str)
        """
        return self.type_d

    def set_type_d(self, new_type):
        """
        affect: type_d = new_type (str)
        """
        self.type_d = new_type
        db.session.commit()

class Devices(db.Model):
    """

    """
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    nb_volt = db.Column(db.Integer, nullable=False)
    hub_port = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)

    def add_new_device(name, description, nb_volt=12, hub_port=0):
        """
        Add a new device

        :parameter
        name: name of the device (string)
        description: description of the device (string)
        """

        new_device = Devices(name=name, nb_volt=nb_volt, hub_port=hub_port, description=description)
        db.session.add(new_device)
        db.session.commit()

class MeasureConsumption(db.Model):
    """
    """
    __tablename__ = "measure_consumption"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    measure = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)

    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"))
    device = db.relationship("Devices", backref=db.backref("deviceI", lazy=True))

    def add_new_measure(m, did):
        """
        Add a new device

        :parameter
        measure: name of the device (string)
        device_id: description of the device (string)
        """

        new_measure = MesaureConsumption(measure=m, datetime=datetime.today(), device_id=did)
        db.session.add(new_measure)
        db.session.commit()


# Initializing the database
Devices.add_new_device(name="Frigo", description="Frigo de 12V", nb_volt=12, hub_port=0)
Devices.add_new_device(name="Bouiloire", description="Bouiloire de 12V", nb_volt=12, hub_port=2)
Devices.add_new_device(name="Taque de cuisson", description="Taque de cuisson", nb_volt=12, hub_port=3)

AdvicesConsumption.add_new_advice("Consommation", "Pour donner 750 lumens, une ampoule à incandescence a besoin de 60 W", "Ampoule à incandescence")
AdvicesConsumption.add_new_advice("Consommation", "Pour donner 750 lumens, une ampoule économique a besoin 12 W ", "Ampoule économique")
AdvicesConsumption.add_new_advice("Consommation", "Pour donner 750 lumens une ampoule LED a besoin 6.5 W", "Ampoule LED")

AdvicesConsumption.add_new_advice("Consommation", "Energie nécessaire pour chauffer 1,5 litre d'eau de 20 à 95°C = 295 Wh", "Gazette")
AdvicesConsumption.add_new_advice("Consommation", "Energie nécessaire pour chauffer 1,5 litre d'eau de 20 à 95°C = 162 Wh", "Induction")
AdvicesConsumption.add_new_advice("Consommation", "Energie nécessaire pour chauffer 1,5 litre d'eau de 20 à 95°C = 233 Wh", "Vitrocéramique")
AdvicesConsumption.add_new_advice("Consommation", "Energie nécessaire pour chauffer 1,5 litre d'eau de 20 à 95°C = 252 Wh", "Fonte")