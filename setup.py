from setuptools import setup

setup(
	name = "JiraGenerator",
	version = "0.0.1",
	packages= ["generator"],
	entry_points= {
	"console_scripts": [
		"jiragen = generator.__main__:main"
		]
	},
	install_requires = ["jsonschema", "jira"],
	include_package_data=True
)