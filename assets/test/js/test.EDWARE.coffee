#globals ok $ EDWARE test require module equals deepEqual
QUnit.config.autostart = false;

require ["cs!test.EDWARE.dataProxy", 
"cs!test.EDWARE.util", 
"cs!test.EDWARE.grid.tablegrid", 
"cs!test.EDWARE.studentList", 
"cs!test.EDWARE.individualStudent",
"cs!test.EDWARE.confidenceLevelBar",
"cs!test.EDWARE.populationBar",
"cs!test.EDWARE.comparingPopulation",
"cs!test.EDWARE.breadcrumb",
"cs!test.EDWARE.edwareFilter"
], ()->
  QUnit.start()

