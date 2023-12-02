import csv
import random
from bidict import bidict # pip install bidict

debug = False

"""
    A quick and useful program to match people given OS constraints
    This program came out of a need to pair mac users with non-mac users
"""

class Student:
    def __init__(self, name, id, grouped, opsys, groupID):
        self.name = name
        self.id = id
        self.grouped = grouped
        self.opsys = opsys
        self.groupID = groupID
        self.friends = []

    def __str__(self):
        return f'Name: {self.name},\tID: {self.id},\tGrouped: {self.grouped},\tOS: {self.opsys},\tGroupID: {self.groupID},\tFriends: {self.friends}'

    def add_friend(self, friend):
        self.friends.append(friend)
        
    def set_groupID(self, groupID):
        self.groupID = groupID
        
    def friends(self):
        return self.friends
    
    
file_path = 'Project_Groups.csv'

groups = {} # Create a dictionary of groups

pairs = {} # Create a dictionary of groups (used to create a bidict below)

pairs_responder = bidict(pairs) # Create a bijective dictionary of pairs
pairs_friend = pairs_responder.inverse

pair_candidates = [] # Remaining people who are not yet paired to a group (but who wish to do so)

# ID Dictionary
people = {}

def generateID():
    """
        Generates a ID starting from 0
    """
    i = 0
    while True:
        yield i
        i += 1

def add_group(members, groups, groupGen, people, debug=False):
    """
        Adds a group to the groups dictionary
        members: list of members ['Student1', 'Student2', ...]
        groups: dictionary of groups
        groupGen: ID generator object
        people: dictionary of people
    """
    
    groupID = next(groupGen)
    if debug:
        print(f'Group ID: {groupID}')
    groups[groupID] = members
    
    # set their group IDs in people dictionary
    for member in members:
        people[member.name].set_groupID(groupID)
    
def write_groups(groups,people):
    """
        Writes the groups to a csv file
        groups: dictionary of groups
        people: dictionary of people
    """
    with open('groups.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Group ID', 'Members'])
        for groupID in groups.keys():
            members = groups[groupID]
            member_names = ""
            for member in members:
                member_names += member.name+ "("+ str(people[member.name].id) + "-"+ str(people[member.name].opsys) +")" + ", "
            member_names = member_names[:-2] + ""
            writer.writerow([groupID , member_names])
        
# open a text file and write to it
with open('problematic.txt', 'w') as problematic:
    problematic.write('Here are the problematic peope:\n')
    with open('problematic_responder.txt', 'w') as problemres:
        problemres.write('Here are the problematic responders:\n')
        # open the csv file and read it
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)
            data = [row for row in reader]
            groupGen = generateID()
            
            for entry in data:
                stu = Student(entry[0].lower(),entry[1],entry[2],entry[3],-1) # groupID is -1 by default
                friend = entry[4].lower()
                if friend != '':  # if friend is not empty (they have friend)
                    stu.add_friend(friend)
                    # Check if the bijective map contains the person as a friend (Responder <-> Friend) (The default behaviour is to add the first person as a responder, and the second as a friend)
                    if friend not in pairs_responder:
                        pairs_responder[stu.name] = friend # Add the person as a responder, and their friend as a friend
                    people[stu.name] = stu
                else: # they are either on their own or want to pair up
                    people[stu.name] = stu
                    # Add lonely people to their own group
                    if stu.grouped == 'alone':
                        add_group([stu], groups, groupGen, people)
                    else: # people who wish to pair up
                        # Add them to the candidates pool
                        pair_candidates.append(stu.name)
            # Check if the paired people chose each other and they contain at least 1 non-macOS user
            for person in pairs_responder.keys():
                groupmate = pairs_responder[person]
                if groupmate not in people:
                    print("We have a groupmate that does not exist:", groupmate)
                    problematic.write(f'{groupmate}@sabanciuniv.edu,\n')
                    problemres.write(f'{person}@sabanciuniv.edu,\n')
                else:
                    groupmates_mate = people[groupmate].friends[0] # We have an array of friends, hence the [0]
                    # Check if they chose each other
                    if debug:
                        print(person,groupmates_mate)
                    if person != groupmates_mate:
                        print("We have a conflict of groupmates!", person, groupmates_mate)
                    # Check if there is at least 1 non-macOS user
                    elif ((people[groupmate].opsys == "macOS") and (people[groupmates_mate].opsys == "macOS")):
                        print("We have a macOS pair!",groupmate,groupmates_mate)
                    # The existing pairs now can be grouped
                    group_members = [people[groupmate],people[groupmates_mate]]
                    add_group(group_members,groups,groupGen,people)
                    
            # Now we process the pair candidates (this part could have received more love & care :), but it does the job for now)
                
            # Array of mac users
            mac_users = []
            non_mac_users = []
            # Filter the mac users from the rest
            for user in range(len(pair_candidates)):
                useros = people[pair_candidates[user]].opsys
                if useros == "macOS":
                    mac_users.append(pair_candidates[user])
                else:
                    non_mac_users.append(pair_candidates[user])
            if debug:
                print(mac_users)
                print(len(mac_users))
                print(non_mac_users)
                print(len(non_mac_users))
            
            # If we have more mac users than non-mac users
            if len(mac_users) > len(non_mac_users):
                print("We have more mac users to pair. macOS users:",len(mac_users),"non-macOS users:",len(non_mac_users))
                for non_mac_user in range(len(non_mac_users)-1):
                    # Then we will pair all non-mac users with a mac user
                    if debug:
                        print(len(non_mac_users))
                        print(non_mac_user)
                    rand_mac_user = random.randint(0,len(mac_users)-1)
                    person1 = non_mac_users[0]
                    person2 = mac_users[rand_mac_user]
                    # we have a pair!
                    if debug:
                        print("New pair:")
                        print(person1,person2)
                    # Add them as friends
                    people[person1].add_friend(person2)
                    people[person2].add_friend(person1)
                    new_pair_members = [people[person1],people[person2]]
                    # Create a new group
                    add_group(new_pair_members,groups,groupGen,people)
                    # remove paired people from list
                    pair_candidates.remove(person1)
                    non_mac_users.remove(person1)
                    pair_candidates.remove(person2)
                    mac_users.remove(person2)
                # We now have only mac users they can be even or odd
                odd_mac_users = True
                if (len(mac_users) % 2) == 0:
                    odd_mac_users = False
                for mac_user in range((len(mac_users)//2)-1):
                    rand_mac_user = random.randint(1,len(mac_users)-1)
                    person1 = mac_users[0]
                    person2 = mac_users[rand_mac_user]
                    # Perform removal
                    people[person1].add_friend(person2)
                    people[person2].add_friend(person1)
                    new_pair_members = [people[person1],people[person2]]
                    # Create a new group
                    add_group(new_pair_members,groups,groupGen,people)
                    # remove paired people from list
                    pair_candidates.remove(person1)
                    pair_candidates.remove(person2)
                    mac_users.remove(person1)
                    mac_users.remove(person2)
                    
                if odd_mac_users:
                    # group of 3
                    # add them as friends
                    for name1 in mac_users:
                        student1 = people[name1]
                        for name2 in mac_users:
                            if name1 != name2:
                                student1.add_friend(name2)
                    new_group_of_3_members = [people[i] for i in mac_users]
                    add_group(new_group_of_3_members,groups,groupGen,people)
                
            elif len(mac_users) == len(non_mac_users):
                print("We have a perfect match of non/macOS users. macOS users:",len(mac_users),"non-macOS users:",len(non_mac_users))
                for non_mac_user in range(len(non_mac_users)-1):
                    # Then we will pair all non-mac users with a mac user
                    rand_mac_user = random.randint(0,len(mac_users)-1)
                    person1 = non_mac_users[0]
                    person2 = mac_users[rand_mac_user]
                    # we have a pair!
                    if debug:
                        print("New pair:")
                        print(person1,person2)
                    # Add them as friends
                    people[person1].add_friend(person2)
                    people[person2].add_friend(person1)
                    new_pair_members = [people[person1],people[person2]]
                    # Create a new group
                    add_group(new_pair_members,groups,groupGen,people)
                    # remove paired people from list
                    pair_candidates.remove(person1)
                    non_mac_users.remove(person1)
                    pair_candidates.remove(person2)
                    mac_users.remove(person2)
            else:
                print("We have more non-mac users to pair. macOS users:",len(mac_users),"non-macOS users:",len(non_mac_users))
                for mac_user in range(len(mac_users)-1):
                    # Then we will pair all non-mac users with a mac user
                    rand_non_mac_user = random.randint(0,len(non_mac_users)-1)
                    person1 = mac_users[0]
                    person2 = non_mac_users[rand_non_mac_user]
                    # we have a pair!
                    if debug:
                        print("New pair:")
                        print(person1,person2)
                    # Add them as friends
                    people[person1].add_friend(person2)
                    people[person2].add_friend(person1)
                    new_pair_members = [people[person1],people[person2]]
                    # Create a new group
                    add_group(new_pair_members,groups,groupGen,people)
                    # remove paired people from list
                    pair_candidates.remove(person1)
                    non_mac_users.remove(person1)
                    pair_candidates.remove(person2)
                    mac_users.remove(person2)
                # We now have only non_mac users, they can be even or odd
                odd_non_mac_users = True
                if (len(non_mac_users) % 2) == 0:
                    odd_non_mac_users = False
                for non_mac_user in range((len(mac_users)//2)-1):
                    rand_non_mac_user = random.randint(1,len(non_mac_users)-1)
                    person1 = non_mac_users[0]
                    person2 = non_mac_users[rand_non_mac_user]
                    # Perform removal
                    people[person1].add_friend(person2)
                    people[person2].add_friend(person1)
                    new_pair_members = [people[person1],people[person2]]
                    # Create a new group
                    add_group(new_pair_members,groups,groupGen,people)
                    # remove paired people from list
                    pair_candidates.remove(person1)
                    pair_candidates.remove(person2)
                    non_mac_users.remove(person1)
                    non_mac_users.remove(person2)
                if odd_non_mac_users:
                    # group of 3
                    # add them as friends
                    for name1 in non_mac_users:
                        student1 = people[name1]
                        for name2 in non_mac_users:
                            if name1 != name2:
                                student1.add_friend(name2)
                    new_group_of_3_members = [people[i] for i in non_mac_users]
                    add_group(new_group_of_3_members,groups,groupGen,people)
            
            write_groups(groups,people)