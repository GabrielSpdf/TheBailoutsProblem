from math import sqrt

from vs.constants import VS

AC_INCR = {
    0: (0, -1),  #  u: Up
    1: (1, -1),  # ur: Upper right diagonal
    2: (1, 0),  #  r: Right
    3: (1, 1),  # dr: Down right diagonal
    4: (0, 1),  #  d: Down
    5: (-1, 1),  # dl: Down left left diagonal
    6: (-1, 0),  #  l: Left
    7: (-1, -1),  # ul: Up left diagonal
}


COST_LINE = 0.0
COST_DIAG = 0.0

INF = 9223372036854775807


def adj(a, grid_map):
    x, y = a
    if not grid_map.in_map(a):
        return []
    difficulty, seq, adj_info = grid_map.get(a)
    adj = []
    for dx, dy in AC_INCR.values():
        if not grid_map.in_map((x + dx, y + dy)):
            continue
        wall_info, seq, adj_info = grid_map.get((x + dx, y + dy))
        if wall_info == 100:
            continue
        target_xy = (x + dx, y + dy)
        if dx == 0 or dy == 0:
            step_cost = COST_LINE * difficulty
        else:
            step_cost = COST_DIAG * difficulty

        adj.append((target_xy, step_cost))
    return adj


def cost(u, v):
    x1, y1 = u
    x2, y2 = v
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def search(cost_line, cost_diag, grid_map, s, e):
    global COST_LINE, COST_DIAG
    COST_LINE = cost_line
    COST_DIAG = cost_diag

    closed = {}
    open = {}
    open[s] = 0
    parents = {}
    parents[s] = None
    while len(open) > 0:
        u = min(open, key=open.get)
        closed[u] = open[u]
        if u == e:
            break
        open.pop(u)
        for v, difficulty in adj(u, grid_map):
            g = closed[u] + difficulty
            h = cost(v, e)
            new_cost = g + h
            open_cost = open.get(v, None)
            if open_cost is not None:
                if open_cost < new_cost:
                    continue
            closed_cost = closed.get(v, None)
            if closed_cost is not None:
                if closed_cost < new_cost:
                    continue
            open[v] = new_cost
            parents[v] = (u, difficulty)

    path = []
    difficulty = 0.0
    while e:
        path.append(e)
        if parents[e]:
            e, step_difficulty = parents[e]
            difficulty += step_difficulty
        else:
            e = None

    path.reverse()
    dpath = []
    for i in range(len(path) - 1):
        i += 1
        dpath.append((path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]))

    if len(dpath) == 0:
        return dpath, 0.0

    dpath = list(map(lambda x: (x[0], x[1], False), dpath))
    x, y, f = dpath[len(dpath) - 1]
    dpath[len(dpath) - 1] = (x, y, True)
    return dpath, difficulty
