from odoo import models, fields


class Visit(models.Model):
    _name = 'hr_hospital.visit'
    _description = 'Patient Visit'
    _rec_name = 'name'
    _order = 'visit_date desc'

    name = fields.Char(
        string='Visit Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'hr_hospital.visit'
        ) or 'New'
    )
    patient_id = fields.Many2one(
        comodel_name='hr_hospital.patient',
        string='Patient',
        required=True,
        index=True
    )
    doctor_id = fields.Many2one(
        comodel_name='hr_hospital.doctor',
        string='Doctor',
        required=True,
        index=True
    )
    visit_date = fields.Datetime(
        string='Visit Date',
        required=True,
        default=fields.Datetime.now
    )
    diagnosis = fields.Text(
        string='Diagnosis'
    )
    prescription = fields.Text(
        string='Prescription'
    )
    notes = fields.Text(
        string='Additional Notes'
    )
    status = fields.Selection(
        selection=[
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        string='Status',
        default='scheduled',
        required=True
    )
