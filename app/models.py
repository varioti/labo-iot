from app import db

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
        new_advice.session.add(new_advice)
        db.session.commit()
