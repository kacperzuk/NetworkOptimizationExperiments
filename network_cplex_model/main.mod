/*********************************************
 * OPL 12.7.1.0 Model
 * Author: admin
 * Creation Date: 27 gru 2017 at 12:41:22
 *********************************************/

 main{
  var source = new IloOplModelSource("network.mod");
  var cplex_model = new IloCplex();
  var def = new IloOplModelDefinition(source);
  var opl = new IloOplModel(def,cplex_model);
  var x = 1;
 	while(x) {
 		var data = new IloOplDataSource("data/" + 1 + ".dat"); 	
 		opl.addDataSource(data);
 		opl.generate();
 		
 		if(cplex_model.solve()){
 			var ofile = new IloOplOutputFile("results/" + 1 + ".txt") 
 			ofile.writeln("Cost:" + cplex_model.getObjValue());
 			ofile.writeln("Nodes:" + opl.Nodes);
 			ofile.writeln("Arcs:" + opl.Arcs);
 			ofile.writeln("Demands:" + opl.Demands);
 			ofile.writeln("xed:" + opl.x);
 			ofile.writeln("ye:" + opl.y);
 			ofile.writeln("ue:" + opl.u);
 			ofile.close();
 		 	writeln("Problem solved")
 		} else {
 		 	writeln("Cannot solve problem");
 		}
 		
 		x -=1; 	
 		data.end();
	}
	opl.end();
	def.end();
	cplex_model.end();
	source.end();
 }