require({
	paths: {
		cs: '3p/cs',
		'coffee-script': '3p/coffee-script',
		jquery: '3p/jquery-1.7.2.min',
		jqGrid: '3p/jquery.jqGrid.min',
		bootstrap: '3p/bootstrap.min',
		text: '3p/text',
		mustache: '3p/mustache',
		templates: 'templates',
		edwareUtil: 'EDWARE.util',
		edwareDataProxy: 'EDWARE.dataProxy',
		edwareGrid: 'widgets/grid/EDWARE.grid.tablegrid',
		edwareGridFormatters: 'widgets/grid/EDWARE.grid.formatters',
		edwareStudentList: 'EDWARE.studentList',
		edwareDistrictList: 'EDWARE.districtList',
		edwareStateStudentList: 'EDWARE.stateStudentList',
		edwareIndividualStudent: 'EDWARE.individualStudent',
		edwareSchoolList: 'EDWARE.schoolList',
		edwareBreadcrumbs: 'widgets/breadcrumb/EDWARE.breadcrumbs',
		edwareConfidenceLevelBar: 'widgets/confidenceLevelBar/EDWARE.confidenceBar',
		edwarePopulationBar: 'widgets/populationBar/EDWARE.populationBar',
		
		// Templates
		edwareBreadcrumbsTemplate: 'widgets/breadcrumb/template.html',
		edwareConfidenceLevelBarTemplate: 'widgets/confidenceLevelBar/template.html',
		edwarePopulationBarTemplate: 'widgets/populationBar/template.html'
	},
	shim: {
        'jqGrid': {
            //These script dependencies should be loaded before loading
            //jqGrid
            deps: ['jquery'],
            exports: 'jqGrid'
        },
        'bootstrap': {
        	deps: ['jquery'],
            exports: 'bootstrap'
        }
   }
});