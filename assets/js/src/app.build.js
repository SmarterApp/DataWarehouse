({
	appDir: ".",
	baseUrl: "modules",
	dir : "build",
	preserveLicenseComments: false,
	optimize: 'uglify',
	modules: [
	{
		//exclude jquery to avoid duplication
		name : "EDWARE.comparingPopulations"
	},
	
	{
		name : "EDWARE.comparingPopulationsReport"
	},
	{
		name : "EDWARE.individualStudent"
	},
	{
		name : "EDWARE.individualStudentReport"
	},
	{
		name : "EDWARE.studentList"
	},
	{
		name : "EDWARE.studentListReport"
	}]
})