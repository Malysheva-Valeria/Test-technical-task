from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ITAssetMovement(models.Model):
    """
    Модель для відстеження історії переміщень IT-активів.

    Зберігає інформацію про всі переміщення активів між співробітниками:
    хто, кому, коли та з якої причини передав актив.
    """
    _name = 'it.asset.movement'
    _description = 'IT Asset Movement'
    _inherit = ['mail.thread']
    _order = 'movement_date desc'

    #Основна інформація
    name = fields.Char(
        string='Номер переміщення',
        required=True,
        copy=False,
        readonly=True,
        default='/',
        help='Автоматично генерований номер переміщення'
    )

    asset_id = fields.Many2one(
        comodel_name='it.asset',
        string='Актив',
        required=True,
        ondelete='cascade',
        tracking=True,
        help='Актив, який переміщується'
    )

    #Хто передав і кому
    previous_employee_id = fields.Many2one(
        comodel_name='res.partner',
        string='Попередній співробітник',
        domain=[('is_company', '=', False)],
        tracking=True,
        help='Співробітник, який передає актив'
    )

    employee_id = fields.Many2one(
        comodel_name='res.partner',
        string='Співробітник',
        required=True,
        domain=[('is_company', '=', False)],
        tracking=True,
        help='Співробітник, який отримує актив'
    )

    #Дата та причина
    movement_date = fields.Date(
        string='Дата переміщення',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help='Коли відбулося переміщення'
    )

    movement_type = fields.Selection([
        ('assignment', 'Призначення'),
        ('transfer', 'Передача'),
        ('return', 'Повернення'),
        ('maintenance', 'На ремонт')
    ], string='Тип переміщення', default='assignment', tracking=True)

    reason = fields.Text(
        string='Причина переміщення',
        help='Чому актив було переміщено'
    )

    notes = fields.Text(
        string='Примітки',
        help='Додаткова інформація'
    )

    #Хто виконав переміщення
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Відповідальний',
        default=lambda self: self.env.user,
        tracking=True,
        help='Користувач, який виконав переміщення'
    )

    #Computed поля
    asset_code = fields.Char(
        related='asset_id.code',
        string='Інвентарний номер',
        store=True,
        help='Інвентарний номер активу'
    )

    asset_category = fields.Char(
        related='asset_id.category_id.name',
        string='Категорія активу',
        store=True,
        help='Категорія активу'
    )

    @api.model
    def create(self, vals):
        """При створенні генеруємо номер переміщення та оновлюємо актив"""
        #Генерація послідовного номера
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'it.asset.movement'
            ) or '/'

        #Створення переміщення
        movement = super().create(vals)

        #Оновлення співробітника в активі
        if movement.asset_id:
            movement.asset_id.write({
                'employee_id': movement.employee_id.id
            })

            #Створення повідомлення в chatter активу
            movement.asset_id.message_post(
                body=_('Актив переміщено від %(from_emp)s до %(to_emp)s') % {
                    'from_emp': movement.previous_employee_id.name or _('склад'),
                    'to_emp': movement.employee_id.name,
                }
            )

        return movement

    @api.constrains('previous_employee_id', 'employee_id')
    def _check_employees(self):
        """Перевірка, що співробітники різні"""
        for movement in self:
            if (movement.previous_employee_id and
                    movement.previous_employee_id == movement.employee_id):
                raise ValidationError(
                    _('Неможливо передати актив самому собі!')
                )

    def name_get(self):
        """Форматування відображення запису історії"""
        result = []
        for movement in self:
            name = f"{movement.asset_id.name} → {movement.employee_id.name} ({movement.movement_date})"
            result.append((movement.id, name))
        return result