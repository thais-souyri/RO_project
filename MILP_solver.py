from RO22 import *

import cvxpy as cp


### Déclaration des données ###

def dimensions(instance):
    nb_jobs = instance.nb_jobs()
    nb_tasks = instance.nb_tasks()
    nb_machines = instance.nb_machines()
    nb_operators = instance.nb_operators
    return nb_tasks, nb_jobs, nb_machines, nb_operators


dim = dimensions(Instance_tiny)


def r_j(instance):
    r_j = []
    nb_jobs = instance["parameters"]["size"]["nb_jobs"]
    for j in range(0, nb_jobs):
        r_j.append(instance["jobs"]["release_date"])
    return r_j


def p_i(instance):
    p_i = []
    nb_tasks = instance["parameters"]["size"]["nb_tasks"]
    for i in range(0, nb_tasks):
        p_i.append(instance["tasks"]["processing_time"])
    return p_i


def delta(instance):
    nb_jobs, nb_tasks, nb_machines, nb_operators = dimensions(instance)
    mat = [[0 for i in range(nb_tasks)] for j in range(nb_jobs)]
    for job in instance.jobs:
        task_sequence = job.task_sequence
        for task in task_sequence:
            mat[task - 1][job.index - 1] = 1
    return mat


delta = delta(Instance_tiny)


def M_iom(instance):
    nb_tasks = instance["parameters"]["size"]["nb_tasks"]
    nb_operators = instance["parameters"]["size"]["nb_operators"]
    nb_machines = instance["parameters"]["size"]["nb_machines"]
    M_iom = [[[0 for m in range(0, nb_machines)] for o in range(0, nb_operators)] for i in range(0, nb_tasks)]
    for i in range(0, nb_tasks):
        for o in range(0, nb_operators):
            for m in range(0, nb_machines):
                if m in instance["tasks"][i]["operators"] and o in instanceinstance["tasks"][i]["operators"]:
                    M_iom[i][o][m] = 1
    return M_iom


T = 30  # final time upper bound

### Creation des variables ###

C = cp.Variable(Instance_tiny.nb_tasks(), boolean=False)
B = cp.Variable(Instance_tiny.nb_tasks(), boolean=False)
p = []
for i in range(Instance_tiny.nb_tasks()):
    p.append(Instance_tiny.tasks[i].processing_time)
constr1 = (C == B + p)

Bj = cp.Variable(Instance_tiny.nb_jobs(), boolean=False)
Cj = cp.Variable(Instance_tiny.nb_jobs(), boolean=False)
Tj = cp.Variable(Instance_tiny.nb_jobs(), boolean=False)
Uj = cp.Variable(Instance_tiny.nb_jobs(), boolean=True)

d = []
for j in range(Instance_tiny.nb_jobs()):
    d.append(Instance_tiny.jobs[j].release_date)
constrTj = (Tj >= Cj - d)
constrTj2 = (Tj >= 0)
constrUj = (Uj * 100 >= Tj)

constr = []
for j in range(Instance_tiny.nb_jobs()):
    constrb = (Bj[j] == B[Instance_tiny.jobs[j].tasks_sequence[0] - 1])
    constrb2 = (Bj[j] >= B[Instance_tiny.jobs[j].release_date])
    constrT1 = (Bj[j] >= B[Instance_tiny.jobs[j].release_date])
    constrc = (Cj[j] == C[Instance_tiny.jobs[j].tasks_sequence[-1] - 1])
    constr.append(constrb)
    constr.append(constrb2)
    constr.append(constrc)
