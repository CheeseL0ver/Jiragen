
#!/usr/local/bin/python3.7

#########################################################
# Version: Extreme Alpha 0.1.0
# Created by: Shandon Anderson
# Last Modified: 03/05/2019
# Description: Automatic creation of Jira tasks.
#########################################################

import json, sys, getpass, argparse, os
from jsonschema import validate
from jsonschema import exceptions
from jira import JIRA
from jira.exceptions import JIRAError

class Util():
    def __init__(self):
        """Constructor for the Util class."""
        self.jsonFile = None
        self.parseArgs()
        self.run()

    def parseArgs(self):
        """Parses the arguments passed when running the script."""
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter
            ,description="""Python based Jira task generator.\nConfluence Link:""",prog="jirgen")

        parser.add_argument("-f", "--file", action='store', help="Tasks file in JSON format",metavar="JSON", required=True)

        parser.add_argument("-v", "--version", action='version', help='Show the program\'s version number and JiraURL',version="Jiragen 0.1.0\nJiraUrl: %s" % Main(noRun=True).jiraURL)

        args = parser.parse_args()

        if (args.file):
            self.jsonFile = args.file

    def run(self):
        Main(jsonFile=self.jsonFile)

class Main():
  """Main class for task creation"""

  def __init__(self, jsonFile=None, noRun=False):
    """Constructor for Main class."""
    self.jiraURL = ''

    if noRun == False:
        username = input('Username:')
        password = getpass.getpass('Password:')
        self.jsonFile = jsonFile

        self.j = None

        try: #Validate User
            self.j = JIRA(self.jiraURL, basic_auth=(username,password), max_retries=1)
        except JIRAError as error:
            if (error.status_code == 401 or error.status_code == 403):
                print('Jira login failed. Please check your username and password.')
                sys.exit()
            else:
                print('An error occured. Status code: %s' % error.status_code)

        self.tasks = []
        self.linkedIssues = []
        self.createdIssues = []
        self.confirmedLinks = []
        self.returnStatuses = []
        self.updateLinks = []
        self.taskJson = []
        self.main()

  def loadTasks(self):
    """Loads task objects from input file."""

    print('Loading task from file...')

    schema = os.path.join(os.path.dirname(__file__), 'schema.json') #Read schema JSON
    with open(schema, 'r') as fp:
        schemaJson = fp.read()
    schemaJson = json.loads(schemaJson)

    try: #Read task JSON
      with open(self.jsonFile, 'r') as fp:
          try:
            self.taskJson = (json.loads(fp.read()))
          except json.decoder.JSONDecodeError as err:
            print("Task JSON Load Error: %s\nError Line: %s\nError Column: %s" % (err.msg, err.lineno, err.colno))
            sys.exit()

      for task in self.taskJson:
        try:
          validate(task, schemaJson)
        except exceptions.ValidationError as err:
          print("Task JSON Validation Error: %s" % err.message)
          sys.exit()

    except FileNotFoundError as err:
      print('File \'%s\' does not exist.' % self.jsonFile)
      sys.exit()

  def buildTasks(self):
    """Creates a list of task objects from the objects read in
    from the file."""

    print('Generating tasks...')
    for task in self.taskJson:

      try:
        story_points = task['story_points']
      except KeyError:
        story_points = 1

      try:
        assignee = {'name': task['assignee']}
      except KeyError:
        assignee = {'name': ''}

      try:
        priority = {'name': task['priority']}
      except KeyError:
        priority = {'name': '2— Normal'}

      try:
        description = task['description']
      except KeyError:
        description = ''

      try:
        components = [{'name': component} for component in task['components']]
      except KeyError:
        components = []

      issue = {
        'project': task['project'],
        'summary': task['summary'],
        'customfield_10201': task['epic_link'],
        'customfield_10300': story_points,
        'assignee': assignee,
        'priority':  priority,
        'description': description,
        'components': components,
        'reporter': {'name': task['reporter']},
        'issuetype': task['issue_type']
      }
      self.tasks.append(issue)

  def createIssues(self):
    """Creates a Jira issue for each task object in the tasks list."""

    print('Creating tasks in Jira...')
    tasks = [task for task in self.tasks] #List of task dicts
    self.returnStatuses = self.j.create_issues(field_list=tasks)

    self.createdIssues = [ (status['status'], (status['issue'].key if status['status'] == 'Success' else False) , status['input_fields']['summary']) for status in self.returnStatuses]

  def linkIssues(self):
    """Searches for links between issues in the specified file."""

    print('Checking for links...')

    for task in self.taskJson: #Read links from task JSON
      try:
        link = ({'issuelinks': [{'type': links} for links in task['linked_issues']]
        }, task['summary'])
        self.linkedIssues.append(link)
      except KeyError:
        self.linkedIssues.append(None)


    for issueLink in self.linkedIssues:
      if issueLink == None: # No link
        pass
      else:
        issueLinks = issueLink[0]['issuelinks']
        for link in issueLinks:
         #check Link
          linkType = list(link['type'].keys())[0]
          toLink = list(link['type'].values())[0]
          baseTask = issueLink[1]
          if self.findTask(toLink, baseTask):
            toLinkKey = self.getKey(toLink) # current task's id
            baseTaskKey = self.getKey(baseTask) # link to task id

            self.confirmedLinks.append((linkType, baseTaskKey, toLinkKey))

  def getKey(self, summary):
    """Returns the key of an issue with specified summary from the
    list of newly generated Jira tasks or from previously created tasks."""

    #Task was created from current running JSON
    for link in self.returnStatuses:
      if link['input_fields']['summary'] == summary:
        return link['issue'].key

    #Task to be linked already exists, search Jira for its key
    try:
        result = self.j.search_issues('summary ~ \"%s\"' % summary)
        return (result[0].key)

    except JIRAError as e:
        print(e)
        print("Desired link issue %s was not found in Jira. Exiting..." % summary)
        sys.exit()

  def findTask(self, toLink, baseTask):
    """Determines if the tasks to be linked were both created."""
    for task in self.createdIssues:
      if toLink in task[0] and 'Error' in task[0]: # Task to be linked to not was created
        return False
    for task in self.createdIssues:
      if baseTask in task[0] and 'Error' in task[0]: # Task was not created
        return False
    return True # Both the task and the link to task where created

  def generateUpdateLinks(self):
    """Creates a links in proper Jira format."""
    print('Generating links...')

    for link in self.confirmedLinks: #link types supported: blockedBy, blocks, clones, duplicates, escalates, split
        type = link[0]
        if type == 'blockedBy':
            self.updateLinks.append((link[1],{
                'add': {
                    'type': {
                        "name": 'Blocks',
                        "inward": "is blocked by",
                        "outward": "blocks"
                    },
                    "inwardIssue":{
                        "key": link[2]
                    }
                }
            }))

        elif type == 'blocks':
                self.updateLinks.append((link[1], {
                    'add': {
                        'type': {
                            "name": 'Blocks',
                            "inward": "is blocked by",
                            "outward": "blocks"
                        },
                        "outwardIssue": {
                            "key": link[2]
                        }
                    }
                }))

        elif type == 'clones':
                self.updateLinks.append((link[1], {
                    'add': {
                        'type': {
                            "name": 'Cloners',
                            "inward": "is cloned by",
                            "outward": "clones"
                        },
                        "outwardIssue": {
                            "key": link[2]
                        }
                    }
                }))

        elif type == 'clonedBy':
            self.updateLinks.append((link[1],{
                'add': {
                    'type': {
                        "name": 'Cloners',
                        "inward": "is cloned by",
                        "outward": "clones"
                    },
                    "inwardIssue":{
                        "key": link[2]
                    }
                }
            }))

        elif type == 'duplicates':
                self.updateLinks.append((link[1], {
                    'add': {
                        'type': {
                            "name": 'Duplicate',
                            "inward": "is duplicated by",
                            "outward": "duplicates"
                        },
                        "outwardIssue": {
                            "key": link[2]
                        }
                    }
                }))

        elif type == 'duplicatedBy':
            self.updateLinks.append((link[1],{
                'add': {
                    'type': {
                        "name": 'Duplicate',
                        "inward": "is duplicated by",
                        "outward": "duplicates"
                    },
                    "inwardIssue":{
                        "key": link[2]
                    }
                }
            }))

        elif type == 'escalates':
                self.updateLinks.append((link[1], {
                    'add': {
                        'type': {
                            "name": 'Escalated',
                            "inward": "Escalates",
                            "outward": "Escalated by"
                        },
                        "inwardIssue": {
                            "key": link[2]
                        }
                    }
                }))

        elif type == 'escalatedBy':
            self.updateLinks.append((link[1],{
                'add': {
                    'type': {
                        "name": 'Escalated',
                        "inward": "Escalates",
                        "outward": "Escalated by"
                    },
                    "outwardIssue":{
                        "key": link[2]
                    }
                }
            }))

        elif type == 'splitTo':
                self.updateLinks.append((link[1], {
                    'add': {
                        'type': {
                            "name": 'Issue split',
                            "inward": "split from",
                            "outward": "split to"
                        },
                        "outwardIssue": {
                            "key": link[2]
                        }
                    }
                }))

        elif type == 'splitFrom':
            self.updateLinks.append((link[1],{
                'add': {
                    'type': {
                        "name": 'Issue split',
                        "inward": "split from",
                        "outward": "split to"
                    },
                    "inwardIssue":{
                        "key": link[2]
                    }
                }
            }))

        elif type == 'causes':
                self.updateLinks.append((link[1], {
                    'add': {
                        'type': {
                            "name": 'Problem/Incident',
                            "inward": "is caused by",
                            "outward": "causes"
                        },
                        "outwardIssue": {
                            "key": link[2]
                        }
                    }
                }))

        elif type == 'causedBy':
            self.updateLinks.append((link[1],{
                'add': {
                    'type': {
                        "name": 'Problem/Incident',
                        "inward": "is caused by",
                        "outward": "causes"
                    },
                    "inwardIssue":{
                        "key": link[2]
                    }
                }
            }))

        elif type == 'relatesTo':
                self.updateLinks.append((link[1], {
                    'add': {
                        'type': {
                            "name": 'Relates',
                            "inward": "relates to",
                            "outward": "relates to"
                        },
                        "outwardIssue": {
                            "key": link[2]
                        }
                    }
                }))

        else:
            return

  def update(self):
    """Updates the task links in Jira using formatted links in updateLinks list."""

    print('Updating links in Jira...')

    for link in self.updateLinks:
      issue = self.j.issue(link[0]) # Instance of desired Jira issue

      issue.update(issuelinks=[link[1]]) # Update the issue's link

  def main(self):
    """Main program sequence."""

    self.loadTasks() # Read task file
    self.buildTasks() # Format tasks to Jira format
    self.createIssues() # Create issues within Jira
    self.linkIssues() # Check for supported task links
    self.generateUpdateLinks() # Generate update links in Jira format
    self.update() # Update task links in Jira

def main():
  """Main method to be called by CLI tool."""
  Util()
  
