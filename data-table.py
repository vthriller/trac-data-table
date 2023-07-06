from trac.wiki.macros import WikiMacroBase
from trac.util.html import Markup
from trac.wiki import Formatter
import StringIO
import yaml
from collections import OrderedDict

# make all yaml dicts ordered
# based on https://stackoverflow.com/a/21912744
class OrderedLoader(yaml.SafeLoader):
	pass
def construct_mapping(loader, node):
	loader.flatten_mapping(node)
	output = OrderedDict()

	# this is like loader.construct_pairs(), except this loop also checks if key already exists
	# we check for collision here and not in the dict to raise nicer exceptions
	for knode, vnode in node.value:
		k = loader.construct_object(knode, deep=False)
		v = loader.construct_object(vnode, deep=False)
		if k in output:
			raise yaml.constructor.ConstructorError(
				'while constructing a mapping',
				node.start_mark,
				'%r is defined multiple times' % k,
				knode.start_mark,
			)
		output[k] = v
	return output
OrderedLoader.add_constructor(
	yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping,
)

class DataTableMacro(WikiMacroBase):
	'''
	Renders YAML document as a table.
	'''
	def expand_macro(self, formatter, name, text, args):
		try:
			data = yaml.load(text, OrderedLoader)
		except Exception as e:
			# show exception to the user, as-is
			raise Exception(str(e))

		if not isinstance(data, dict):
			raise Exception('top-level should be a dict')

		cols = data.pop('_columns', OrderedDict())
		for row, row_data in data.items():
			if not isinstance(row_data, dict):
				raise Exception('row %s should be a dict' % row)
			for col in row_data.keys():
				if col not in cols:
					cols[col] = col

		out = StringIO.StringIO()

		out.write('<table class="wiki">')

		out.write('<tr><th></th>')
		for col in cols.values():
			out.write('<th>')
			out.write(Markup.escape(col))
			out.write('</th>')
		out.write('</tr>')

		for row, row_data in data.items():
			out.write('<tr><th>%s</th>' % Markup.escape(row))
			for col in cols:
				if col in row_data:
					out.write('<td>')
					cell = unicode(row_data[col])
					Formatter(self.env, formatter.context).format(cell, out)
					out.write('</td>')
				elif (args.get('show_gaps') or '0') != '0':
					# TODO class
					out.write('<td style="background-color: #ddd;"></td>')
				else:
					out.write('<td></td>')
			out.write('</tr>')

		out.write('</table>')
		return Markup(out.getvalue())
