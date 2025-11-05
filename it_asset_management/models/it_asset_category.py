from odoo import models, fields, api


class ITAssetCategory(models.Model):
    """
    Модель для категоризації IT-активів.
    Дозволяє групувати активи за типами (комп'ютери, сервери, мобільні пристрої, etc).
    """

    #Внутрішні атрибути моделі
    _name = 'it.asset.category'
    _description = 'IT Asset Category'
    _order = 'name'

    #Базова інформація про категорію
    name = fields.Char(
        string='Назва категорії',
        required=True,
        translate=True
    )
    
    code = fields.Char(
        string='Код',
        help='Унікальний код категорії'
    )
    
    description = fields.Text(
        string='Опис'
    )

    #Ієрархічна структура (дерево категорій)
    parent_id = fields.Many2one(
        'it.asset.category',
        string='Батьківська категорія',
        ondelete='cascade'
    )
    
    child_ids = fields.One2many(
        'it.asset.category',
        'parent_id',
        string='Дочірні категорії'
    )

    #Computed поле - автоматичний підрахунок
    asset_count = fields.Integer(
        string='Кількість активів',
        compute='_compute_asset_count'
    )

    #Стандартне поле для архівації
    active = fields.Boolean(
        string='Активна',
        default=True
    )
    
    @api.depends('name')
    def _compute_asset_count(self):
        """Підрахування кількості активів в кожній категорії"""
        for category in self:
            category.asset_count = self.env['it.asset'].search_count([
                ('category_id', '=', category.id)
            ])
    
    def name_get(self):
        """Форматування відображення назви категорії з урахуванням ієрархії"""
        result = []
        for category in self:
            name = category.name
            if category.parent_id:
                name = f"{category.parent_id.name} / {name}"
            result.append((category.id, name))
        return result
