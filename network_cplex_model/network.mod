/*********************************************
 * OPL 12.7.1.0 Model
 * Author: admin
 * Creation Date: 26 gru 2017 at 23:37:03
 *********************************************/


{string} Nodes = ...;
 
 tuple Arc {
 	string src;
 	string dst;
 	int cap;
 	int cost;
 }
 
 tuple Demand {
   	string src;
 	string dst;
 	int volume;
 	int backup; 
 }
 
 {Arc} Arcs with src in Nodes, dst in Nodes = ...;
 
 {Demand} Demands with src in Nodes, dst in Nodes = ...;
 
 dvar boolean u[Arcs];
 dvar float+ y[Arcs];
 dvar boolean x[Arcs][Demands];
 
 minimize sum(e in Arcs) e.cost*u[e];
 
 subject to {
 	  
 	forall(d in Demands){
 		forall(v in Nodes){
 			if(d.src == v)
 				sum(e in Arcs : e.src == v) x[e][d] - sum(e in Arcs : e.dst == v) x[e][d] == 1;
 			if(d.dst == v)
 				sum(e in Arcs : e.src == v) x[e][d] - sum(e in Arcs : e.dst == v) x[e][d] == -1; 
 			if(d.src != v && d.dst != v)
 				sum(e in Arcs : e.src == v) x[e][d] - sum(e in Arcs : e.dst == v) x[e][d] == 0;  
 		} 	
 	}
 	
 	forall(e in Arcs) {
 		forall(x in Arcs) { 	
 			if(e.src == x.dst && x.src == e.dst) 
 				u[e] == u[x];
 		} 		
 	}
 	
 	forall(d in Demands) {
 		forall(t in Demands) { 
 			forall(e in Arcs) {
 				 if(d.dst == t.dst && d.src == t.src && t.backup == 1 && d.backup == 0){
 				 	x[e][d] + x[e][t] <= 1; 			
      			} 				 			 	
 			}
 		} 		
 	}
// 	
 	forall(e in Arcs) 
 		sum(d in Demands)x[e][d]*d.volume == y[e];
 	
 	forall(e in Arcs)
 	  y[e] <= e.cap*u[e];
 	 
 }
 
 execute {
  for (var e in Arcs) {
  	write("<"+ e.src +"," + e.dst +"> active:" + u[e] + "\n")  
  }
 }
 