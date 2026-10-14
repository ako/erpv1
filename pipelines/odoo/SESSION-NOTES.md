# Method log — pipelines/odoo

Format: `YYYY-MM-DD  <stack>  <dimension>  winner: <method>  loser: <method>  cause: <one line>`

2026-10-14  odoo  endpoints     winner: ast (extractor)          loser: regex (validator)   cause: controllers use bare `@route(` (from odoo.http import route), regex only matched `@http.route(`
2026-10-14  odoo  associations  winner: both fixed                loser: both                cause: `related=` relational fields declare no comodel; both sides now walk the related path (incl. mixins and _inherits parents)
2026-10-14  odoo  entityFields  winner: grep probe (3rd method)   loser: ast AND regex       cause: type-annotated declarations `x: Model = fields.T(` (18 in res.partner & co.) — ast saw AnnAssign, regex required `x =`; correlated blind spot, score was a false 100%
2026-10-14  odoo  associations  winner: ast (extractor)          loser: regex (validator)   cause: a `# comment` between `fields.One2many(` and the comodel literal (account.move.invoice_line_ids)
