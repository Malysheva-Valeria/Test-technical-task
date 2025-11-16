from odoo import models, fields


class Disease(models.Model):
    _name = 'hr_hospital.disease'
    _description = 'Disease Type'
    _rec_name = 'name'

    name = fields.Char(
        string='Disease Name',
        required=True,
        index=True
    )
    code = fields.Char(
        string='Disease Code',
        required=True
    )
    description = fields.Text(
        string='Description'
    )
    category = fields.Selection(
        selection=[
            ('infectious', 'Infectious'),
            ('chronic', 'Chronic'),
            ('genetic', 'Genetic'),
            ('other', 'Other')
        ],
        string='Category',
        default='other'
    )
    patient_ids = fields.Many2many(
        comodel_name='hr_hospital.patient',
        string='Patients',
        relation='patient_disease_rel',
        column1='disease_id',
        column2='patient_id'
    )
