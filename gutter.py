import sublime, sublime_plugin
import re
import json
import os

smeltJsonRegions = []
codeLines = {} #A dictionary that matches the blocktype to a list of regions

class UpdateGutterCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.add_regions("smeltJson", [], "source")
		for blockType in ["impulse", "repeating", "chain", "impulse-chain", "repeating-chain"]:
			self.view.add_regions(blockType, [], "source")
			codeLines[blockType] = []
			self.view.add_regions(blockType + "-off", [], "source")
			codeLines[blockType + "-off"] = []
			self.view.add_regions(blockType + "-conditional", [], "source")
			codeLines[blockType + "-conditional"] = []
			self.view.add_regions(blockType + "-conditional-off", [], "source")
			codeLines[blockType + "-conditional-off"] = []

		smeltJsonRegions = self.view.find_all(">\{.*\}")
		self.view.add_regions("smeltJson",smeltJsonRegions)
		lastType = "impulse"
		lastConditional = ""
		lastAuto = ""
		for i in range(len(smeltJsonRegions)):
			if (i<(len(smeltJsonRegions)-1)):
				codeRegion = sublime.Region(smeltJsonRegions[i].end()+1, smeltJsonRegions[i+1].begin()-1)
			elif (smeltJsonRegions[i].end()+1<self.view.size()):
				codeRegion = sublime.Region(smeltJsonRegions[i].end()+1, self.view.size())

			jsonString = self.view.substr(smeltJsonRegions[i])
			jsonString = jsonString[jsonString.find("{"):]
			smeltJson = json.loads(jsonString)
			newType = ""
			newConditional = ""
			try: 
				conditional = smeltJson["conditional"]
				if (conditional):
					newConditional = "-conditional"
				else:
					newConditional = ""
			except KeyError:
				newConditional = lastConditional

			try:
				if (smeltJson["type"] in ["impulse", "repeating", "chain", "impulse-chain", "repeating-chain"]):
					newType = smeltJson["type"]
				else:
					newType = lastType
			except KeyError:
				newType = lastType

			try:
				if (not smeltJson["auto"]):
					newAuto = "-off"
				else:
					newAuto = ""
			except KeyError:
				newAuto = lastAuto


			for line in self.view.lines(codeRegion):
				if ("comment" in self.view.scope_name(line.begin())):
					continue
				if(re.search(r"^\s*\/",self.view.substr(line)) and not re.search(r"^\s*\/\/", self.view.substr(line))):
					if (newType == "impulse-chain" or  newType == "repeating-chain"):
						newType = newType[0:-6]
						self.add_code_region(newType + newConditional + newAuto, line)
						newType = "chain"
						newAuto = ""
					else:
						self.add_code_region(newType+newConditional + newAuto, line)


				elif (re.search(r"^\s*\#",self.view.substr(line))):
					newType = "impulse"
					newConditional = ""
					newAuto = ""
					lastType = "impulse"
					lastConditional = ""
					lastAuto = ""

			lastType = newType
			lastConditional = newConditional

	def get_icon(self, icon):
		if int(sublime.version())<3014:
			path = "../MinecraftCommandCode"
			extension = ""
		else:
			path = os.path.realpath(__file__)
			root = os.path.split(os.path.dirname(path))[1]
			path = "Packages/" + os.path.splitext(root)[0]
			extension = ".png"
		return path + "/icons/" + icon + extension

	def add_code_region(self, label, line):
		codeLines[label].append(line)
		
		icon = self.get_icon(label)
		self.view.add_regions(label, codeLines[label], "source",  icon, sublime.PERSISTENT | sublime.HIDDEN)

class UpdateGutter(sublime_plugin.EventListener):
	def on_load(self, view):
		if (view.file_name().endswith(".mcc")):
			view.run_command("update_gutter")

	def on_modified(self, view):
		if (view.file_name().endswith(".mcc")):
			view.run_command("update_gutter")

	def on_activate(self, view):
		if (view.file_name().endswith(".mcc")):
			view.run_command("update_gutter")