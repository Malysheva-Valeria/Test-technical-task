from odoo import models, fields, api


class Patient(models.Model):
    _name = 'hr_hospital.patient'
    _description = 'Hospital Patient'
    _rec_name = 'name'

    name = fields.Char(
        string='Full Name',
        required=True,
        index=True
    )
    birth_date = fields.Date(
        string='Date of Birth',
        required=True
    )
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=True
    )
    gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ],
        string='Gender',
        required=True
    )
    phone = fields.Char(
        string='Phone'
    )
    email = fields.Char(
        string='Email'
    )
    address = fields.Text(
        string='Address'
    )
    doctor_id = fields.Many2one(
        comodel_name='hr_hospital.doctor',
        string='Attending Doctor',
        required=True
    )
    visit_ids = fields.One2many(
        comodel_name='hr_hospital.visit',
        inverse_name='patient_id',
        string='Visits'
    )
    disease_ids = fields.Many2many(
        comodel_name='hr_hospital.disease',
        string='Diseases',
        relation='patient_disease_rel',
        column1='patient_id',
        column2='disease_id'
    )

    @api.depends('birth_date')
    def _compute_age(self):
        from datetime import date
        for patient in self:
            if patient.birth_date:
                today = date.today()
                birth = patient.birth_date
                patient.age = today.year - birth.year - (
                    (today.month, today.day) < (birth.month, birth.day)
                )
            else:
                patient.age = 0
