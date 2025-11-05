from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ITAsset(models.Model):
    """
    Головна модель для управління IT-активами.
    Зберігає всю інформацію про актив: характеристики, стан, відповідального співробітника etc.
    """
    _name = 'it.asset'
    _description = 'IT Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Назва активу',
        required=True,
        tracking=True
    )
    
    code = fields.Char(
        string='Інвентарний номер',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    category_id = fields.Many2one(
        'it.asset.category',
        string='Категорія',
        required=True,
        tracking=True
    )
    
    description = fields.Text(
        string='Опис'
    )
    
    #Технічні характеристики
    serial_number = fields.Char(
        string='Серійний номер',
        tracking=True
    )
    
    manufacturer = fields.Char(
        string='Виробник'
    )
    
    model = fields.Char(
        string='Модель'
    )
    
    specifications = fields.Text(
        string='Технічні характеристики',
        help='Детальний опис технічних характеристик активу'
    )
    
    #Фінансова інформація
    purchase_date = fields.Date(
        string='Дата придбання',
        tracking=True
    )
    
    purchase_price = fields.Float(
        string='Ціна придбання',
        tracking=True
    )
    
    warranty_end_date = fields.Date(
        string='Дата закінчення гарантії'
    )
    
    #Життєвий цикл
    state = fields.Selection([
        ('purchase', 'Придбання'),
        ('available', 'Доступний'),
        ('assigned', 'Призначений'),
        ('in_use', 'У використанні'),
        ('maintenance', 'На ремонті'),
        ('retired', 'Списаний')
    ], string='Статус', default='purchase', required=True, tracking=True)
    
    #Відповідальна особа
    employee_id = fields.Many2one(
        'res.partner',
        string='Закріплений за співробітником',
        domain=[('is_company', '=', False)],
        tracking=True
    )
    
    assignment_date = fields.Date(
        string='Дата призначення',
        tracking=True
    )
    
    #Історія переміщень
    movement_ids = fields.One2many(
        'it.asset.movement',
        'asset_id',
        string='Історія переміщень'
    )
    
    #Заявки пов'язані з активом
    request_ids = fields.One2many(
        'it.asset.request',
        'asset_id',
        string='Заявки'
    )
    
    request_count = fields.Integer(
        string='Кількість заявок',
        compute='_compute_request_count'
    )
    
    #QR код
    qr_code = fields.Char(
        string='QR код',
        compute='_compute_qr_code',
        store=True
    )
    
    active = fields.Boolean(
        string='Активний',
        default=True
    )
    
    notes = fields.Html(
        string='Примітки'
    )
    
    @api.model
    def create(self, vals):
        """Генерація автоматичного інвентарного номера при створенні"""
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('it.asset') or _('New')
        return super(ITAsset, self).create(vals)
    
    @api.depends('code')
    def _compute_qr_code(self):
        """Генерація QR коду на основі інвентарного номера"""
        for asset in self:
            asset.qr_code = asset.code if asset.code != _('New') else ''
    
    def _compute_request_count(self):
        """Підрахунок кількості заявок для активу"""
        for asset in self:
            asset.request_count = len(asset.request_ids)
    
    def action_assign_to_employee(self):
        """Призначення активу співробітнику"""
        self.ensure_one()
        return {
            'name': _('Призначити співробітнику'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.asset',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
    
    def action_view_requests(self):
        """Відкриття списку заявок для активу"""
        self.ensure_one()
        return {
            'name': _('Заявки'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.asset.request',
            'view_mode': 'tree,form',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id},
        }
    
    def action_set_in_use(self):
        """Зміна статусу активу на 'У використанні'"""
        for asset in self:
            if not asset.employee_id:
                raise ValidationError(_('Не можна встановити статус "У використанні" без призначеного співробітника.'))
            asset.state = 'in_use'
    
    def action_set_maintenance(self):
        """Зміна статусу активу на 'На ремонті'"""
        self.write({'state': 'maintenance'})
    
    def action_set_available(self):
        """Зміна статусу активу на 'Доступний'"""
        self.write({'state': 'available', 'employee_id': False})
    
    def action_retire(self):
        """Списання активу"""
        self.write({'state': 'retired', 'active': False})
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Створення запису в історії переміщень при зміні співробітника"""
        if self.employee_id and self.id:
            self.env['it.asset.movement'].create({
                'asset_id': self.id,
                'employee_id': self.employee_id.id,
                'movement_date': fields.Date.today(),
                'notes': 'Призначено співробітнику'
            })
