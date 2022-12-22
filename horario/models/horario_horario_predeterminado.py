from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime

class HorarioHorarioPredeterminado(models.Model):
    _name = "horario.horario.predeterminado"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Horarios Predeterminados"

    def _get_horas(self):
        """
             Funcion para optener 4 annos siguientes apartir del actual
        :return:
            :: Genera 4 años sumando al años actual
        """
        lsi = []
        for a in range(24):
            if a > 9:
                lsi.append((str(a), (str(a))))
            else:
                lsi.append(("0"+str(a), ("0"+str(a))))
        return lsi

    def _get_minutos(self):
        """
             Funcion para optener 4 annos siguientes apartir del actual
        :return:
            :: Genera 4 años sumando al años actual
        """
        lsi = []
        for a in range(60):
            if a > 9:
                lsi.append((str(a), (str(a))))
            else:
                lsi.append(("0" + str(a), ("0" + str(a))))
        return lsi

    name = fields.Char(
        string="Nombre",
        required=False,
    )

    horarioPredeterminado_ids = fields.One2many(
        comodel_name="horario.horario.predeterminado.line",
        inverse_name="horarioPredeterminado_id",
        string="Horario",
        required=False,
    )
    diaHorario = fields.Selection(
        string="Dia",
        selection=
        [
            ('Lunes', 'Lunes'),
            ('Martes', 'Martes'),
            ('Miercoles', 'Miercoles'),
            ('Jueves', 'Jueves'),
            ('Viernes', 'Viernes'),
            ('Sabado', 'Sabado'),
            ('Domingo', 'Domingo'),
        ],
        required=False,
    )
    horaEntrada = fields.Selection(
        string="Hora Entrada",
        selection=_get_horas,
        required=False,

    )
    horaSalida= fields.Selection(
        string="Hora Salida",
        selection=_get_horas,
        required=False,

    )
    minutoEntrada = fields.Selection(
        string="Minuto entrada",
        selection=_get_minutos,
        required=False,

    )
    minutoSalida = fields.Selection(
        string="Minuto salida",
        selection=_get_minutos,
        required=False,

    )

    def agregar_horario(self):
        existe = False
        horasTotales = timedelta(hours=0)
        for data in self.horarioPredeterminado_ids:
            if data.diaHorario == self.diaHorario:
                existe = True

        if existe != True:
            entrada = datetime.strptime(str(datetime.today().date()) + ' ' + self.horaEntrada+':'+self.minutoEntrada + ':00',"%Y-%m-%d %H:%M:%S")
            salida = datetime.strptime(str(datetime.today().date()) + ' ' + self.horaSalida+':'+self.minutoSalida + ':00',"%Y-%m-%d %H:%M:%S")
            horas = (salida - entrada) - timedelta(hours=1)
            horasTotales += horas
            self.horarioPredeterminado_ids = [(0, 0, {'horarioPredeterminado_id': self.id,
                                                      'diaHorario': self.diaHorario,
                                                      'horaEntrada': self.horaEntrada + ':' + self.minutoEntrada,
                                                      'horaSalida': self.horaSalida + ':' + self.minutoSalida,
                                                      })]
        else:
            raise ValidationError("Ya tiene creado un horario para el dia "+self.diaHorario)

class HorarioHorarioPredeterminadoList(models.Model):
    _name = "horario.horario.predeterminado.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Horarios Predeterminados"

    horarioPredeterminado_id = fields.Many2one(
        comodel_name="horario.horario.predeterminado",
        string="",
        required=False,
        ondelete="cascade"
    )
    diaHorario = fields.Char(
        string="Dia",
        equired=False,
    )
    horaEntrada = fields.Char(
        string="Hora entrada",
        required=False,
    )
    horaSalida = fields.Char(
        string="Hora Salida",
        required=False,
    )
