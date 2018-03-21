import sublime
import sublime_plugin
import os
from .CommandTree import COMMAND_TREE
from .Parser import Parser

colorSchemeColors ={ 
	"mcccomment" : "comment",
	"mcccommand" : "keyword",
	"mccentity"  : "entity.name",
	"mccliteral" : "support.type", #Italic too
	"mccstring"  : "string",
	"mccconstant": "constant.numeric"
}
max_token_ids = {}

class MccHighlightCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		full_region = sublime.Region(0, self.view.size())
		file_lines = self.view.lines(full_region)
		token_id = 0
		parser = Parser(self.view)

		for line in file_lines:
			token_id = parser.highlight(COMMAND_TREE, line, 0)

		viewId = self.view.id() # If token_ids aren't overwritten already, remove them from the equation
		if viewId in max_token_ids and max_token_ids[viewId] > token_id:
			for i in range(token_id, max_token_ids[viewId]):
				self.view.add_regions("token" + str(i), [])
		max_token_ids[viewId] = token_id

		print("done")