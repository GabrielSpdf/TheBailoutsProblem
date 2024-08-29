import random

from pandas.core.reshape.merge import uuid

from search import search


def evaluate_sequence(
    sequence, victims, map, cost_line, cost_diag, tlim, cost_first_aid
):

    plan = []
    plan_walk_time = 0.0
    plan_rtime = tlim
    current_pos = (0, 0)
    score = 0.0
    for seq in sequence:
        victim_index = next(
            (index for (index, v) in enumerate(victims) if v[0] == seq), None
        )
        victim = victims[victim_index]

        next_plan, time_required = search(
            cost_line, cost_diag, map, current_pos, victim[1]
        )
        _, time_to_go_back = search(
            cost_line, cost_diag, map, victim[1], (0, 0)
        )
        time_required += cost_first_aid
        if plan_walk_time + time_required + time_to_go_back > plan_rtime - 40:
            continue
        score += 100 - victim[2][-1]
        plan_walk_time += time_required
        plan = plan + next_plan
        current_pos = victim[1]
    return score


def select_best(scores_dict):
    sorted_sequences = sorted(scores_dict, key=lambda x: x[0], reverse=True)
    sorted_sequences = list(map(lambda x: x[1], sorted_sequences))
    return sorted_sequences[: len(sorted_sequences) // 2]


def reproduce(sequence1, sequence2):
    child = sequence1[: len(sequence1) // 2] + sequence2[: len(sequence2) // 2]
    child = [i for n, i in enumerate(child) if i not in child[n + 1 :]]
    for seq in sequence1:
        if seq not in child:
            child.append(seq)
    return child


def reproduce_pop(population):
    children = []
    for i in range(len(population) - 1):
        sequence1 = population[i]
        sequence2 = population[i + 1]
        child = reproduce(sequence1, sequence2)
        children.append(child)
    children.append(reproduce(population[0], population[len(population) - 1]))

    return children


def initialize_random(victims, n_sequences):
    sequences = []
    vic_list = []
    for victim in victims:
        vic_list.append(victim[0])
    for _ in range(n_sequences):
        sequence = vic_list[:]
        random.shuffle(sequence)
        sequences.append(sequence)
    return sequences


def select_the_best(
    population, victims, map, cost_line, cost_diag, tlim, cost_first_aid
):
    scores = []
    for sequence in population:
        score = evaluate_sequence(
            sequence,
            victims,
            map,
            cost_line,
            cost_diag,
            tlim,
            cost_first_aid,
        )
        scores.append((score, sequence))

    return max(scores, key=lambda x: x[0])


def seq_list2dict(seqs, victims):
    victim_list = []
    for seq in seqs:
        for victim in victims:
            if victim[0] == seq:
                victim_list.append(victim)
                break
    return victim_list

