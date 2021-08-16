import random
import pickle
from tkinter import *
import matplotlib.pyplot as plt
import numpy as np

from Functions import *
from Path import Path
from Segment import Segment
from Point import Point

FILE_NAME = 'zad1.txt'
POPULATION_SIZE = 1000

CROSSOVER_CHANCE = 0.6
MUTATION_CHANCE = 0.1
MUTATION_DISTANCE = 1
EPOCHES_NUMBER = 7

MAX_SEGMENTS_NUMBER = 6
MIN_SEGMENTS_NUMBER = 1
MAX_SEGMENT_LENGTH = 6
MIN_SEGMENT_LENGTH = 1
TOURNAMENT_SIZE = 200

def tournament(ind_list):
    tournament_list = []

    for j in range(0, TOURNAMENT_SIZE):
        index = random.randint(0, len(ind_list) - 1)
        tournament_list.append(ind_list[index])

    return min(tournament_list, key=lambda ind: ind.fitness)


def roulette(ind_list):
    tuples_list = [] 
    first_value = 0
    last_value = 0
    
    fitness_sum = sum((1 / ind.fitness) for ind in ind_list)
    fitness_avg = fitness_sum / len(ind_list)

    for i in range(0, len(ind_list)):
        probability = 1 / ind_list[i].fitness / fitness_sum 
        last_value = last_value + probability
        tuples_list.append((first_value, last_value))
        first_value = last_value

    rand = random.random()
    for i in range(0, len(tuples_list)):
        if tuples_list[i][0] < rand and rand < tuples_list[i][1]:
            winner = ind_list[i]

    return winner


def crossover(parent1, parent2):
    probability = random.random()
    if probability > 1 - CROSSOVER_CHANCE:
        rand = random.randint(0, len(parent1.paths))
        new_paths_list = parent1.paths[:rand] + parent2.paths[rand:]
        
        child = Individual()
        child.height = parent1.height
        child.width = parent1.width
        child.paths = new_paths_list

        return child
    else: 
        return parent1 if random.randint(1,2) == 1 else parent2


class Individual:

    def __init__(self):
        self.paths = []
        self.fitness = 0
        self.width = 0
        self.height = 0

    def __str__(self):
        return 'Individual: fitness - %d' % (self.fitness)

    def read_file(self, file_name):
        with open(file_name) as file:
            size_arr = file.readline().split(';')
            self.width = int(size_arr[0])
            self.height = int(size_arr[1])

            while True:
                line = file.readline()
                if not line:
                    break
                coords_arr = line.rstrip('\n').split(';')

                start = Point(int(coords_arr[0]), int(coords_arr[1]))
                end = Point(int(coords_arr[2]), int(coords_arr[3]))
                self.paths.append(Path(start, end))

            file.close()

    def generate_random(self):
        direction = ['u', 'd', 'l', 'r']

        for path in self.paths:
            current = path.start
            end = path.end

            rand_direction = direction[random_int(0, 3)]
            horizontal = True if (rand_direction == 'l' or rand_direction == 'r') else False
            segments_num = random.randint(MIN_SEGMENTS_NUMBER, MAX_SEGMENTS_NUMBER)

            for i in range(segments_num): 
                rand_step =  random_int(MIN_SEGMENT_LENGTH, MAX_SEGMENT_LENGTH)
                if horizontal:
                    rand_direction = direction[random_int(2, 3)]
                    next_x = (current.x + rand_step) if rand_direction == 'r' else (current.x - rand_step)
                    path.segments.append(Segment(rand_direction, rand_step))
                    current = Point(next_x, current.y)
                else:
                    rand_direction = direction[random_int(0, 1)]
                    next_y = (current.y + rand_step) if rand_direction == 'u' else (current.y - rand_step)
                    path.segments.append(Segment(rand_direction, rand_step))
                    current = Point(current.x, next_y)
                horizontal = not horizontal

            if current != end:
                # if points are on the same line
                if current.x == end.x:
                    if current.y > end.y: 
                        path.segments.append(Segment('d', current.y - end.y))
                    else: 
                        path.segments.append(Segment('u', end.y - current.y))
                    continue

                if current.y == end.y:
                    if current.x > end.x: 
                        path.segments.append(Segment('l', current.x - end.x))
                    else: 
                        path.segments.append(Segment('r', end.x - current.x))
                    continue

                # if points are not on the same line
                if horizontal:
                    if current.x < end.x: path.segments.append(Segment('r', end.x - current.x))
                    else: path.segments.append(Segment('l', current.x - end.x))

                    if current.y < end.y: path.segments.append(Segment('u', end.y - current.y))
                    else: path.segments.append(Segment('d', current.y - end.y))

                else:
                    if current.y < end.y: path.segments.append(Segment('u', end.y - current.y))
                    else: path.segments.append(Segment('d', current.y - end.y))

                    if current.x < end.x: path.segments.append(Segment('r', end.x - current.x))
                    else: path.segments.append(Segment('l', current.x - end.x))


    def draw_plot(self):
        for path in self.paths: 
            x = []
            y = []
            x.append(path.start.x)
            y.append(path.start.y)
            current = path.start
            for segment in path.segments:
                if segment.direction == 'u':
                    next_point = Point(current.x, current.y + segment.step)
                elif segment.direction == 'd':
                    next_point = Point(current.x, current.y - segment.step)
                elif segment.direction == 'l':
                    next_point = Point(current.x - segment.step, current.y)
                elif segment.direction == 'r':
                    next_point = Point(current.x + segment.step, current.y)
                color = path.color
                x.append(next_point.x)
                y.append(next_point.y)
                current = next_point

            x.append(path.end.x)
            y.append(path.end.y)
            plt.grid(True)
  
            plt.plot(x,y, color = color, markerfacecolor= color, linewidth=3, markersize=8, marker='o')

        plt.xticks(np.arange(0, self.width, 1.0))
        plt.yticks(np.arange(0, self.height, 1.0))
        plt.show()


    def assess_fitness(self):
        intersections_count = 0
        for i in range(len(self.paths) - 1):
            current1 = self.paths[i].start #Point object

            for j in range(i + 1, len(self.paths)):
                current2 = self.paths[j].start

                for segment1 in self.paths[i].segments:
                
                    if segment1.direction == 'u': end1 = Point(current1.x, current1.y + segment1.step)
                    if segment1.direction == 'd': end1 = Point(current1.x, current1.y - segment1.step)
                    if segment1.direction == 'l': end1 = Point(current1.x - segment1.step, current1.y)
                    if segment1.direction == 'r': end1 = Point(current1.x + segment1.step, current1.y)


                    for segment2 in self.paths[j].segments:

                        if segment2.direction == 'u': end2 = Point(current2.x, current2.y + segment2.step)
                        if segment2.direction == 'd': end2 = Point(current2.x, current2.y - segment2.step)
                        if segment2.direction == 'l': end2 = Point(current2.x - segment2.step, current2.y)
                        if segment2.direction == 'r': end2 = Point(current2.x + segment2.step, current2.y)

                        p1 = current1
                        q1 = end1
                        p2 = current2
                        q2 = end2
                        if  doIntersect(p1, q1, p2, q2) == True: intersections_count+=1
                        current2 = end2

                    current1 = end1
                    current2 = self.paths[j].start
                
                current1 = self.paths[i].start

        # sumaryczna długość ścieżek - done
        sum_paths_length = 0
        for path in self.paths:
            for segment in path.segments:
                sum_paths_length += segment.step


        # sumaryczna liczba segmentów tworzących ścieżki - done
        segments_num = 0
        for path in self.paths:
            segments_num += len(path.segments)

        
        # liczba ścieżek poza płytką 
        segments_num_outside = 0 
        for path in self.paths:
            current = path.start

            for segment in path.segments:
                if segment.direction == 'u':
                    next_point = Point(current.x, current.y + segment.step)

                elif segment.direction == 'd':
                    next_point = Point(current.x, current.y - segment.step)

                elif segment.direction == 'l':
                    next_point = Point(current.x - segment.step, current.y)

                elif segment.direction == 'r':
                    next_point = Point(current.x + segment.step, current.y)

                if 0 > next_point.y or next_point.y > self.height - 1 or 0 > next_point.x or next_point.x > self.width - 1 or 0 > current.y or current.y > self.height - 1 or 0 > current.x or current.x > self.width - 1:
                    segments_num_outside += 1

                current = next_point

        self.fitness = intersections_count * 12 + segments_num_outside * 20 + sum_paths_length + segments_num


    def mutate(self):
        probability = random.random()

        if (probability > 1 - MUTATION_CHANCE):
            times = random.randint(1, len(self.paths) - 1)
            for i in range(times):
                rand_path = random.randint(0, len(self.paths) - 1)

                if len(self.paths[rand_path].segments) > 2: 
                    rand_segment = random.randint(1, len(self.paths[rand_path].segments) - 2)
                    mutation = random.randint(0,1)
                    distance = random.randint(1, MUTATION_DISTANCE)

                    if mutation == 1:
                        previous = self.paths[rand_path].segments[rand_segment - 1]
                        next = self.paths[rand_path].segments[rand_segment + 1]
                        current = self.paths[rand_path].segments[rand_segment]
                        is_possible = previous.step > MUTATION_DISTANCE and next.step > MUTATION_DISTANCE

                        if previous.direction == next.direction and current.direction != previous.direction and current.direction != next.direction and  is_possible:
                            previous.step -= MUTATION_DISTANCE
                            next.step += MUTATION_DISTANCE
                        
                        elif previous.direction != next.direction and current.direction != previous.direction and current.direction != next.direction and is_possible:
                            previous.step += MUTATION_DISTANCE
                            next.step += MUTATION_DISTANCE

                    else:
                        previous = self.paths[rand_path].segments[rand_segment - 1]
                        next = self.paths[rand_path].segments[rand_segment + 1]
                        current = self.paths[rand_path].segments[rand_segment]
                        is_possible = previous.step > MUTATION_DISTANCE and next.step > MUTATION_DISTANCE

                        if previous.direction == next.direction and current.direction != previous.direction and current.direction != next.direction and is_possible:
                            previous.step += MUTATION_DISTANCE
                            next.step -= MUTATION_DISTANCE
                        
                        elif previous.direction != next.direction and current.direction != previous.direction and current.direction != next.direction and is_possible:
                            previous.step -= MUTATION_DISTANCE
                            next.step -= MUTATION_DISTANCE


if __name__ == '__main__':
    population = []
    for i in range(POPULATION_SIZE):
        ind = Individual()
        ind.read_file(FILE_NAME)
        ind.generate_random()
        ind.assess_fitness()
        population.append(ind)
    

    for epoch in range(EPOCHES_NUMBER):      
        new_population = []

        for i in range(len(population)):
            parent1 = tournament(population)
            parent2 = tournament(population)

            child = crossover(parent1, parent2)
            child.mutate()
            child.assess_fitness()
            new_population.append(child)

        population = new_population

    winner = min(population, key=lambda ind: ind.fitness)
    print ('WINNER: %d' % (winner.fitness))
    winner.draw_plot()



