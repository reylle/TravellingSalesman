# Add prohibited path, excluding sub-paths
def add_prohibited(path, prohibiteds):
    aux = prohibiteds.copy()
    for prhbtd in aux:
        if path == prhbtd[:-1]:
            prohibiteds.remove(prhbtd)
    prohibiteds += [path]


# Solver using brute force
def brute_force_solver(target_node, vertices, adjacencies):
    best_path = ''
    best_distance = -1
    prohibiteds = [[]]

    # While all paths have not yet been tested
    while prohibiteds[0] != [target_node]:
        if not prohibiteds[0]:
            prohibiteds.pop(0)
        distance = 0
        found = False
        visited = [target_node]
        # While a full path, containing all the nodes, or an invalid path have not been found
        while len(visited) < len(vertices) and not found:
            # Try every path from the last visited node
            for node_adj in adjacencies[visited[-1]]:
                # Checks if it hasn't been visited or is a prohibited path
                if node_adj not in visited and not prohibited(visited + [node_adj], prohibiteds):
                    # Checks if this is the last node and, if so, if it has adjancy with the target node
                    if len(visited) == len(adjacencies.keys()) - 1 and target_node in adjacencies[node_adj].keys() or \
                            len(visited) < len(adjacencies.keys()) - 1:
                        distance += adjacencies[visited[-1]][node_adj]
                        visited += [node_adj]
                        found = True
                        break
            if found:
                found = False
            else:
                found = True

        # Checks if it's a full path
        if len(visited) == len(vertices):
            # Adds the path as already visited
            add_prohibited(visited[:-1], prohibiteds)
            distance += adjacencies[visited[-1]][target_node]
            visited += [target_node]
            # If this path is smaller, add it as the best so far
            if best_distance == -1 or distance < best_distance:
                best_distance = distance
                best_path = visited
        else:
            # Adds the path as already visited
            add_prohibited(visited.copy(), prohibiteds)

    # No possible solution found
    if best_distance == -1:
        return 'Inexistent solution\n'

    # Constructs the string for the output
    output = construct_output(best_path, vertices, adjacencies, best_distance)

    # Adds the algorithm name in the output
    return 'Brute Force\n' + output


# Creates a string containing the path with the vertices' values and the final distance
def construct_output(visited, vertices, adjacencies, distance):
    length = len(visited)
    output = 'Path: '

    for x in range(0, length):
        if x == (length - 1):
            output += vertices[visited[x]]
        else:
            output += vertices[visited[x]] + ' - {} -> '.format(adjacencies[visited[x]][visited[x+1]])

    output += '\n'
    output += 'Distance: {}'.format(distance)
    output += '\n'

    return output


# Gets the target's key based on it's occurency in the dict, either by key or value
def get_node(vertices, target):
    for key in vertices.keys():
        if target == key or target == vertices[key]:
            return key
    return None


# Gets the user's target from the console, using the keyboard
def get_target():
    return input('Which node is the source?\n')


# Loads the file, that needs to be in the same folder as the script 'main.py', according to the model.
# An example can be found in the file 'in.txt' where
# '#N,4' indicates the nodes' keys and values section has begun and that it'll have 4 nodes
# each line that follows indicates first the key, than a separator ',' and lastly the value
# '#A' indicates the connections between the nodes will be given at the next lines
# each line after the indicator have the source, destination and cost, separated by the same separator ','
# Obs: Blank lines can be inserted anywhere for easier reading
# If symmetric is set to True, the path from A -> B with cost X will be created in conjunction with the path
# B -> A with the same cost X
def load(filename, symmetric=True):
    file = open(filename, 'r', encoding='utf-8')

    # Find the first section indicator
    info = file.readline().split(',')
    while '#N' not in info:
        info = file.readline().split(',')

    # Get the number of vertices (useless, but was defined in the model)
    # num_vertices = info[1].replace('\n', '')
    vertices = {}
    # Find the second indicator
    while '#A\n' not in info:
        info = file.readline().split(',')
        if len(info) == 2:
            vertices[info[0]] = u'{}'.format(info[1].replace('"', '').replace("'", "").replace('\n', ''))

    # Gets the adjacencies
    adjacencies = {}
    while info:
        info = file.readline()
        if len(info) > 0:
            info = info.split(',')
        if len(info) == 3:
            if info[0] not in adjacencies.keys():
                adjacencies[info[0]] = {}
            distance = float(info[2].replace('\n', ''))
            if distance > 0:
                adjacencies[info[0]][info[1]] = distance
                # If symmetric, creates the same path for the opposite direction but with the same cost
                if symmetric:
                    if info[1] not in adjacencies.keys():
                        adjacencies[info[1]] = {}
                    adjacencies[info[1]][info[0]] = distance
            # Negative distance
            else:
                return None, None

    # Missing data
    if vertices.keys() != adjacencies.keys():
        return None, None

    # return num_vertices, vertices, adjacencies
    return vertices, adjacencies


# Solver using greedy algorithm
def greedy_solver(target_node, vertices, adjacencies):
    prohibiteds = []
    visited = []
    distance = 0

    visited += [target_node]
    while len(visited) < len(adjacencies.keys()):
        smallest = -1
        node_aux = ''
        # Try every path from the last visited node
        for node_adj in adjacencies[visited[-1]]:
            # Checks if it hasn't been visited or is a prohibited path
            if node_adj not in visited and not prohibited(visited + [node_adj], prohibiteds):
                # Checks if this is the last node and, if so, if it has adjancy with the target node
                if len(visited) == len(adjacencies.keys())-1 and target_node in adjacencies[node_adj].keys() or \
                        len(visited) < len(adjacencies.keys())-1:
                    # If the distance is smaller, store it
                    if smallest == -1 or adjacencies[visited[-1]][node_adj] < smallest:
                        smallest = adjacencies[visited[-1]][node_adj]
                        node_aux = node_adj
        # If no possible candidate was found
        if smallest == -1:
            add_prohibited(visited, prohibiteds)
            visited = [target_node]
            distance = 0
            # No possible solution found
            if prohibiteds[0] == visited:
                return 'Inexistent solution\n'
        else:
            visited += [node_aux]
            distance += smallest

    distance += adjacencies[visited[-1]][target_node]
    visited += [target_node]

    output = construct_output(visited, vertices, adjacencies, distance)

    return 'Greedy Algorithm\n' + output


# Checks if a sequency if prohibited (only leads to missing adjacencies)
def prohibited(visited, prohibiteds):
    found = False
    if not prohibiteds:
        return found
    for prohibited_list in prohibiteds:
        if len(visited) == len(prohibited_list):
            for x in range(0, len(visited)):
                if prohibited_list[x] != visited[x]:
                    break
                if x == len(visited)-1:
                    found = True
    return found


# Main function
def main():
    # generate the data with the number of vertices (not used)
    # num_vertices, vertices, adjacencies = load('in.txt', symmetric=True)
    # generate the data without the number of vertices
    vertices, adjacencies = load('in.txt', symmetric=False)

    if vertices is None or adjacencies is None:
        print('Invalid input. Missing data or negative distances.')
        return

    # get the target from user input (can be the node key or value, ex: '1' or 'Curitiba')
    target_node = None
    while target_node is None:
        target = get_target()
        target_node = get_node(vertices, target)
        if target_node is None:
            print('Inexistent node.')

    # solve using brute force
    output = brute_force_solver(target_node, vertices, adjacencies)
    print(output)
    # solve using greedy algorithm
    output = greedy_solver(target_node, vertices, adjacencies)
    print(output)

    print('Complete :3')


if __name__ == '__main__':
    main()
