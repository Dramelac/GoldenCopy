# GoldenCopy

You encounter limitations with your golden tickets (DACLs, detection)? 
GoldenCopy retrieves all the information (ID, groups, etc) of a specific user in a neo4j database (bloodhound) and prepares the mimikatz/ticketer command to impersonate his permissions.

## Installation

**GoldenCopy** works with python >= 3.6

### Using pip
```bash
python3 -m pip install GoldenCopy
```

### From source
```bash
git clone https://github.com/Dramelac/GoldenCopy.git
cd GoldenCopy
python3 setup.py install
```

## Examples

- Impersonating 'john@domain.local' using default localhost neo4j (neo4j/exegol4thewin) database:
```
goldencopy.py john@domain.local
```
- Custom neo4j DB:
```
goldencopy.py -b neo4j.server.local -u neo4juser -p neo4jpass john@domain.local
```
- Adding stealth mode:
```
goldencopy.py -b bolt://neo4j.server.local:7687 -u neo4juser -p neo4jpass -s john@domain.local
```
- Using specific tools:
```
goldencopy.py -t mimikatz john@domain.local
```
```
goldencopy.py -t ticketer john@domain.local
```

## Usages

```
usage: goldencopy.py [-h] [-v] [-b BOLT] [-u USERNAME] [-p PASSWORD]
                     [-t {mimikatz,ticketer,all}] [-s] [-k KRBTGT] [-g GROUPS]
                     [--sid SID] [-c CUSTOM]
                     target_user

GoldenCopy - Copy the properties and groups of a user from neo4j to create an
identical golden ticket

positional arguments:
  target_user           Target user to copy (format: <username>[@<domain>])

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose logging

Neo4j connection configuration:
  -b BOLT, --bolt BOLT  Neo4j bolt connexion (default: bolt://127.0.0.1:7687)
  -u USERNAME, --username USERNAME
                        Neo4j username (default : neo4j)
  -p PASSWORD, --password PASSWORD
                        Neo4j password (default : exegol4thewin)

Ticket configuration:
  -t {mimikatz,ticketer,all}, --tools {mimikatz,ticketer,all}
                        Ticket creation tools (default : all)
  -s, --stealth         Stealth mode (default : disable)
  -k KRBTGT, --krbtgt KRBTGT
                        KRBTGT RC4,AES Key

Advanced ticket configuration:
  -g GROUPS, --groups GROUPS
                        Manually add extra group ids (can be separated by
                        commas)
  --sid SID             Manually add extra sids (SID history) (can be
                        separated by commas)
  -c CUSTOM, --custom CUSTOM
                        Custom options
```