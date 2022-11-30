from app import db, app
from datetime import datetime

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

    measures = db.relationship("MeasureConsumption", overlaps="measures")

    def get_between_measures(self, start, end):
        """day_consumption = 0
        begin = datetime.datetime(date.year, date.month, date.day)
        print(begin) 
        print(date)
        with app.app_context():
            mesures = list(MeasureConsumption.query.filter(MeasureConsumption.datetime.between(begin, date)))
            for m in mesures"""
        device_measures = self.measures
        between_measures = []
        for measure in list(device_measures):
            if start <= measure.datetime <= end:
                between_measures.append(measure)

        return between_measures


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
    device = db.relationship("Devices", backref=db.backref("deviceI", lazy=True), overlaps="measures")

    def add_new_measure(m, did, date = None):
        """
        Add a new device

        :parameter
        measure: name of the device (string)
        device_id: description of the device (string)
        """
        if date is None:
            date=datetime.today()

        with app.app_context():
            new_measure = MeasureConsumption(measure=m, datetime=date, device_id=did)
            db.session.add(new_measure)
            db.session.commit()

    def get_serializable_measure(self):
        return {"datetime":self.datetime.strftime("%Y/%m/%d, %H:%M:%S"), "measure":self.measure}


class WindowLog(db.Model):
    """
    """
    __tablename__ = "window_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)

    def add_new_action(action):
        """
        Add a new action in the log

        :parameter
        measure: name of the device (string)
        device_id: description of the device (string)
        """
        with app.app_context():
            new_action = WindowLog(action=action, datetime=datetime.today())
            db.session.add(new_action)
            db.session.commit()

    def get_serializable_action(self):
        return {"datetime":self.datetime.strftime("%Y/%m/%d, %H:%M:%S"), "action":self.action}


# Initializing the database
with app.app_context():
    db.drop_all()
    db.create_all()

    Devices.query.delete()
    Devices.add_new_device(name="Frigo", description="Frigo de 12V", nb_volt=12, hub_port=0)
    Devices.add_new_device(name="Bouiloire", description="Bouiloire de 12V", nb_volt=12, hub_port=2)
    Devices.add_new_device(name="Taque de cuisson", description="Taque de cuisson", nb_volt=12, hub_port=3)

    AdvicesConsumption.query.delete()
    AdvicesConsumption.add_new_advice("Consommation Ampoule", "Pour donner 750 lumens, une ampoule à incandescence a besoin de 60 W", "Ampoule à incandescence")
    AdvicesConsumption.add_new_advice("Consommation Ampoule", "Pour donner 750 lumens, une ampoule économique a besoin 12 W ", "Ampoule économique")
    AdvicesConsumption.add_new_advice("Consommation Ampoule", "Pour donner 750 lumens une ampoule LED a besoin 6.5 W", "Ampoule LED")

    AdvicesConsumption.add_new_advice("Consommation Taque", "Energie nécessaire pour chauffer 1,5 litre d'eau de 20 à 95°C = 295 Wh", "Gazette")
    AdvicesConsumption.add_new_advice("Consommation Taque", "Energie nécessaire pour chauffer 1,5 litre d'eau de 20 à 95°C = 162 Wh", "Induction")
    AdvicesConsumption.add_new_advice("Consommation Taque", "Energie nécessaire pour chauffer 1,5 litre d'eau de 20 à 95°C = 233 Wh", "Vitrocéramique")
    AdvicesConsumption.add_new_advice("Consommation Taque", "Energie nécessaire pour chauffer 1,5 litre d'eau de 20 à 95°C = 252 Wh", "Fonte")
    AdvicesConsumption.add_new_advice("Consommation Taque", "Les taques à inductions consomment 30 à 40% d'électricité en moins", "Induction")

    AdvicesConsumption.add_new_advice("Consommation", "Un frigidaire-Congélateur A+/304 L consomme 304 kWh par an ==> coût 46,99 € (compteur de 6kVA en option base)", "Frigo")
    AdvicesConsumption.add_new_advice("Consommation", "Un frigidaire-Congélateur A++/304 L consomme 257 kWh par an ==> coût 39,73 € (compteur de 6kVA en option base)", "Frigo")
    AdvicesConsumption.add_new_advice("Consommation", "Un frigidaire-Congélateur A+++/304 L consomme 160 kWh par an ==> coût 24,74 € (compteur de 6kVA en option base)", "Frigo")

    AdvicesConsumption.add_new_advice("Astuce", "Pour la cuisson à électricité privilégier les casseroles à fond parfaitement plat", "Cuisson Electrique")
    AdvicesConsumption.add_new_advice("Astuce", "Pour accéléer la cuissson ou le chauffage de l'eau vous devriez mettre un couvercle. Je geste"
                                                "peut vous faire économiser 45 €/an.", "Cuisson")

    AdvicesConsumption.add_new_advice("Astuce", "Si on fait une grande quantité de vaisselle mieux vaut utiliser la vaisselle pour économiser de l'eau."
                                                "Une machine peut laver jusqu’à 160 pièces de vaisselle avec seulement 10 à 12 litres d’eau.", "Lave-vaisselle")
    AdvicesConsumption.add_new_advice("Astuce", "Si vous devez rincer la vaisselle avant de la mettre dans la machine utiliser, utiliser de l'eau qui "
                                                "a déjà servi par exemple à laver les légumes ou cuir les pâtes...", "Lave-vaisselle")
    AdvicesConsumption.add_new_advice("Astuce", "Bien remplir le lave-vaisselle et consulter le mode d’emploi pour connaître la consommation d'eau et d'énergie de chaque programme"
                                        , "Lave-vaisselle")

    AdvicesConsumption.add_new_advice("Astuce", "Dégivrer le frigidaire peut vous faire économiser de l'argent. Par exemple de 2 mm de givre c'est environ 10 % de consommation"
                                                " supplémentaire et 5 mm de givre c'est + 30% de consommation.", "Frigidaire")
    AdvicesConsumption.add_new_advice("Astuce", "Bien choisir l'emplacement de son frigidaire: ne pas le mettre trop près des radiateurs, de la chaudière ou du four puisqu'ils"
                                                " produisent de la chaleur et auront plus tendances à le faire fonctionner d'avantage.", "Frigidaire")
    AdvicesConsumption.add_new_advice("Astuce", "Choisir la température adequate pour la conservation afin d'économiser de l'argent. 4-5° pour le réfrigérateur et -18° pour la congélation", "Frigidaire")

    AdvicesConsumption.add_new_advice("Astuce", "Quand on est raccordé au gaz, cuisiner avec ce derneir coûte moitié moins chère que"
                                                "l'électrique car on utilise le gaz pour se chauffer", "Choix énergie")
    AdvicesConsumption.add_new_advice("Astuce", "Aérez suffisament votre cuisine si vous utiliser le gaz et utiliser la hotte à chaque cuisson", "Utilisation gaz")
    AdvicesConsumption.add_new_advice("Astuce", "Si on utilise l'électricité il faut privilégier les taques à induction car elle "
                                                "consomme 30 à 40 % d’électricité en moins que les taques en fonte ou les vitrocéramiques.", "Choix énergie")

    AdvicesConsumption.add_new_advice("Achat G", "Bien réfléchire à ses habitudes afin de prendre l'appareil le mieux "
                                                "adapté à ses besoins et à la taille de sa famille", "Achat")
    AdvicesConsumption.add_new_advice("Achat G", "Le froid alimentaire représente 26% de la facture d'éléctricité d'après EDF.", "Frigo")
    AdvicesConsumption.add_new_advice("Achat G", "Prendre au serieux l'étiquette d'énergie car entre un modèle A+ et A+++ "
                                                "la consommation peut varier du simple au double", "Achat")


    AdvicesConsumption.add_new_advice("Utilisation", "Pour l'induction utiliser des ustenciles à adaptés (au fond aimanté)", "Induction")

    MeasureConsumption.query.delete()