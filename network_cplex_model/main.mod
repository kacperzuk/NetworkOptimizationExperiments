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
  var f = new IloOplInputFile("data/paths.txt")
  var s;
 	while(!f.eof) {
 		s = f.readline();
 		var data = new IloOplDataSource("data/" + s + ".dat"); 	
 		opl.addDataSource(data);
 		opl.generate();
 		writeln("file " + s)
 		if(cplex_model.solve()){
 			var ofile = new IloOplOutputFile("results/" + s + ".txt") 
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
	f.close();
	opl.end();
	def.end();
	cplex_model.end();
	source.end();
 }