from odoo import models, fields, api


class Doctor(models.Model):
    _name = 'hr_hospital.doctor'
    _description = 'Hospital Doctor'
    _rec_name = 'name'

    name = fields.Char(
        string='Full Name',
        required=True,
        index=True
    )
    specialty = fields.Char(
        string='Specialty',
        required=True
    )
    phone = fields.Char(
        string='Phone'
    )
    email = fields.Char(
        string='Email'
    )
    is_intern = fields.Boolean(
        string='Is Intern',
        default=False
    )
    mentor_id = fields.Many2one(
        comodel_name='hr_hospital.doctor',
        string='Mentor Doctor',
        domain=[('is_intern', '=', False)]
    )
    intern_ids = fields.One2many(
        comodel_name='hr_hospital.doctor',
        inverse_name='mentor_id',
        string='Interns'
    )
    patient_ids = fields.One2many(
        comodel_name='hr_hospital.patient',
        inverse_name='doctor_id',
        string='Patients'
    )
    visit_ids = fields.One2many(
        comodel_name='hr_hospital.visit',
        inverse_name='doctor_id',
        string='Visits'
    )
    patient_count = fields.Integer(
        string='Number of Patients',
        compute='_compute_patient_count'
    )

    @api.depends('patient_ids')
    def _compute_patient_count(self):
        for doctor in self:
            doctor.patient_count = len(doctor.patient_ids)
