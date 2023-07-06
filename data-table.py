from trac.wiki.macros import WikiMacroBase
from trac.util.html import Markup
from trac.wiki import Formatter
import StringIO
import yaml
from collections import OrderedDict

# make all yaml dicts ordered
# based on https://stackoverflow.com/a/21048064
yaml.add_constructor(
	yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
	lambda loader, node: OrderedDict(loader.construct_pairs(node))
)

class DataTableMacro(WikiMacroBase):
	'''
	Renders YAML document as a table.
	'''
	def expand_macro(self, formatter, name, text, args):
		try:
			data = yaml.safe_load(text)
		except Exception as e:
			# show exception to the user, as-is
			raise Exception(str(e))

		if not isinstance(data, dict):
			raise Exception('top-level should be a dict')

		cols = OrderedDict()
		for row, row_data in data.items():
			if not isinstance(row_data, dict):
				raise Exception('row %s should be a dict' % row)
			for col in row_data.keys():
				cols[col] = col

		out = StringIO.StringIO()

		out.write('<table class="wiki">')

		out.write('<tr><th></th>')
		for col in cols:
			out.write('<th>')
			out.write(Markup.escape(col))
			out.write('</th>')
		out.write('</tr>')

		for row, row_data in data.items():
			out.write('<tr><th>%s</th>' % Markup.escape(row))
			for col in cols:
				out.write('<td>')
				cell = unicode(row_data.get(col, ''))
				Formatter(self.env, formatter.context).format(cell, out)
				out.write('</td>')
			out.write('</tr>')

		out.write('</table>')
		return Markup(out.getvalue())
