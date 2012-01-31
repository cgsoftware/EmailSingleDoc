# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import pooler
import tools

from tools.translate import _
from osv import fields,osv
import time
import netsvc
from tools.misc import UpdateableStr, UpdateableDict


email_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Send invoice/s by Email">
    <field name="email_sent"/>
</form>'''

email_done_fields = {
    'email_sent': {'string':'Quantity of Emails sent', 'type':'integer', 'readonly': True},
}


class email_single_doc(osv.osv_memory):
 _name = 'email.single_doc'
 _description = 'Genera Invia Email Ad un Singolo Partner per i Doc Selezionati '

 _columns= {
            'to': fields.char("A:", size=1024, required=True),
            'subject':fields.char('Oggetto ',  size=64, required=True),
            'text': fields.text('Testo Messagio', required=True),
            }    
    
 def default_get(self, cr, uid, fields, context=None):
        data={}
        p = pooler.get_pool(cr.dbname)
        user = p.get('res.users').browse(cr, uid, uid, context)
        subject = user.company_id.name+_('. Documento Num.')
        text = '\n--\n' + user.signature
        pool = pooler.get_pool(cr.dbname)
        fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])

        invoices = p.get('fiscaldoc.header').browse(cr, uid, active_ids, context)
        adr_ids = []
        partner_id = invoices[0].partner_id.id
        for inv in invoices:
            if partner_id != inv.partner_id.id:
                raise osv.except_osv(_('Warning'), _('Hai Selezionato Partner Diversi puoi Inviare allo Stesso Partner'))
            if inv.name:
                subject = subject + ' ' + inv.name
#            if inv.name:
#                text = inv.name + '\n' + text
            if inv.partner_indfat_id.id not in adr_ids:
                adr_ids.append(inv.partner_indfat_id.id)
#            if inv.address_contact_id and inv.address_contact_id.id not in adr_ids:
#                adr_ids.append(inv.address_contact_id.id)
        addresses = p.get('res.partner.address').browse(cr, uid, adr_ids, context)
        to = []
        for adr in addresses:
            if adr.email:
                name = adr.name or adr.partner_id.name
                # The adr.email field can contain several email addresses separated by ,
                to.extend(['%s <%s>' % (name, email) for email in adr.email.split(',')])
        to = ','.join(to)
        return {'to': to, 'subject': subject, 'text': text}
    
 def create_report(self,cr, uid, res_ids, report_name=False, file_name=False,data=False,context=False):
        #import pdb;pdb.set_trace()
        if not report_name or not res_ids:
            return (False, Exception('Report name and Resources ids are required !!!'))
        try:
            ret_file_name = '/tmp/'+file_name+'.pdf'
            service = netsvc.LocalService("report."+report_name);
            (result, format) = service.create(cr, uid, res_ids, data, context)
            fp = open(ret_file_name, 'wb+');
            fp.write(result);
            fp.close();
        except Exception,e:
            print 'Exception in create report:',e
            return (False, str(e))
        return (True, ret_file_name)
    
 

 def  get_data(self, cr, uid, fields, context=None):
        #import pdb;pdb.set_trace()
        pool = pooler.get_pool(cr.dbname)
        fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        if active_ids:
            for doc in fatture.browse(cr, uid, active_ids, context=context):
                if Primo:
                    Primo = False
                    DtIni = doc['data_documento']
                    NrIni = doc['name']
                    danr = doc['id']
                  #import pdb;pdb.set_trace()
                DtFin = doc['data_documento']
                NrFin = doc['name']
                anr = doc['id']
                

                
        
        return{'dadata':DtIni,'adata':DtFin,'danrv':NrIni,'anrv':NrFin,'sconto':False,'prezzi':False}

 def _build_contexts(self, cr, uid, ids, data, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
        result = {}
        sub = data['form']['danrv']
        result = {'danr':data['form']['danrv'],'anr':data['form']['anrv'],'dadata':data['form']['dadata'],
                  'adata':data['form']['adata'], 'sconto':data['form']['sconto'], 'prezzi':data['form']['prezzi'], 'name':sub}
        var = data['form']['prezzi']
        #import pdb;pdb.set_trace()
        if var is True or 1:
            result = {'danr':data['form']['danrv'],'anr':data['form']['anrv'],'dadata':data['form']['dadata'],
                  'adata':data['form']['adata'], 'sconto':data['form']['sconto'], 'prezzi':1,'name':sub}
        else:
            result = {'danr':data['form']['danrv'],'anr':data['form']['anrv'],'dadata':data['form']['dadata'],
                  'adata':data['form']['adata'], 'sconto':data['form']['sconto'], 'prezzi':0,'name':sub}
        return result


 def report_name(self, cr, uid, ids, data, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
        pool = pooler.get_pool(cr.dbname)
        fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        if active_ids:
            for doc in fatture.browse(cr, uid, active_ids, context=context):
                if Primo:
                    Primo = False
                    IdTipoSta = doc.tipo_doc.id
                    TipoStampa = doc.tipo_doc.tipo_modulo_stampa.report_name
                #import pdb;pdb.set_trace()
                else:
                  if IdTipoSta <> doc.tipo_doc.id:
                      raise osv.except_osv(_('ERRORE !'),_('Devi Selezionare documenti con la stessa Causale Documento'))

        return TipoStampa #{
               # 'type': 'ir.actions.report.xml',
              #  'report_name': TipoStampa,
              #  'datas': data,
           # }



 def send_mails(self, cr, uid, ids, context):
     # prepara il dict data per la stampa
    if context is None:
            context = {}
          
    data = {}
    data['ids'] = context.get('active_ids', [])
    data['model'] = context.get('active_model', 'ir.ui.menu')
    data['form'] = self.get_data(cr, uid, [],context)
    used_context = self._build_contexts(cr, uid, ids, data, context=context)
    data['form']['parameters'] = used_context
    
     
    import re
    p = pooler.get_pool(cr.dbname)

    user = p.get('res.users').browse(cr, uid, uid, context)
    file_name = user.company_id.name.replace(' ','_')+'_'+_('Docum')
    account_smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','account'),('state','=','confirm'),('active','=',True)], context=False)
    if not account_smtpserver_id:
        default_smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','default'),('state','=','confirm'),('active','=',True)], context=False)
    smtpserver_id = account_smtpserver_id or default_smtpserver_id
    if smtpserver_id:
        smtpserver_id = smtpserver_id[0]
    else:
        raise osv.except_osv(_('Error'), _('No SMTP Server has been defined!'))
    #import pdb;pdb.set_trace()   
    # Create report to send as file attachments
    report = self.create_report(cr, uid, data['ids'], self.report_name(cr, uid, ids, data, context), file_name,data,context)
    attachments = report[0] and [report[1]] or []
    datarec = self.browse(cr,uid,ids)[0]
    #import pdb;pdb.set_trace()   
    nbr = 0
    for email in datarec.to.split(','):
        #print email, data['form']['subject'], data['ids'], data['form']['text'], data['model'], file_name
        state = p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, email, datarec.subject, datarec.text, attachments)
        if not state:
            raise osv.except_osv(_('Error sending email'), _('Please check the Server Configuration!'))
        nbr += 1

    # Add a partner event
    docs = p.get(data['model']).browse(cr, uid, data['ids'], context)
    partner_id = docs[0].partner_id.id
    c_id = p.get('res.partner.canal').search(cr ,uid, [('name','ilike','EMAIL'),('active','=',True)])
    c_id = c_id and c_id[0] or False
    p.get('res.partner.event').create(cr, uid,
            {'name': _('Email sent through invoice wizard'),
             'partner_id': partner_id,
             'description': _('To: ').encode('utf-8') + datarec.to +
                            _('\n\nSubject: ').encode('utf-8') + datarec.subject +
                            _('\n\nText:\n').encode('utf-8') + datarec.text,
             'document': data['model']+','+str(docs[0].id),
             'canal_id': c_id,
             'user_id': uid, })
    return {'email_sent': nbr}




email_single_doc()






