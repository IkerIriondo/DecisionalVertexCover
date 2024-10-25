from draw_graphs import draw_graphs

from pysat.solvers import Glucose3 as solv

from timeit import default_timer as timer

from pysat.card import EncType, CardEnc

import copy
import numpy

import networkx as nx



def reduce_VC_to_SAT(graph, k):
    sat1 = []
    for i in range(0,len(graph)):
        for j in range(i,len(graph)):
           if graph[i][j] == 1:
               sat1.append([i+1,j+1])
    sat2 = list(CardEnc.atmost(lits = [i+1 for i in range(0,len(graph))], bound = k))
    sat = sat1 + sat2
    return sat


def answer_sat(graph, k, allsolutions): 
    sat = reduce_VC_to_SAT(graph, k)
    s = solv()
    for clause in sat:
        s.add_clause(clause)
    ema = s.solve()
    if ema:
        if not allsolutions:
            e = s.get_model()
            cover = [None for i in range(0,len(graph))]
            for i in range(0,len(graph)):
                 if e[i] < 0:
                    cover[i] = 0
                 else:
                    cover[i] = 1
            return [ema, cover]
        else:
            e = list(s.enum_models())[0:len(graph)]
            emaitzak = []
            for em in e:
               cover = [None for i in range(0,len(graph))]
               for i in range(0,len(graph)):
                   if em[i] < 0:
                      cover[i] = 0
                   else:
                      cover[i] = 1
               emaitzak.append(cover)
            return [ema,emaitzak]
    else:
        return [False]

def binary_search(graph, low, high, allsolutions):
    while True:
        k = (low + high)//2
        ema = answer_sat(graph, k, allsolutions)
        if ema[0]:
            ema1 = answer_sat(graph, k-1, allsolutions)
            if ema1[0]:
                high = k
            else:
                return [k,ema[1]]
        else:
            ema1 = answer_sat(graph, k+1, allsolutions)
            if ema1[0]:
                return [k+1, ema1[1]]
            else:
                low = k
   
     
def cover_2(graph):     
    cover = [None for i in range(0,len(graph))]
    while not isCoverRight(graph, len(graph), cover):
        for i in range(0,len(graph)):
            for j in range(0,len(graph[i])):
                if graph[i][j] == 1:
                    if cover[i] != 1 and cover[j] != 1:
                        cover[i] = 1
                        cover[j] = 1
    return cover.count(1)
     

def greedy(graph):  
    cover = [None for i in range(0,len(graph))]
    graph2 = []
    for i in range(0,len(graph)):
        graph2.append(graph[i].copy())
    while not isCoverRight(graph, len(graph), cover):
        bat = [sum(graph2[i]) for i in range(0,len(graph2))]
        ind = bat.index(max(bat))
        cover[ind] = 1
        for i in range(0,len(graph2)):
            graph2[ind][i] = 0
            graph2[i][ind] = 0
    return cover.count(1)
    

def isCoverRight(graph, length, cover):
    for i in range(0,length):
        for j in range(i,length):
            if graph[i][j] == 1:
               if cover[i] != 1 and cover[j] != 1: 
                   return False
    return True
      
                    
def areCoversRight(graph, length, covers):
    for cover in covers:
        ema = isCoverRight(graph, length, cover)
        if not ema: return False
    return True
    
    
def test(filename, allsolutions):
    
    import pickle
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        
    for graph in data:
    
        answer = binary_search(graph, 1, len(graph), allsolutions)
        if isCoverRight(graph, answer[0], answer[1][0:len(graph)]):
            print("\nMinimum Vertex Cover has: " + str(answer[0]) + " nodes")
            print("SAT-solver's all possible answers are: " + str(answer[1][0:len(graph)]))
            draw_graphs(graph, answer[1])
       
            # for x in answer[1]:
            #     #+ str(answer[1][0:len(graph)]))
            #     print(x)
        else:
            print("SOLUTION INCORRECT!")
                

def test_approximation(filename, allsolutions):
    
    import pickle
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        
    for graph in data:
        c1 = cover_2(graph)
        c2 = greedy(graph)
        
        i = max(c1, c2)//2
        j = min(c1, c2)        
            
        answer = binary_search(graph, i, j, allsolutions)
        
        if isCoverRight(graph, answer[0], answer[1][0:len(graph)]):
            print("\nMinimum Vertex Cover has: " + str(answer[0]) + " nodes")
            print("SAT-solver's answer is: " + str(answer[1][0:len(graph)]))
            draw_graphs(graph, answer[1])
       
            
        else:
            print("SOLUTION INCORRECT!")
   
             
def test_all_solutions(filename, allsolutions):
    
    import pickle
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        
    for graph in data:
    
        answer = binary_search(graph, 1, len(graph), allsolutions)
        
        if areCoversRight(graph, answer[0], answer[1]):#, answer[1][0:len(graph)]):
            print("\nMinimum Vertex Cover has: " + str(answer[0]) + " nodes\n" + "SAT-solver's answer is:\n" + str(answer[1][0:len(graph)]))
        else:
            print("SOLUTION INCORRECT!")
            
        draw_graphs(graph, answer)
              

if __name__ == "__main__":
    #Simple default cases, to check it works fine
    start = timer()
    test('mydata/data1.pkl', False)
    end = timer()
    print('Elapsed time: ' + str(end - start) + ' seconds')
    
    #More complex cases, to check efficiency
    start = timer()
    test('mydata/data2.pkl', False)
    end = timer()
    print('Elapsed time: ' + str(end - start) + ' seconds')
 
    #Cases to test APPROXIMATION algorithms
    start = timer()
    test_approximation('mydata/data2.pkl', False)
    end = timer()
    print('Elapsed time: ' + str(end - start) + ' seconds')
  
    #Find ALL possible solutions
    start = timer()
    test_all_solutions('mydata/data1.pkl', True)
    end = timer()
    print('Elapsed time: ' + str(end - start) + ' seconds')
