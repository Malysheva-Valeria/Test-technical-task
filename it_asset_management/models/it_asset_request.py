from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ITAssetRequest(models.Model):
    """
    Модель для управління заявками співробітників на отримання нового активу
    або ремонт існуючого. Має workflow: створення → очікування → в роботі → готово.
    """

    #Внутрішні атрибути моделі
    _name = 'it.asset.request'
    _description = 'IT Asset Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'create_date desc'

    #Номер заявки (автогенерується через sequence)
    name = fields.Char(
        string='Номер заявки',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True #Логування в chatter
    )

    #Тип заявки
    request_type = fields.Selection([
        ('new', 'Новий актив'),
        ('repair', 'Ремонт'),
        ('replacement', 'Заміна')
    ], string='Тип заявки', required=True, default='new', tracking=True)

    #Хто створив заявку (автоматично = поточний користувач)
    requester_id = fields.Many2one(
        'res.partner',
        string='Заявник',
        required=True,
        default=lambda self: self.env.user.partner_id,
        domain=[('is_company', '=', False)],
        tracking=True
    )

    #Актив для ремонту/заміни (обов'язковий якщо request_type != 'new')
    asset_id = fields.Many2one(
        'it.asset',
        string='Актив',
        help='Заповнюється для заявок типу "Ремонт" або "Заміна"',
        tracking=True
    )

    #Категорія для нового активу
    category_id = fields.Many2one(
        'it.asset.category',
        string='Категорія',
        help='Для нових активів - вкажіть бажану категорію'
    )

    #Опис проблеми/потреби
    description = fields.Text(
        string='Опис',
        required=True,
        help='Детальний опис потреби або проблеми'
    )

    #Чому потрібен актив
    justification = fields.Text(
        string='Обґрунтування',
        help='Обґрунтування необхідності активу'
    )

    #Lifecycle статус заявки
    state = fields.Selection([
        ('draft', 'Чернетка'),
        ('submitted', 'Очікування'),
        ('in_progress', 'В роботі'),
        ('approved', 'Схвалено'),
        ('done', 'Готово'),
        ('rejected', 'Відхилено'),
        ('cancelled', 'Скасовано')
    ], string='Статус', default='draft', required=True, tracking=True)

    #Пріоритет виконання
    priority = fields.Selection([
        ('0', 'Низький'),
        ('1', 'Середній'),
        ('2', 'Високий'),
        ('3', 'Критичний')
    ], string='Пріоритет', default='1', tracking=True)

    #Хто відповідає за виконання (призначає менеджер)
    assigned_to_id = fields.Many2one(
        'res.users',
        string='Відповідальний',
        tracking=True,
        domain=[('share', '=', False)]
    )

    #Дати для відстеження термінів
    request_date = fields.Date(
        string='Дата заявки',
        default=fields.Date.today,
        required=True
    )
    
    expected_date = fields.Date(
        string='Очікувана дата виконання'
    )
    
    completion_date = fields.Date(
        string='Дата виконання',
        readonly=True
    )

    #Додаткова інформація
    comments = fields.Html(
        string='Коментарі'
    )
    
    #Для порталу
    access_token = fields.Char(
        'Security Token',
        copy=False
    )
    
    @api.model
    def create(self, vals):
        """Генерація автоматичного номера заявки при створенні"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('it.asset.request') or _('New')
        return super(ITAssetRequest, self).create(vals)
    
    @api.onchange('request_type')
    def _onchange_request_type(self):
        """Очищення поля активу якщо тип заявки - новий актив"""
        if self.request_type == 'new':
            self.asset_id = False
    
    @api.constrains('request_type', 'asset_id')
    def _check_asset_required(self):
        """Перевірка чи заповнений актив для заявок типу ремонт/заміна"""
        for request in self:
            if request.request_type in ['repair', 'replacement'] and not request.asset_id:
                raise ValidationError(_('Для заявок типу "Ремонт" або "Заміна" необхідно вказати актив.'))
    
    def action_submit(self):
        """Подавання заявки на розгляд"""
        self.write({'state': 'submitted'})
        #Надсилання повідомлення менеджерам
        self.message_post(
            body=_('Нова заявка від %s') % self.requester_id.name,
            subject=_('Нова заявка на IT-актив')
        )
    
    def action_start_progress(self):
        """Початок роботи над заявкою"""
        self.write({
            'state': 'in_progress',
            'assigned_to_id': self.env.user.id
        })
    
    def action_approve(self):
        """Схвалення заявки"""
        self.write({'state': 'approved'})
    
    def action_complete(self):
        """Завершення заявки"""
        self.write({
            'state': 'done',
            'completion_date': fields.Date.today()
        })
        #Надсилання повідомлення заявнику
        self.message_post(
            body=_('Ваша заявка виконана'),
            partner_ids=[self.requester_id.id]
        )
    
    def action_reject(self):
        """Відхилення заявки"""
        self.write({'state': 'rejected'})
        #Надсилання повідомлення заявнику
        self.message_post(
            body=_('Вашу заявку відхилено'),
            partner_ids=[self.requester_id.id]
        )
    
    def action_cancel(self):
        """Скасування заявки"""
        self.write({'state': 'cancelled'})
    
    def _compute_access_url(self):
        """Генерація URL для доступу через портал"""
        super(ITAssetRequest, self)._compute_access_url()
        for request in self:
            request.access_url = '/my/asset-requests/%s' % request.id
    
    def _get_report_base_filename(self):
        """Базове ім'я файлу для звіту"""
        self.ensure_one()
        return 'Asset Request - %s' % self.name
