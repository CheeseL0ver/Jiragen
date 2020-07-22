# Jiragen

#### A Python CLI tool for automated Jira Task creation.

## Overview

This CLI tool will create tasks in Jira, based on a supplied JSON file of defined tasks.

## Requirements

- **Python** version 3.7.2 and **pip**.
- An instance of **Jira Server**
- A Jira service account

> **NOTE:** All testing performed has been for Python version 3.7.2, but any version of Python 3.7.\* **_should_** work.

> **NOTE:** Currently the tool only works with [Jira Server](https://docs.atlassian.com/software/jira/docs/api/REST/8.5.4/) and **_not_** Jira Cloud.

## Configuration

### Variable(s)

- After you have downloaded the code you must change the `self.jiraURL` variable in the `generator/__main__.py` file before running the install. This url will look something similar to this `https://jira.<YOUR-DOMAIN>.com/`.

> **NOTE:** Upon running the tool a user will be prompted for a username and password of a Jira Server service account. This username and password is than stored in the `username` and `password` varibles for the remaining runtime of the program. You can hardcode these variables if you prefer, **HOWEVER** this is **not recommended**, as it would be easy for anyone to create tasks using someone else's credentials!

## Install

The code has been packaged in a way that allows for it to be installed as a Python module. To install navigate to the root directory of the project and run the following:

```
$ pip install .
```

After running the above command an executable file named `jiragen` will be created and stored on your device. The storage location varies depending on your operating system. You will need to ensure this storage location directory is included in your system's **PATH** variable. This will allow for execution from anywhere within the system.

> **NOTE:** All testing performed has been for Python version 3.7.2, but any version of Python 3.7.\* **_should_** work just fine.

## Usage

You can run the tool using the following command:

```
$ jiragen -f PATH/TO/TASKFILE
```

> **NOTE:** You will need a JSON document of defined tasks. For information about the doucment format see the [format](#format) section below.

## JSON Format {#format}

### File Attributes

The JSON file uses a few attributes for creating tasks. Below you will find an explanation for each attribute.

| Attribute Name | Description                                        | Required | Default Value |
| -------------- | -------------------------------------------------- | -------- | ------------- |
| project        | The name of the Jira project the task belongs to   | Yes      |               |
| summary        | The name of the task when viewed in Jira           | Yes      |               |
| epic_link      | The name of the Jira epic link the task belongs to | Yes      |               |
| story_points   | The number of story points given to the task       | No       | 1             |
| assignee       | The user in Jira ssigned the task                  | No       | ""            |
| priority       | The name of the priority of the task               | No       | "2-Normal"    |
| description    | The description of the task                        | No       | ""            |
| components     | The components attached to the task                | No       | []            |
| reporter       | The user in Jira who created the task              | Yes      |               |
| issue_type     | The type of the issue                              | Yes      |               |

### File Format

Jiragen verifies the JSON file you provide against a set schema. This file must be in the following format:

```
[{

"project": "PROJECT",

"summary": "SUMMARY",

"epic_link": "EPIC_LINK",

"story_points":  STORY_POINTS,

"assignee": "ASSIGNEE",

"priority": "PRIORITY",

"description": "DESCRIPTION",

"components": ["COMPONENT1","COMPONENT2"],

"reporter": "REPORTER",

"issue_type": "ISSUE_TYPE"

}
]
```

> **NOTE:** The schema is defined in the `generator/schema.json` file.

An example JSON is provided below:

```
[{
      "project": "JIRAGEN",

      "summary": "Blocked Task",

      "epic_link": "Internal-305",

      "story_points": 1,

      "assignee": "user@domain.com",

      "priority": "2— Normal",

      "description": "Normal Task",

      "components": ["Development", "Updates"],

      "reporter": "reporter@domain.com",

      "issue_type": "Task",

      "linked_issues": [{"blockedBy":"Blocker Task"}]
},
{
      "project": "JIRAGEN",

      "summary": "Blocker Task",

      "epic_link": "Internal-305",

      "story_points": 9,

      "assignee": "reporter@domain.com",

      "priority": "4— Urgent",

      "description": "Urgent Task",

      "components": ["Development", "Failure"],

      "reporter": "user@domain.com",

      "issue_type": "Task"
}
]
```

The above JSON file would create two tasks:

1. Blocked Task
2. Blocker Task

With the following attributes:
| Summary | Project | Story Points | Assignee | Priority | Description |Components | Reporter | Issue Type | Link |
|---|---|---|---|---|---|---|---|---|---|
| Blocked Task | Internal | 1 | user@domain.com | 2— Normal | Normal Task | "Development", "Updates" | reporter@domain.com | Task | blockedBy: Blocker Task |
| Blocker Task | Internal | 9 | reporter@domain.com | 4— Urgent | Urgent Task | "Development", "Failure" | user@domain.com | Task | blocks: Blocked Task |

> **NOTE:** When linking the tasks we did not have to specifiy that one task blocks the other. Jira will handle that once a task is created.

## Contributing

If your interested in adding a feature, or fixing a bug feel free to submit a PR, if you are unsure if it fits you can open an issue to discuss it first.

## Licensing

- Source code Copyright &copy; 2020 Shandon Anderson.

  ![GPL3](https://www.gnu.org/graphics/lgplv3-147x51.png)

  This program is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses>.

## Credits

Special thanks to all the contributors behind the [JIRA Python Library](https://github.com/pycontribs/jira). Without this library Jiragen would not exist.
