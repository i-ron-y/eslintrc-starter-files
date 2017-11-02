import sys
import requests
from bs4 import BeautifulSoup

import datetime

# Here is where the data scraping happens.

page = requests.get('https://eslint.org/docs/rules/')
soup = BeautifulSoup(page.content, 'html.parser')


# e.g. ['possible-errors', ...]
typeIds = []

# e.g. ['Possible Errors', ...]
typeNames = []

for tag in soup.find_all('h2',{'id':True}):
	if not (tag['id'] == 'deprecated' or tag['id'] == 'removed'):
		typeIds.append(tag['id'])
		typeNames.append(tag.get_text())


# e.g. [(RuleType1, [(RuleName1, RuleDef1), (RuleName2, RuleDef2), ...]), (RuleType2, [...]), ...]
ruleGroups = []

for i in range(len(typeIds)):
	header = soup.find(id=typeIds[i])

	table = header.find_next_sibling('table')

	# e.g. [RuleName1, RuleDef1, RuleName2, RuleDef2, ...]
	tableContents = []

	tableSoup = table.find_all('p')

	for item in tableSoup:
		tableContents.append(item.get_text())
	
	# e.g. [(RuleName1, RuleDef1), (RuleName2, RuleDef2), ...]
	rules = list(zip(tableContents[0::2], tableContents[1::2]))

	# e.g. (RuleType1, [(RuleName1, RuleDef1), (RuleName2, RuleDef2), ...])
	ruleGroup = (typeNames[i], rules)

	ruleGroups.append(ruleGroup)



# Here is where the .eslintrc.js, .eslintrc.json, and .eslintrc.yaml files (containing ONLY the rules) are outputted,
# in the same directory where eslint-starter-file-generator.py is found.
# 
# WARNING: If you already have files named .eslintrc.js, .eslintrc.json, or .eslintrc.yaml in this directory, they WILL be overwritten.

indent = ' '*4
emptyline = '\n'*2


# Helper function: Prepare everything in the output file before the rules section
def prepareOutputStart(type):

	if type == 'js':
		openingChars = 'module.exports = {'
	elif type == 'json':
		openingChars = '{'
	else:    # if type == 'yaml':
		openingChars = ''

	fileDesc = prepareFileDesc(type)

	parserOptionsString = prepareParserOptionsString(type)

	envString = prepareEnvString(type)

	if type == 'js' or type == 'json':

		parserString = firstIndent + commentSymbol + ' "parser": "espree",                         // compatible parsers: "espree" (default), "esprima", "babel-eslint", and "typescript-eslint-parser" (experimental)\n'

		globalsString = (configCategoryHeaderStart + 'globals' + configCategoryHeaderEnd + emptyline +
		                 secondIndent + commentSymbol + ' e.g. "angular": true' + emptyline +
		                 firstIndent + '},\n')

		pluginsString = (firstIndent + '"plugins": [' + emptyline +
		                 secondIndent + commentSymbol + ' e.g. "react" (must run `npm install eslint-plugin-react` first)' + emptyline +
		                 firstIndent + '],\n')

		extendsString = (firstIndent + '"extends": [' + emptyline +
		                 secondIndent + commentSymbol + ' "eslint:recommended"                    // enables a subset of core rules that report common problems, which have a check mark on the rules page\n' +
		                 secondIndent + commentSymbol + ' "eslint:all"                            // enable all core rules in the currently installed version of ESLint' + emptyline +
		                 firstIndent + '],\n')

	else:    # if type == 'yaml':

		parserString = commentSymbol + ' parser: "espree",                        # compatible parsers: "espree" (default), "esprima", "babel-eslint", and "typescript-eslint-parser" (experimental)\n'

		globalsString = (commentSymbol + ' globals' + configCategoryHeaderEnd + emptyline +
		                 commentSymbol + secondIndent + commentSymbol + ' e.g. angular\n' +
		                 commentSymbol + secondIndent + commentSymbol + ' angular: true\n')

		pluginsString = (commentSymbol + ' plugins' + configCategoryHeaderEnd + emptyline +
		                 commentSymbol + secondIndent + commentSymbol + ' e.g. react (must run `npm install eslint-plugin-react` first)\n' +
		                 commentSymbol + secondIndent + commentSymbol + ' - react\n')

		extendsString = (commentSymbol + ' extends' + configCategoryHeaderEnd + emptyline +
		                 commentSymbol + secondIndent + commentSymbol + ' - eslint:recommended                # enables a subset of core rules that report common problems, which have a check mark on the rules page\n' +
		                 commentSymbol + secondIndent + commentSymbol + ' - eslint:all                        # enable all core rules in the currently installed version of ESLint\n')

	outputStart = (openingChars + emptyline +
		           fileDesc + emptyline +
		           parserOptionsString + emptyline +
		           parserString + emptyline +
		           envString + emptyline +
		           globalsString + emptyline +
		           pluginsString + emptyline +
		           extendsString + emptyline)

	return outputStart


# Helper function: Prepare the file description string
def prepareFileDesc(type):

	fileDesc = (firstIndent + commentSymbol + ' [' + type.upper() + ']\n' +
		        firstIndent + commentSymbol + '\n' +
		        firstIndent + commentSymbol + ' An .eslintrc starter file with all rules (set to 0) and envs (set to false) listed.\n' +
		        firstIndent + commentSymbol + ' Other options (although by no means comprehensive) are either set to false or else commented out.\n' +
		        firstIndent + commentSymbol + '\n' +
		        firstIndent + commentSymbol + ' Updated on ' + datetime.datetime.now().strftime ("%Y-%m-%d") + '.\n' +
		        firstIndent + commentSymbol + '\n' +
		        firstIndent + commentSymbol + ' Starter file generated by ESLint Starter File Generator:\n' +
		        firstIndent + commentSymbol + '     https://github.com/i-ron-y/eslint-starter-file-generator\n' +
		        firstIndent + commentSymbol + '\n' +
		        firstIndent + commentSymbol + ' ESLint docs -- Configuring ESLint:      https://eslint.org/docs/user-guide/configuring\n' +
		        firstIndent + commentSymbol + ' ESLint docs -- List of available rules: https://eslint.org/docs/rules/\n')

	return fileDesc


# Helper function: Prepare the parser options config group
def prepareParserOptionsString(type):

	thirdIndent = secondIndent + indent

	if type == 'js' or type == 'json':

		parserOptionsString = (configCategoryHeaderStart + 'parserOptions' + configCategoryHeaderEnd +
			                   emptyline +
			                   secondIndent + commentSymbol + ' "ecmaVersion": 5,                       // set to 3, 5 (default), 6, 7, or 8 to specify the version of ECMAScript syntax you want to use.\n' +
			                   secondIndent + commentSymbol + '                                         // You can also set to 2015 (same as 6), 2016 (same as 7), or 2017 (same as 8) to use the year-based naming.' +
			                   emptyline +
			                   secondIndent + commentSymbol + ' "sourceType": "script",                 // set to "script" (default) or "module" if your code is in ECMAScript modules.' +
			                   emptyline +
			                   itemStart + 'ecmaFeatures' + configCategoryHeaderEnd +
			                   emptyline +
			                   thirdIndent + '"globalReturn": false,              // allow return statements in the global scope\n' +
			                   thirdIndent + '"impliedStrict": false,             // enable global strict mode (if ecmaVersion is 5 or greater)\n' +
			                   thirdIndent + '"jsx": false,                       // enable JSX' +
			                   emptyline +
			                   thirdIndent + '"experimentalObjectRestSpread": false   // enable support for the experimental object rest/spread properties\n' +
			                   thirdIndent + commentSymbol + ' (IMPORTANT: This is an experimental feature that may change significantly in the future.\n' +
			                   thirdIndent + commentSymbol + ' It’s recommended that you do not write rules relying on this functionality unless you are\n' +
			                   thirdIndent + commentSymbol + ' willing to incur maintenance cost when it changes.)' +
			                   emptyline +
			                   secondIndent + '}' +
			                   emptyline +
			                   firstIndent + '},\n')

	else:    # if type == 'yaml'

		parserOptionsString = (configCategoryHeaderStart + 'parserOptions' + configCategoryHeaderEnd +
			                   emptyline +
			                   secondIndent + commentSymbol + ' ecmaVersion: 5                       # set to 3, 5 (default), 6, 7, or 8 to specify the version of ECMAScript syntax you want to use.\n' +
			                   secondIndent + commentSymbol + '                                      # You can also set to 2015 (same as 6), 2016 (same as 7), or 2017 (same as 8) to use the year-based naming.' +
			                   emptyline +
			                   secondIndent + commentSymbol + ' sourceType: "script"                 # set to "script" (default) or "module" if your code is in ECMAScript modules.' +
			                   emptyline +
			                   itemStart + 'ecmaFeatures' + configCategoryHeaderEnd +
			                   emptyline +
			                   thirdIndent + 'globalReturn: false              # allow return statements in the global scope\n' +
			                   thirdIndent + 'impliedStrict: false             # enable global strict mode (if ecmaVersion is 5 or greater)\n' +
			                   thirdIndent + 'jsx: false                       # enable JSX' +
			                   emptyline +
			                   thirdIndent + 'experimentalObjectRestSpread: false   # enable support for the experimental object rest/spread properties\n' +
			                   thirdIndent + commentSymbol + ' (IMPORTANT: This is an experimental feature that may change significantly in the future.\n' +
			                   thirdIndent + commentSymbol + ' It’s recommended that you do not write rules relying on this functionality unless you are\n' +
			                   thirdIndent + commentSymbol + ' willing to incur maintenance cost when it changes.)\n')

	return parserOptionsString


# Helper function: Prepare the envs config group
def prepareEnvString(type):

	envs = [('browser', 'browser global variables'),
	        ('node', 'Node.js global variables and Node.js scoping.'),
	        ('commonjs', 'CommonJS global variables and CommonJS scoping (use this for browser-only code that uses Browserify/WebPack).'),
	        ('shared-node-browser', 'Globals common to both Node and Browser.'),
	        ('es6', 'enable all ECMAScript 6 features except for modules (this automatically sets the ecmaVersion parser option to 6).'),
	        ('worker', 'web workers global variables.'),
	        ('amd', 'defines require() and define() as global variables as per the amd spec'),
	        ('mocha', 'adds all of the Mocha testing global variables'),
            ('jasmine', 'adds all of the Jasmine testing global variables for version 1.3 and 2.0'),
            ('jest', 'Jest global variables.'),
            ('phantomjs', 'PhantomJS global variables'),
            ('protractor', 'Protractor global variables'),
            ('qunit', 'QUnit global variables.'),
            ('jquery', 'jQuery global variables'),
            ('prototypejs', 'Prototype.js global variables'),
            ('shelljs', 'ShellJS global variables'),
            ('meteor', 'Meteor global variables.'),
            ('mongo', 'MongoDB global variables.'),
            ('applescript', 'AppleScript global variables.'),
            ('nashorn', 'Java 8 Nashorn global variables.'),
            ('serviceworker', 'Service Worker global variables.'),
            ('atomtest', 'Atom test helper globals.'),
            ('embertest', 'Ember test helper globals.'),
            ('webextensions', 'WebExtensions globals.'),
            ('greasemonkey', 'GreaseMonkey globals.')
           ]

	envStringGroup = configCategoryHeaderStart + 'env' + configCategoryHeaderEnd + emptyline

	for i in range(len(envs)):

		if ((type == 'js') or (type == 'json')) and (i == len(envs)-1):
			envNameString = itemStart + envs[i][0] + lastItemEnd
		else:
			envNameString = itemStart + envs[i][0] + itemEnd

		envDefnString = commentSymbol + ' ' + envs[i][1]
		envString = envNameString + ' '*(columnDefn-len(envNameString)) + envDefnString
		envStringGroup += envString + '\n'

	if type == 'js' or type == 'json':
		envStringGroup += "\n" + firstIndent + '},\n'

	return envStringGroup


# Helper function: Prepare the 'usage instruction' comment string
def prepareUsageString(type):

	if type == 'js' or type == 'json':
		usageStringExample = '"quotes": [2, "double"]'

	else:    # if type == 'yaml':
		usageStringExample = 'quotes: [2, double]'

	usageString = (secondIndent + commentSymbol + ' Usage:\n' +
	               secondIndent + commentSymbol + indent + '"off" or 0 - turn the rule off\n' +
	               secondIndent + commentSymbol + indent + '"warn" or 1 - turn the rule on as a warning (doesn’t affect exit code)\n' +
	               secondIndent + commentSymbol + indent + '"error" or 2 - turn the rule on as an error (exit code is 1 when triggered)\n' +
	               secondIndent + commentSymbol + '\n' +
	               secondIndent + commentSymbol + indent + 'If a rule has additional options, you can specify them using array literal syntax, such as:\n' +
	               secondIndent + commentSymbol + indent*2 + usageStringExample + '\n')

	return usageString


# Helper function: Format the rules and rule groups
def formatRules(type):

	formattedRules = ''

	ruleNameStart = itemStart

	if type == 'js' or type == 'json':
		commentHeader = commentSymbol*4
		ruleNameEnd = '": 0,'

	else:    # if type == 'yaml':
		commentHeader = commentSymbol*8
		ruleNameEnd = ': 0'

	for rg in range(len(ruleGroups)):

		headerString = secondIndent + commentHeader + ' ' + ruleGroups[rg][0] + ' ' + commentHeader

		groupRulesString = ''

		for rn in range(len(ruleGroups[rg][1])):
			
			if ((type == 'js') or (type == 'json')) and (rg == len(ruleGroups)-1) and (rn == len(ruleGroups[rg][1])-1):
				ruleNameEnd = '": 0'

			ruleNameString = ruleNameStart + ruleGroups[rg][1][rn][0] + ruleNameEnd
			ruleDefnString = commentSymbol + ' ' + ruleGroups[rg][1][rn][1]
			ruleString = ruleNameString + ' '*(columnDefn-len(ruleNameString)) + ruleDefnString
			groupRulesString += ruleString + '\n'

		groupString = headerString + emptyline + groupRulesString

		formattedRules += groupString + emptyline

	return formattedRules


# Helper function: Format the output file
def formatOutput(type):

	global firstIndent
	global secondIndent
	global commentSymbol
	global configCategoryHeaderStart
	global configCategoryHeaderEnd
	global columnDefn
	global itemStart
	global itemEnd
	global lastItemEnd

	if type == 'js' or type == 'json':
		firstIndent = indent
		columnDefn = 48
		commentSymbol = '//'
		configCategoryHeaderStart = firstIndent + '"'
		configCategoryHeaderEnd = '": {'
		itemStart = firstIndent + indent + '"'
		itemEnd = '": false,'
		lastItemEnd = '": false'
	
	else:    # if type == 'yaml':
		firstIndent = ''
		columnDefn = 41
		commentSymbol = '#'
		configCategoryHeaderStart = firstIndent
		configCategoryHeaderEnd = ':'
		itemStart = firstIndent + indent
		itemEnd = ': false'

	secondIndent = firstIndent + indent

	outputStart = prepareOutputStart(type)

	ruleConfigHeader = configCategoryHeaderStart + 'rules' + configCategoryHeaderEnd

	usageString = prepareUsageString(type)

	formattedRules = formatRules(type)
	
	if type == 'js' or type == 'json':
		outputEnd = firstIndent + '}' + emptyline + '}'
	
	else:    # if type == 'yaml':
		outputEnd = ''

	outputString = outputStart + ruleConfigHeader + emptyline + usageString + emptyline + formattedRules + outputEnd

	return outputString


# Output the file(s)

readme = ('# .eslintrc starter files' +
	      emptyline +
	      '.eslintrc starter files with all rules (set to 0) and envs (set to false) listed.' +
	      emptyline +
	      'Other options (although by no means comprehensive) are either set to false or else commented out.' +
	      emptyline +
	      'Updated on ' + datetime.datetime.now().strftime ("%Y-%m-%d") + '.' +
	      emptyline +
	      'JavaScript, JSON, and YAML versions.' +
	      emptyline +
	      'Starter files generated by a customised version of [ESLint Starter File Generator](https://github.com/i-ron-y/eslint-starter-file-generator)' +
	      emptyline +
	      '* [ESLint docs -- Configuring ESLint](https://eslint.org/docs/user-guide/configuring)\n' +
	      '* [ESLint docs -- List of available rules](https://eslint.org/docs/rules/)\n' +
	      emptyline +
          '## Credits' +
          emptyline + 
          'Inspired by, and an update of, [ESLint Reset](https://gist.github.com/cletusw/e01a85e399ab563b1236) by [cletusw](https://github.com/cletusw).')

filetypes = ['js', 'json', 'yaml']

# No arguments: Output .eslintrc.js, .eslintrc.json, and .eslintrc.yaml (and README.md)
if len(sys.argv) == 1:

	for ft in filetypes:
		
		filename = '.eslintrc.' + ft
		
		f = open(filename, 'w')
		f.write(formatOutput(ft))
		f.close()

	f = open('README.md', 'w')
	f.write(readme)
	f.close()

# 1 argument: Output .eslintrc file in either js, json, or yaml format, according to user input
elif len(sys.argv) == 2:

	if sys.argv[1] not in filetypes:

		print('Valid filetypes are: js, json, yaml\n')

	else:

		filename = '.eslintrc.' + sys.argv[1]

		f = open(filename, 'w')
		f.write(formatOutput(sys.argv[1]))
		f.close()

# 2 arguments: Output a file in either js, json, or yaml format (user inputs filetype and filename)
elif len(sys.argv) == 3:

	if sys.argv[1] not in filetypes:

		print('Valid filetypes are: js, json, yaml\n')

	else:

		filename = sys.argv[2] + '.' + sys.argv[1]

		f = open(filename, 'w')
		f.write(formatOutput(sys.argv[1]))
		f.close()	

else:

	print('Usage: python eslint-starter-file-generator.py [filetype [filename]]\n')
	print('Valid filetypes are: js, json, yaml\n')
	print('Please input filename without extension - extension is automatically the selected filetype.')

