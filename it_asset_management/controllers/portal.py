from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


class ITAssetPortal(CustomerPortal):
    """
    Контролер для портальної частини модуля IT Asset Management.
    Надає співробітникам доступ до їх активів і заявок через портал.
    """
    
    def _prepare_home_portal_values(self, counters):
        """Додає кількість активів і заявок на головну сторінку порталу"""
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        if 'asset_count' in counters:
            asset_count = request.env['it.asset'].search_count([
                ('employee_id', '=', partner.id),
                ('state', 'in', ['assigned', 'in_use'])
            ])
            values['asset_count'] = asset_count
        
        if 'request_count' in counters:
            request_count = request.env['it.asset.request'].search_count([
                ('requester_id', '=', partner.id)
            ])
            values['request_count'] = request_count
        
        return values
    
    @http.route(['/my/assets', '/my/assets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_assets(self, page=1, sortby=None, filterby=None, **kw):
        """Відображає список активів закріплених за співробітником"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ITAsset = request.env['it.asset']

        domain = []
        
        #Сортування
        searchbar_sortings = {
            'date': {'label': _('Дата призначення'), 'order': 'assignment_date desc'},
            'name': {'label': _('Назва'), 'order': 'name'},
            'category': {'label': _('Категорія'), 'order': 'category_id'},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        #Підрахунок
        asset_count = ITAsset.search_count(domain)
        
        #Пагінація
        pager = portal_pager(
            url="/my/assets",
            url_args={},
            total=asset_count,
            page=page,
            step=self._items_per_page
        )
        
        #Пошук активів
        assets = ITAsset.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'assets': assets,
            'page_name': 'asset',
            'pager': pager,
            'default_url': '/my/assets',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        
        return request.render("it_asset_management.portal_my_assets", values)
    
    @http.route(['/my/asset/<int:asset_id>'], type='http', auth="user", website=True)
    def portal_my_asset(self, asset_id, **kw):
        """Відображає детальну інформацію про конкретний актив"""
        try:
            asset_sudo = self._document_check_access('it.asset', asset_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'asset': asset_sudo,
            'page_name': 'asset',
        }
        
        return request.render("it_asset_management.portal_my_asset", values)
    
    @http.route(['/my/asset-requests', '/my/asset-requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_requests(self, page=1, sortby=None, filterby=None, **kw):
        """Відображає список заявок співробітника"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ITAssetRequest = request.env['it.asset.request']
        
        domain = [('requester_id', '=', partner.id)]
        
        #Фільтрація
        searchbar_filters = {
            'all': {'label': _('Всі'), 'domain': []},
            'submitted': {'label': _('Очікування'), 'domain': [('state', '=', 'submitted')]},
            'in_progress': {'label': _('В роботі'), 'domain': [('state', '=', 'in_progress')]},
            'done': {'label': _('Готово'), 'domain': [('state', '=', 'done')]},
        }
        
        #Сортування
        searchbar_sortings = {
            'date': {'label': _('Дата заявки'), 'order': 'request_date desc'},
            'name': {'label': _('Номер'), 'order': 'name'},
            'state': {'label': _('Статус'), 'order': 'state'},
        }
        
        if not sortby:
            sortby = 'date'
        if not filterby:
            filterby = 'all'
        
        order = searchbar_sortings[sortby]['order']
        domain += searchbar_filters[filterby]['domain']
        
        #Підрахунок
        request_count = ITAssetRequest.search_count(domain)
        
        #Пагінація
        pager = portal_pager(
            url="/my/asset-requests",
            url_args={},
            total=request_count,
            page=page,
            step=self._items_per_page
        )
        
        #Пошук заявок
        requests = ITAssetRequest.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'requests': requests,
            'page_name': 'asset_request',
            'pager': pager,
            'default_url': '/my/asset-requests',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'sortby': sortby,
            'filterby': filterby,
        })
        
        return request.render("it_asset_management.portal_my_requests", values)

    @http.route(['/my/asset-requests/<int:request_id>'], type='http', auth="user", website=True)
    def portal_my_request(self, request_id, access_token=None, **kw):
        """Відображає детальну інформацію про конкретну заявку"""
        try:
            request_sudo = self._document_check_access('it.asset.request', request_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        #Забезпечення доступу до токена
        request_sudo._portal_ensure_token()

        values = {
            'asset_request': request_sudo,
            'page_name': 'asset_request',
            'pid': kw.get('pid'),
            'hash': kw.get('hash'),
        }

        return request.render("it_asset_management.portal_my_request", values)
    
    @http.route(['/my/asset-requests/new'], type='http', auth="user", website=True)
    def portal_new_request(self, **kw):
        """Форма для створення нової заявки"""
        partner = request.env.user.partner_id
        categories = request.env['it.asset.category'].search([])
        assets = request.env['it.asset'].search([
            ('employee_id', '=', partner.id),
            ('state', 'in', ['assigned', 'in_use'])
        ])
        
        values = {
            'categories': categories,
            'assets': assets,
            'page_name': 'new_request',
        }
        
        return request.render("it_asset_management.portal_new_request", values)
    
    @http.route(['/my/asset-requests/create'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def portal_create_request(self, **post):
        """Створення нової заявки від співробітника"""
        partner = request.env.user.partner_id
        
        vals = {
            'requester_id': partner.id,
            'request_type': post.get('request_type'),
            'description': post.get('description'),
            'justification': post.get('justification', ''),
            'priority': post.get('priority', '1'),
        }
        
        #Додавання активу якщо це ремонт або заміна
        if post.get('request_type') in ['repair', 'replacement']:
            vals['asset_id'] = int(post.get('asset_id'))
        else:
            #Для нового активу додаємо категорію
            if post.get('category_id'):
                vals['category_id'] = int(post.get('category_id'))
        
        #Створення заявки
        new_request = request.env['it.asset.request'].sudo().create(vals)
        
        #Одразу подання на розгляд
        new_request.action_submit()
        
        return request.redirect('/my/asset-requests/%s' % new_request.id)

    @http.route(['/my/asset-requests/<int:request_id>/message'], type='http', auth="user", website=True,
                methods=['POST'], csrf=True)
    def portal_request_message(self, request_id, **post):
        """Додавання коментаря до заявки"""
        try:
            request_sudo = self._document_check_access('it.asset.request', request_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        #Додавання коментаря
        message = post.get('message', '').strip()
        if message:
            request_sudo.message_post(
                body=message,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                author_id=request.env.user.partner_id.id,
            )

        return request.redirect(f'/my/asset-requests/{request_id}')