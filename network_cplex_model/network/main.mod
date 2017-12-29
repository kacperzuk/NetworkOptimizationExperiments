/*********************************************
 * OPL 12.7.1.0 Model
 * Author: admin
 * Creation Date: 27 gru 2017 at 12:41:22
 *********************************************/

 main{
  var f = new IloOplInputFile("data/paths.txt")
  var s;
   		writeln("start");
 
 	while(!f.eof) {
 	 	var source = new IloOplModelSource("network.mod");
 	 	var cplex_model = new IloCplex();
 	 	var def = new IloOplModelDefinition(source);
  		var opl = new IloOplModel(def,cplex_model); 	
 	
 		s = f.readline();
 		var data = new IloOplDataSource("data/" + s + ".dat"); 	
 		writeln("file " + s);
 		opl.addDataSource(data);
 		opl.generate();
 		writeln("solving");
 		if(cplex_model.solve()){
 			var ofile = new IloOplOutputFile("results/" + s + ".txt") 
 			ofile.writeln("Cost:" + cplex_model.getObjValue());
 			ofile.writeln("Nodes:" + opl.Nodes);
 			ofile.writeln("Arcs:" + opl.Arcs);
 			ofile.writeln("Demands:" + opl.Demands);
 			ofile.writeln("xed:" + opl.x);
 			ofile.writeln("ye:" + opl.y);
 			ofile.writeln("ue:" + opl.u);
 			for(var e in opl.Arcs){
 				if(e.cost != 0 && opl.u[e] != 0)
 					ofile.writeln("Buy arc" + e);
 					 			
 			}
 			ofile.close();
 		 	writeln("Problem solved")
 		} else {
 		 	writeln("Cannot solve problem");
 		} 	
 		data.end();
 		opl.end();
		def.end();
		cplex_model.end();
		source.end();
	}
	f.close();
	   		writeln("stop");
 }