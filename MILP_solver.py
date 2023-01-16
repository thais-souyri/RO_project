from RO22 import *

import cvxpy as cp


### Déclaration des données ###

def dimensions(instance):
    nb_jobs = instance.nb_jobs()
    nb_tasks = instance.nb_tasks()
    nb_machines = instance.nb_machines()
    nb_operators = instance.nb_operators
    return nb_tasks, nb_jobs, nb_machines, nb_operators


nb_tasks, nb_jobs, nb_machines, nb_operators = dimensions(Instance_tiny)

def w(instance):
    w=[]
    jobs = instance.jobs
    for job in jobs:
        w.append(job.weight)
    return w

w = w(Instance_tiny)

alpha = Instance_tiny.alpha
beta = Instance_tiny.beta

def r_j(instance):
    r_j = []
    for j in range(0, nb_jobs):
        r_j.append(instance["jobs"]["release_date"])
    return r_j


def p_i(instance):
    p_i = []
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
    M_iom = [[[0 for m in range(0, nb_machines)] for o in range(0, nb_operators)] for i in range(0, nb_tasks)]
    for i in range(0, nb_tasks):
        for o in range(0, nb_operators):
            for m in range(0, nb_machines):
                if m in instance["tasks"][i]["operators"] and o in instanceinstance["tasks"][i]["operators"]:
                    M_iom[i][o][m] = 1
    return M_iom


T = 30  # final time upper bound

### Creation des variables et contraintes###

constraints = []

X = [[[[] for m in range(nb_machines)] for o in range(nb_operators)] for i in range(nb_tasks)]

for i in range(nb_tasks):
    for o in range(nb_operators):
        for m in range(nb_machines):
            for t in range(T):
                X[i][o][m].append(cp.Variable(boolean=True))

C = cp.Variable(Instance_tiny.nb_tasks(), boolean=False)
B = cp.Variable(Instance_tiny.nb_tasks(), boolean=False)
p = []
for i in range(Instance_tiny.nb_tasks()):
    p.append(Instance_tiny.tasks[i].processing_time)
constraints.append(C == B + p)

Bj = cp.Variable(Instance_tiny.nb_jobs(), boolean=False)
Cj = cp.Variable(Instance_tiny.nb_jobs(), boolean=False)
Tj = cp.Variable(Instance_tiny.nb_jobs(), boolean=False)
Uj = cp.Variable(Instance_tiny.nb_jobs(), boolean=True)

d = []
for j in range(Instance_tiny.nb_jobs()):
    d.append(Instance_tiny.jobs[j].release_date)
constraints.append(Tj >= Cj - d)
constraints.append(Tj >= 0)
constraints.append(Uj * 100 >= Tj)

for j in range(Instance_tiny.nb_jobs()):
    constraints.append(Bj[j] == B[Instance_tiny.jobs[j].task_sequence[0] - 1])
    constraints.append(Bj[j] >= B[Instance_tiny.jobs[j].release_date])
    constraints.append(Bj[j] >= B[Instance_tiny.jobs[j].release_date])
    constraints.append(Cj[j] == C[Instance_tiny.jobs[j].task_sequence[-1] - 1])

### Définition de la fonction objectif ## #

term = []
for j in range(nb_jobs):
    term.append(w[j]*(Cj[j]+alpha*Uj[j]+beta*Tj[j]))

obj = cp.Minimize(cp.sum(term))

### Définition et résolution du problème ###

prob = cp.Problem(obj, constraints)
prob.solve(solver=cp.ECOS_BB)